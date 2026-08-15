# core/ollama_brain.py
import requests
from .brain_interface import BrainInterface

class OllamaBrain(BrainInterface):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:3b", temperature: float = 0.3):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    def is_available(self) -> bool:
        try:
            # اختبار الاتصال بأي نقطة نهاية خفيفة
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.is_available():
            raise ConnectionError("Ollama service is not available.")

        # تحضير الرسائل بصيغة الدردشة
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            }
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120  # مهلة أطول لأن النموذج يحتاج وقتاً
        )
        response.raise_for_status()
        data = response.json()
        # إرجاع النص من أول choice
        return data["message"]["content"].strip()