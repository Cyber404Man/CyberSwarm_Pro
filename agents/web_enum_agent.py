# agents/web_enum_agent.py
from .base_agent import BaseAgent

class WebEnumAgent(BaseAgent):
    def __init__(self, brain, tool_manager, **callbacks):
        super().__init__(brain, tool_manager, "web_enum", **callbacks)

    def system_prompt(self) -> str:
        return (
            "أنت خبير في تعداد مسارات وملفات الويب. "
            "أعطني فقط أوامر gobuster أو ffuf أو dirb مع الخيارات المناسبة. "
            "لا تشرح."
        )

    def build_prompt(self, target: str) -> str:
        return (
            f"أعطني أمراً أو أمرين لاكتشاف المسارات والملفات المخفية على {target}. "
            "استخدم gobuster أو ffuf مع قائمة كلمات شائعة (مثل common.txt أو directory-list-2.3-medium.txt). "
            "مثال: gobuster dir -u http://TARGET -w /usr/share/wordlists/dirb/common.txt"
        )