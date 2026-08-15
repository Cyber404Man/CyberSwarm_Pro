# core/brain_interface.py
from abc import ABC, abstractmethod

class BrainInterface(ABC):
    """واجهة موحدة لأي نموذج لغوي."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        يرسل prompt للنموذج ويعيد الرد كنص.
        system_prompt: توجيه للنظام (دور النموذج).
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """يتحقق من أن الخدمة متاحة وجاهزة."""
        pass