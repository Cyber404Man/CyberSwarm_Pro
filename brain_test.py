# test_brain.py
import sys
import os

# أضف المجلد الحالي لمسار البحث حتى يتعرف على مجلد core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ollama_brain import OllamaBrain

brain = OllamaBrain(model="qwen2.5:3b")

print("جاري التحقق من اتصال Ollama...")
if brain.is_available():
    print("✅ Ollama متصل. جاري إرسال طلب تجريبي...")
    try:
        answer = brain.generate("اكتب لي جملة قصيرة عن الأمن السيبراني")
        print("📝 الرد:")
        print(answer)
    except Exception as e:
        print(f"❌ حصل خطأ أثناء التوليد: {e}")
else:
    print("❌ Ollama غير متصل. تأكد من تشغيله بأمر 'ollama serve' في طرفية أخرى.")