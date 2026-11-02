"""Nhắc uống nước khi có người ngồi lâu trong phòng học (14:00–21:30), qua loa camera.

Camera không biết ai là con, ai là bố, nên cứ trong phòng có người liền 30 phút là nhắc tên con
(bố ngồi cùng bàn cũng nghe). Phòng trống từ 5 phút trở lên thì tính là đã đứng dậy, đếm lại từ đầu.
Không nhắc chồng lên giờ nhắc nghỉ khi học với cô, hay ngay sau câu nhắc việc buổi tối của màn hình chờ.
Ảnh chỉ nằm trong bộ nhớ để đếm người, không lưu lại. Mỗi lần nhắc ghi một dòng vào log.txt.

Chạy thử (2 phút là nhắc, không phát tiếng, chạy 10 phút):  ../vieneu-venv/bin/python nhac_uong_nuoc.py --thu
"""
import datetime, os, subprocess, sys, time

os.environ.setdefault("HF_HUB_OFFLINE", "1")

from lich import VIEC_TOI
from tao_cau_hoi import AM_THANH, ten_file

BAT_DAU, HET = (14, 0), (21, 30)
NGOI_LAU = datetime.timedelta(minutes=30)
DUNG_DAY = datetime.timedelta(minutes=5)    # phòng trống chừng này thì đếm lại từ đầu
NHAC_UONG = "Tùng Lâm ơi, ngồi lâu rồi, uống một ngụm nước đi nào!"
KHONG_NHAC = [((19, 10), (19, 25))]          # quanh giờ nhắc nghỉ khi học với cô (nhac_nghi.py)
KHONG_NHAC += [((v[0], v[1]), (v[0], v[1] + 5)) for v in VIEC_TOI]  # 5 phút sau câu nhắc tắm, dọn đồ chơi


def dang_tranh(bay_gio):
    hm = (bay_gio.hour, bay_gio.minute)
    return any(tu <= hm < den for tu, den in KHONG_NHAC)


class DemNgoi:
    """Theo dõi từ lúc phòng có người, để biết khi nào đã ngồi đủ lâu."""

    def __init__(self, ngoi_lau=NGOI_LAU, dung_day=DUNG_DAY):
        self.ngoi_lau, self.dung_day = ngoi_lau, dung_day
        self.ngoi_tu = self.vang_tu = None

    def buoc(self, bay_gio, co_nguoi):
        """Ghi nhận một lần nhìn phòng; trả về True nếu đến lúc nhắc uống nước."""
        if co_nguoi:
            self.vang_tu = None
            if self.ngoi_tu is None:
                self.ngoi_tu = bay_gio
        else:
            if self.vang_tu is None:
                self.vang_tu = bay_gio
            if bay_gio - self.vang_tu >= self.dung_day:
                self.ngoi_tu = None
            return False
        if bay_gio - self.ngoi_tu >= self.ngoi_lau and not dang_tranh(bay_gio):
            self.ngoi_tu = bay_gio  # nhắc xong thì đếm lại, ngồi tiếp 30 phút nữa thì nhắc lần sau
            return True
        return False


def ghi(dong):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {dong}", flush=True)


def main():
    import dem_nguoi, loa_camera

    thu = "--thu" in sys.argv
    tep = os.path.join(AM_THANH, ten_file(NHAC_UONG))
    if not os.path.exists(tep) and not thu:
        from vieneu import Vieneu  # lần đầu tạo giọng mất khoảng 1 phút
        tts = Vieneu()
        tts.save(tts.infer(NHAC_UONG), tep)

    if thu:
        dem = DemNgoi(datetime.timedelta(minutes=2), datetime.timedelta(minutes=1))
        het = datetime.datetime.now() + datetime.timedelta(minutes=10)
    else:
        dem = DemNgoi()
        het = datetime.datetime.now().replace(hour=HET[0], minute=HET[1], second=0)

    while datetime.datetime.now() < het:
        try:
            n = dem_nguoi.dem(dem_nguoi.chup())
        except Exception as loi:  # camera mất mạng: bỏ qua lần này, không tính là phòng trống
            print("Không chụp được camera:", loi, flush=True)
            n = None
        bay_gio = datetime.datetime.now()
        if thu:
            ghi(f"(thử) thấy {n} người")
        if n is not None and dem.buoc(bay_gio, n > 0):
            if thu:
                ghi("(thử) đến lúc nhắc uống nước, không phát tiếng")
                continue
            try:
                loa_camera.phat(tep)
            except Exception as loi:  # loa camera không được thì đọc bằng loa Pi
                print("Loa camera lỗi:", loi, flush=True)
                subprocess.run(["aplay", "-q", tep], timeout=30)
            ghi(f"Nhắc uống nước (đã có người {NGOI_LAU.seconds // 60} phút)")
        time.sleep(30 if thu else 60)


if __name__ == "__main__":
    main()
