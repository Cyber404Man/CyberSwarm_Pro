# tools/tool_manager.py
import subprocess
import shlex
import os
from typing import Optional

class ToolManager:
    """يشغل أدوات اختبار الاختراق الفعلية بشكل آمن."""
    
    ALLOWED_TOOLS = [
        "nmap", "gobuster", "ffuf", "nikto", "whois", "dig",
        "curl", "wget", "nslookup", "host", "whatweb", "wpscan"
    ]
    
    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = work_dir or os.getcwd()
    
    def run_command(self, command: str, timeout: int = 60) -> str:
        tool_name = shlex.split(command)[0] if command.strip() else ""
        if tool_name not in self.ALLOWED_TOOLS:
            return f"[ERROR] الأداة '{tool_name}' غير مسموح بها."
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, cwd=self.work_dir
            )
            output = result.stdout + "\n" + result.stderr
            if len(output.splitlines()) > 200:
                output = "\n".join(output.splitlines()[:200]) + "\n... (مقتطع)"
            return output.strip()
        except subprocess.TimeoutExpired:
            return f"[ERROR] انتهت المهلة ({timeout}s)."
        except Exception as e:
            return f"[ERROR] {e}"