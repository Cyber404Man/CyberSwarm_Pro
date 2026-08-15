# test_orchestrator.py
"""
اختبار المنسق مع أدوات حقيقية ووكلاء متخصصين.
يُجري فحصاً عميقاً على 127.0.0.1 لاختبار سير العمل.
"""

import sys
import os

# إضافة مجلد المشروع إلى sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ollama_brain import OllamaBrain
from core.orchestrator import Orchestrator
from tools.tool_manager import ToolManager

def main():
    # 1. إنشاء الدماغ المحلي
    brain = OllamaBrain()
    if not brain.is_available():
        print("❌ Ollama غير متصل. شغّله بأمر 'ollama serve' أولاً.")
        return

    # 2. إنشاء مدير الأدوات الحقيقي
    tm = ToolManager()

    # 3. دوال مراقبة بسيطة
    def on_phase(phase, prog):
        print(f"\n>>> مرحلة {phase} ({prog:.0f}%)")

    def on_think(msg):
        print(f"[تفكير] {msg}")

    def on_exec(cmd):
        print(f"[تنفيذ] {cmd}")

    def on_res(out):
        # اقتطاع المخرجات الطويلة
        short = out[:200] + "..." if len(out) > 200 else out
        print(f"[نتيجة] {short}")

    def on_finding(f):
        print(f"[ثغرة] {f.get('title')} ({f.get('severity')})")

    # 4. إنشاء المنسق
    orch = Orchestrator(
        brain=brain,
        tool_manager=tm,
        on_phase_change=on_phase,
        on_think=on_think,
        on_execute=on_exec,
        on_result=on_res,
        on_finding=on_finding,
    )

    # 5. تشغيل فحص على المضيف المحلي بنمط عميق (deep) لاختبار جميع المراحل
    target = "127.0.0.1:8080"
    mode = "deep"   # يمكنك تغييره إلى "quick" لو أردت فحصاً سريعاً
    print(f"بدء فحص {target} بنمط {mode}...\n")
    result = orch.run(target=target, mode=mode)

    # 6. عرض النتائج النهائية
    print("\n" + "=" * 50)
    print(f"اكتمل الفحص. تم اكتشاف {len(result.all_findings)} ثغرة.")
    if result.all_findings:
        print("\nالثغرات:")
        for f in result.all_findings:
            print(f" - [{f.get('severity')}] {f.get('title')}")

if __name__ == "__main__":
    main()
