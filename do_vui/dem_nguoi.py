"""Đếm số người trong khung hình camera bằng YOLO11n (ONNX), chạy ngay trên Pi.

Chỉ đếm "có bao nhiêu người", không nhận ra ai là ai; ảnh chụp chỉ nằm trong bộ nhớ, không lưu lại.
Cần mô hình ~/hoc/mo_hinh/yolo11n.onnx và chạy bằng vieneu-venv (đã có onnxruntime + numpy).

Chạy thử:  ../vieneu-venv/bin/python dem_nguoi.py
"""
import os, subprocess

import numpy as np
import onnxruntime

from loa_camera import CAM_IP, doc_mat_khau
from urllib.parse import quote

MO_HINH = os.path.expanduser("~/hoc/mo_hinh/yolo11n.onnx")
RONG, CAO = 640, 480  # luồng phụ của camera; cả hai chia hết cho 32 nên đưa thẳng vào YOLO, không cần co ảnh
CHAC_CHAN = 0.4       # độ tin cậy tối thiểu để tính là một người

_phien = None


def chup():
    rtsp = f"rtsp://admin:{quote(doc_mat_khau(), safe='')}@{CAM_IP}:554/cam/realmonitor?channel=1&subtype=1"
    anh = subprocess.run(
        ["ffmpeg", "-v", "error", "-rtsp_transport", "tcp", "-i", rtsp, "-frames:v", "1",
         "-s", f"{RONG}x{CAO}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
        capture_output=True, timeout=20, check=True).stdout
    return np.frombuffer(anh, np.uint8).reshape(CAO, RONG, 3)


def dem(anh):
    global _phien
    if _phien is None:
        _phien = onnxruntime.InferenceSession(MO_HINH)
    dau_vao = anh.transpose(2, 0, 1)[None].astype(np.float32) / 255
    ra = _phien.run(None, {"images": dau_vao})[0][0]  # (84, số ô): 4 toạ độ + 80 loại vật, loại 0 là người
    diem = ra[4]
    hop = ra[:4, diem > CHAC_CHAN].T  # cx, cy, w, h
    diem = diem[diem > CHAC_CHAN]
    # Một người có thể được nhiều ô cùng bắt: giữ ô điểm cao nhất, bỏ các ô chồng lên nó quá nửa
    con_lai, so_nguoi = np.argsort(-diem), 0
    while len(con_lai):
        so_nguoi += 1
        a, khac = hop[con_lai[0]], hop[con_lai[1:]]
        x1 = np.maximum(a[0] - a[2] / 2, khac[:, 0] - khac[:, 2] / 2)
        x2 = np.minimum(a[0] + a[2] / 2, khac[:, 0] + khac[:, 2] / 2)
        y1 = np.maximum(a[1] - a[3] / 2, khac[:, 1] - khac[:, 3] / 2)
        y2 = np.minimum(a[1] + a[3] / 2, khac[:, 1] + khac[:, 3] / 2)
        giao = np.clip(x2 - x1, 0, None) * np.clip(y2 - y1, 0, None)
        hop_nhat = a[2] * a[3] + khac[:, 2] * khac[:, 3] - giao
        con_lai = con_lai[1:][giao / hop_nhat < 0.5]
    return so_nguoi


if __name__ == "__main__":
    import time
    t = time.time()
    anh = chup()
    t2 = time.time()
    print("so nguoi:", dem(anh), f"| chup {t2 - t:.1f}s, dem {time.time() - t2:.1f}s")
    t3 = time.time()
    print("so nguoi:", dem(anh), f"| lan dem thu hai {time.time() - t3:.1f}s")
