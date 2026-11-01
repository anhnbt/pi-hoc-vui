"""Giọng đọc tạo sẵn cho màn hình chờ (lịch việc sáng và tối), bằng giọng VieNeu.
Máy chủ tìm file bằng ten_file(câu) trong web/am_thanh/. Câu nào đã có file thì bỏ qua.

Chạy: ../vieneu-venv/bin/python tao_man_cho.py
"""
import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")

from tao_cau_hoi import AM_THANH, ten_file
from lich import VIEC_SANG, NHAC_LAI_NUOC, VIEC_TOI


def gom_cau_doc():
    """Mọi câu cần đọc, theo thứ tự lịch, bỏ câu trùng."""
    cau = [v[-1] for v in VIEC_SANG]
    cau.append(NHAC_LAI_NUOC[-1])
    cau += [v[-1] for v in VIEC_TOI]
    return list(dict.fromkeys(cau))


def main():
    tat_ca = gom_cau_doc()
    thieu = [c for c in tat_ca if not os.path.exists(os.path.join(AM_THANH, ten_file(c)))]
    print(f"{len(tat_ca)} câu, cần tạo giọng {len(thieu)} câu", flush=True)
    if thieu:
        from vieneu import Vieneu
        tts = Vieneu()
        for i, cau in enumerate(thieu, 1):
            tts.save(tts.infer(cau), os.path.join(AM_THANH, ten_file(cau)))
            print(f"[{i}/{len(thieu)}] {cau}", flush=True)
    print("Xong!", flush=True)


if __name__ == "__main__":
    main()
