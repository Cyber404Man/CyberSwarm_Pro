# agents/recon_agent.py
from .base_agent import BaseAgent

class ReconAgent(BaseAgent):
    def __init__(self, brain, tool_manager, **callbacks):
        super().__init__(brain, tool_manager, "recon", **callbacks)
    
    def system_prompt(self) -> str:
          return (
             "أنت خبير في جمع المعلومات. أعد الأوامر فقط. "
             "كل أمر في سطر يبدأ بـ 'أمر:' . لا تشرح."
    )
    
    def build_prompt(self, target: str) -> str:
        return f"أعطني أوامر لجمع المعلومات عن {target}. استخدم whois, dig, nslookup, host."
