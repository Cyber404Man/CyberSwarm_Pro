# agents/base_agent.py
"""
الوكيل الأساسي (BaseAgent) - يُستخدم كأب لجميع الوكلاء المتخصصين.
يحتوي على الوظائف المشتركة بين الوكلاء: استخراج الأوامر، تحليل المخرجات،
وتنفيذ المرحلة.
"""

from typing import List, Dict, Any, Callable, Optional
from core.brain_interface import BrainInterface
from tools.tool_manager import ToolManager


class BaseAgent:
    """كل أساسي لأي وكيل متخصص."""

    def __init__(
        self,
        brain: BrainInterface,
        tool_manager: ToolManager,
        phase_name: str,
        on_think: Optional[Callable] = None,
        on_execute: Optional[Callable] = None,
        on_result: Optional[Callable] = None,
        on_finding: Optional[Callable] = None,
    ):
        self.brain = brain
        self.tool_manager = tool_manager
        self.phase_name = phase_name
        self.on_think = on_think or (lambda msg: None)
        self.on_execute = on_execute or (lambda cmd: None)
        self.on_result = on_result or (lambda out: None)
        self.on_finding = on_finding or (lambda f: None)

    # ── رسالة النظام (تُوجّه النموذج) ──
    def system_prompt(self) -> str:
        return (
            "أنت خبير أمن سيبراني. "
            "أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' . "
            "لا تشرح ولا تضف أي نص آخر."
        )

    # ── مطالعة المرحلة (تُخصَّص في الوكيل الفرعي) ──
    def build_prompt(self, target: str) -> str:
        prompts = {
            "recon": f"أعطني أوامر لجمع المعلومات عن {target} (whois, dig, nslookup, host). أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
            "port_scan": f"أعطني أوامر nmap لفحص المنافذ على {target}. استخدم nmap -sV --top-ports 100. أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
            "web_enum": f"أعطني أوامر لاكتشاف المسارات على {target} (gobuster, ffuf). أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
            "vuln_scan": f"أعطني أوامر لفحص الثغرات على {target} (nikto, nuclei). أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
            "exploit": f"أعطني أوامر لاستغلال ثغرات على {target} (sqlmap). أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
            "report": "اكتب ملخصاً بالثغرات. أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
        }
        return prompts.get(
            self.phase_name,
            f"أعطني الأوامر اللازمة لمرحلة {self.phase_name} على {target}. أعد الأوامر فقط، كل أمر في سطر يبدأ بـ 'أمر:' .",
        )

    # ── استخراج الأوامر من رد النموذج ──
    def extract_commands(self, text: str) -> List[str]:
        allowed = getattr(self.tool_manager, "ALLOWED_TOOLS", [])
        commands = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
             continue
        # ابحث عن أي أداة مسموحة موجودة في السطر
            for tool in allowed:
             if tool in line:
                idx = line.find(tool)
                cmd = line[idx:].strip().rstrip(".,;!؟")
                # الكلمة الأولى بعد الاستخراج يجب أن تكون الأداة
                first_word = cmd.split()[0] if cmd else ""
                if first_word in allowed:
                    commands.append(cmd)
                break   # نأخذ أول تطابق فقط
        if not commands:
          return ["whois 127.0.0.1"]
        return commands

    # ── تحليل المخرجات واكتشاف الثغرات ──
    def analyze_output(self, command: str, output: str) -> List[Dict[str, Any]]:
        if not output or len(output.strip()) < 10:
            return []
        prompt = (
            f"أنت خبير أمن سيبراني. حلل مخرجات الأمر التالي:\n"
            f"الأمر: {command}\n"
            f"المخرجات:\n{output}\n\n"
            "هل تكشف هذه المخرجات عن ثغرات أمنية (مثل منافذ مفتوحة، إصدارات قديمة، مسارات حساسة، تكوينات خاطئة)؟ "
            "أجب بصيغة JSON فقط:\n"
            '[{"title":"...", "description":"...", "severity":"Critical/High/Medium/Low/Info", "remediation":"..."}]\n'
            "إذا لم توجد ثغرات أجب: []"
        )
        try:
            answer = self.brain.generate(prompt)
            import json
            import re

            json_match = re.search(r"\[.*\]", answer, re.DOTALL)
            if json_match:
                findings = json.loads(json_match.group())
                if isinstance(findings, list):
                    return findings
        except Exception:
            pass
        return []

    # ── تشغيل المرحلة ──
    def run(self, target: str) -> List[Dict[str, Any]]:
        self.on_think(f"بدء مرحلة {self.phase_name}")
        prompt = self.build_prompt(target)
        commands_text = self.brain.generate(
            prompt, system_prompt=self.system_prompt()
        )
        commands = self.extract_commands(commands_text)
        self.on_think(f"الأوامر المستخرجة: {commands}")

        findings = []
        for cmd in commands:
            if not cmd.strip() or cmd.startswith("echo"):
                continue  # تجاهل أوامر echo
            self.on_execute(cmd)
            output = self.tool_manager.run_command(cmd, timeout=120)
            self.on_result(output)
            found = self.analyze_output(cmd, output)
            for f in found:
                self.on_finding(f)
                findings.append(f)
        return findings