"""Các câu nhắn hay dùng, đọc sẵn bằng giọng VieNeu (hay hơn Piper). Bấm câu nào trên trang /loi-nhan
thì phát đúng file đã đọc sẵn; câu gõ tay thì may_chu.py đọc ngay bằng Piper.

Chạy: ../vieneu-venv/bin/python tao_loi_nhan.py
"""
import json, os

os.environ.setdefault("HF_HUB_OFFLINE", "1")

from tao_cau_hoi import AM_THANH, WEB, ten_file

CAU_SAN = [
    "Con ơi, xuống ăn cơm nhé!",
    "Con đi tắm nhé!",
    "Đến giờ đi ngủ rồi con ơi!",
    "Con tắt tivi, cho mắt nghỉ một chút nhé!",
    "Con uống nước đi nhé!",
    "Con dọn đồ chơi gọn gàng nhé!",
    "Bố mẹ sắp về rồi, con ngoan nhé!",
    "Bố mẹ yêu con nhiều lắm!",
]


def main():
    thieu = [c for c in CAU_SAN if not os.path.exists(os.path.join(AM_THANH, ten_file(c)))]
    print(f"{len(CAU_SAN)} câu, cần tạo giọng {len(thieu)} câu", flush=True)
    if thieu:
        from vieneu import Vieneu
        tts = Vieneu()
        for i, cau in enumerate(thieu, 1):
            tts.save(tts.infer(cau), os.path.join(AM_THANH, ten_file(cau)))
            print(f"[{i}/{len(thieu)}] {cau}", flush=True)
    with open(os.path.join(WEB, "loi_nhan.js"), "w", encoding="utf-8") as f:
        f.write("window.CAU_SAN = " + json.dumps(CAU_SAN, ensure_ascii=False, indent=1) + ";\n")
    print("Xong!", flush=True)


if __name__ == "__main__":
    main()
