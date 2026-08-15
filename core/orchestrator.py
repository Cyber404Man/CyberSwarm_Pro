# core/orchestrator.py
"""
المنسق الرئيسي (Orchestrator) - العقل المدبر لسرب الوكلاء.
يدير مراحل الفحص، يتواصل مع النموذج اللغوي، وينفذ الأوامر عبر ToolManager.
مستقل تماماً عن Streamlit.
"""

from typing import Callable, List, Dict, Any, Optional
from .brain_interface import BrainInterface
from .scan_result import ScanResult
from tools.tool_manager import ToolManager
from agents.base_agent import BaseAgent
from agents.portscan_agent import PortScanAgent
from agents.recon_agent import ReconAgent
from agents.web_enum_agent import WebEnumAgent
from agents.vuln_agent import VulnScanAgent
# سنضيف وكلاء آخرين هنا لاحقاً

class Orchestrator:
    def __init__(
        self,
        brain: BrainInterface,
        tool_manager: Optional[ToolManager] = None,
        on_phase_change: Optional[Callable[[str, float], None]] = None,
        on_think: Optional[Callable[[str], None]] = None,
        on_execute: Optional[Callable[[str], None]] = None,
        on_result: Optional[Callable[[str], None]] = None,
        on_finding: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        :param brain: أي كائن ينفذ واجهة BrainInterface (مثل OllamaBrain).
        :param tool_manager: مدير تشغيل أدوات الاختراق. إن لم يُعطَ، ينشأ ToolManager افتراضي.
        :param on_phase_change: callback(phase: str, progress: float) عند تغير المرحلة.
        :param on_think: callback(message: str) عندما "يفكر" النموذج.
        :param on_execute: callback(command: str) عند تنفيذ أمر.
        :param on_result: callback(output: str) عند استلام مخرجات أمر.
        :param on_finding: callback(finding: dict) عند اكتشاف ثغرة.
        """
        self.brain = brain
        self.tool_manager = tool_manager or ToolManager()

        # دوال الكول باك (تحديث الواجهة لاحقاً)
        self.on_phase_change = on_phase_change or (lambda p, prog: None)
        self.on_think = on_think or (lambda msg: None)
        self.on_execute = on_execute or (lambda cmd: None)
        self.on_result = on_result or (lambda out: None)
        self.on_finding = on_finding or (lambda finding: None)

    # ── مراحل الفحص ──
    def _get_phases(self, mode: str) -> List[str]:
        if mode == "quick":
            return ["recon", "port_scan", "web_enum"]
        elif mode == "deep":
            return ["recon", "port_scan", "web_enum", "vuln_scan", "exploit", "report"]
        elif mode =="savage": 
            return ["recon", "port_scan_full", "web_enum_aggressive", "vuln_scan_nuclei", "sql_injection_test", "report"] 
        else:
            return ["recon", "scan", "report"]

    # ─ـ إنشاء الوكيل المناسب للمرحلة ─ـ
    def _create_agent(self, phase: str) -> BaseAgent:
        """ينشئ الوكيل المناسب للمرحلة مع إعدادات الكولباكس الصحيحة."""
        callbacks = {
            "on_think": self.on_think,
            "on_execute": self.on_execute,
            "on_result": self.on_result,
            "on_finding": self.on_finding,
        }
        if phase == "recon":
            return ReconAgent(self.brain, self.tool_manager, **callbacks)
        elif phase == "port_scan":
            return PortScanAgent(self.brain, self.tool_manager, **callbacks)
    #  أضف وكلاء مستقبليين هنا (web_enum, vuln_scan, exploit, report)
        elif phase == "web_enum":
            return WebEnumAgent(self.brain, self.tool_manager, **callbacks)
        elif phase == "vuln_scan":
            return VulnScanAgent(self.brain, self.tool_manager, **callbacks)
        else:
        # استخدام الوكيل العام مع prompting افتراضي
             return BaseAgent(self.brain, self.tool_manager, phase, **callbacks)
 
    # ─ـ الدالة الرئيسية: run ─ـ
    def run(self, target: str, mode: str) -> ScanResult:
        phases = self._get_phases(mode)
        result = ScanResult(target=target, mode=mode)

        for idx, phase in enumerate(phases):
            progress = (idx / len(phases)) * 100
            self.on_phase_change(phase, progress)

            agent = self._create_agent(phase)
            findings = agent.run(target)
            result.all_findings.extend(findings)
            result.phases_completed.append(phase)

        # إنشاء تقرير مبسط
        result.report = {
            "executive_summary": f"فحص {target} ({mode}) اكتمل. اكتُشفت {len(result.all_findings)} ثغرة.",
            "findings": result.all_findings,
        }
        self.on_phase_change("completed", 100.0)
        return result