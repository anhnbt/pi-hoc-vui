"""Tiến trình đọc nhanh bằng Piper cho lời nhắn gõ tay: nạp giọng một lần (khoảng 10 giây), sau đó mỗi câu dưới 1 giây.

may_chu.py chạy file này bằng ~/hoc/venv (có piper-tts) và nói chuyện qua stdin/stdout:
mỗi dòng vào là JSON {"chu": ..., "tep": ...}, đọc xong ghi file wav rồi trả lại một dòng "xong".
"""
import json, os, sys, wave

from piper import PiperVoice

giong = PiperVoice.load(os.path.expanduser("~/hoc/vi_VN-vais1000-medium.onnx"))
print("san_sang", flush=True)
for dong in sys.stdin:
    yeu_cau = json.loads(dong)
    with wave.open(yeu_cau["tep"], "wb") as w:
        giong.synthesize_wav(yeu_cau["chu"], w)
    print("xong", flush=True)
