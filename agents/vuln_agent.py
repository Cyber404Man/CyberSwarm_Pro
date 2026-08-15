# agents/vuln_agent.py
from .base_agent import BaseAgent

class VulnScanAgent(BaseAgent):
    def __init__(self, brain, tool_manager, **callbacks):
        super().__init__(brain, tool_manager, "vuln_scan", **callbacks)

    def system_prompt(self) -> str:
        return (
            "أنت خبير في فحص الثغرات المعروفة. "
            "أعطني أوامر nikto أو nuclei مع الخيارات المناسبة. لا تشرح."
        )

    def build_prompt(self, target: str) -> str:
        return (
            f"أعطني أوامر لفحص الثغرات المعروفة على {target}. "
            "استخدم nikto أو nuclei. مثال: nikto -h http://TARGET"
        )