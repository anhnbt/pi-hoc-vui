"""Nhắc nghỉ giữa buổi học gia sư (18:30–20:00), qua loa camera ở phòng học.

Không cần biết cô dạy thứ mấy: cron chạy file này 18:30 mỗi ngày. Trong 20 phút đầu, cứ 20 giây đếm số người
trong phòng một lần; quá nửa số lần thấy từ 2 người trở lên thì tính là hôm nay có buổi học.
Có buổi học thì 19:15 nhắc nghỉ 5 phút, 19:20 nhắc học tiếp. Mỗi ngày ghi một dòng vào log.txt.

Chạy thử ngay (đếm 1 phút, chỉ cần thấy 1 người, nhắc liền):  ../vieneu-venv/bin/python nhac_nghi.py --thu
"""
import datetime, json, os, subprocess, sys, time

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import dem_nguoi, loa_camera
from tao_cau_hoi import AM_THANH, ten_file

THEO_DOI_DEN = (18, 50)   # theo dõi phòng từ lúc chạy đến giờ này
GIO_NGHI = (19, 15)
GIO_HOC_TIEP = (19, 20)
NHAC_NGHI = ("Cô ơi, con học được bốn mươi lăm phút rồi ạ. "
             "Cô cho con nghỉ năm phút, uống nước và vận động một chút nhé!")
HOC_TIEP = "Hết giờ nghỉ rồi! Con ngồi vào bàn, mình học tiếp nhé."


def tao_giong():
    """Câu nào chưa có giọng đọc thì tạo bằng VieNeu (lần đầu mất khoảng 1 phút)."""
    thieu = [c for c in (NHAC_NGHI, HOC_TIEP) if not os.path.exists(os.path.join(AM_THANH, ten_file(c)))]
    if thieu:
        from vieneu import Vieneu
        tts = Vieneu()
        for cau in thieu:
            tts.save(tts.infer(cau), os.path.join(AM_THANH, ten_file(cau)))


def noi(cau):
    tep = os.path.join(AM_THANH, ten_file(cau))
    try:
        loa_camera.phat(tep)
    except Exception as loi:  # loa camera không được thì đọc bằng loa Pi
        print("Loa camera lỗi:", loi, flush=True)
        subprocess.run(["aplay", "-q", tep])


def doi_den(gio_phut):
    dich = datetime.datetime.now().replace(hour=gio_phut[0], minute=gio_phut[1], second=0)
    time.sleep(max(0, (dich - datetime.datetime.now()).total_seconds()))


def ghi(dong):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {dong}", flush=True)


def ghi_gia_su(co):
    """Màn hình chờ trên TV đọc file này để biết tối nay có buổi gia sư không."""
    tep = os.path.expanduser("~/hoc/gia_su.json")
    with open(tep, "w", encoding="utf-8") as f:
        json.dump({"ngay": datetime.date.today().isoformat(), "co": co}, f)


def main():
    thu = "--thu" in sys.argv
    tao_giong()
    it_nhat = 1 if thu else 2
    het_gio = time.time() + 60 if thu else datetime.datetime.now().replace(
        hour=THEO_DOI_DEN[0], minute=THEO_DOI_DEN[1], second=0).timestamp()

    so_lan = so_lan_co_hoc = 0
    while time.time() < het_gio:
        try:
            n = dem_nguoi.dem(dem_nguoi.chup())
            so_lan += 1
            so_lan_co_hoc += n >= it_nhat
        except Exception as loi:
            print("Không chụp được camera:", loi, flush=True)
        time.sleep(20)

    if so_lan == 0 or so_lan_co_hoc * 2 <= so_lan:
        ghi_gia_su(False)
        return ghi(f"Không có buổi học gia sư ({so_lan_co_hoc}/{so_lan} lần thấy từ {it_nhat} người)")
    ghi_gia_su(True)
    ghi(f"Có buổi học gia sư ({so_lan_co_hoc}/{so_lan} lần thấy từ {it_nhat} người)")
    if not thu:
        doi_den(GIO_NGHI)
    noi(NHAC_NGHI)
    ghi("Đã nhắc nghỉ giữa giờ")
    if not thu:
        doi_den(GIO_HOC_TIEP)
    noi(HOC_TIEP)
    ghi("Đã nhắc học tiếp")


if __name__ == "__main__":
    main()
