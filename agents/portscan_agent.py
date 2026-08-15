from .base_agent import BaseAgent

class PortScanAgent(BaseAgent):
    def __init__(self, brain, tool_manager, **callbacks):
        super().__init__(brain, tool_manager, "port_scan", **callbacks)
    
    def system_prompt(self) -> str:
        return "أنت خبير في فحص المنافذ. أعد فقط أوامر nmap مع الخيارات المناسبة."
    
    def build_prompt(self, target: str) -> str:
        return f"أنت تفحص المنافذ على {target}. اقترح أوامر nmap التي تراها مثالية، مع خياراتك المفضلة. ضع كل أمر في سطر منفصل، ويمكنك إضافة تعليقات مختصرة."