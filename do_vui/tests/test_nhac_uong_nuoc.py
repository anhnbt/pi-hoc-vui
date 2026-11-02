import datetime, os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from nhac_uong_nuoc import DemNgoi, dang_tranh

NGAY = datetime.datetime(2026, 11, 2)


def luc(gio, phut):
    return NGAY.replace(hour=gio, minute=phut)


def chay(dem, tu, so_phut, co_nguoi=True):
    """Nhìn phòng mỗi phút trong so_phut phút; trả về các giờ đã nhắc."""
    da_nhac = []
    for i in range(so_phut + 1):
        bay_gio = tu + datetime.timedelta(minutes=i)
        if dem.buoc(bay_gio, co_nguoi):
            da_nhac.append((bay_gio.hour, bay_gio.minute))
    return da_nhac


class TestNhacUongNuoc(unittest.TestCase):
    def test_ngoi_du_30_phut_thi_nhac_roi_dem_lai(self):
        self.assertEqual(chay(DemNgoi(), luc(15, 0), 65), [(15, 30), (16, 0)])

    def test_chua_du_30_phut_thi_khong_nhac(self):
        self.assertEqual(chay(DemNgoi(), luc(15, 0), 29), [])

    def test_vang_ngan_khong_dem_lai(self):
        dem = DemNgoi()
        chay(dem, luc(15, 0), 20)
        chay(dem, luc(15, 21), 3, co_nguoi=False)   # ra ngoài 4 phút
        self.assertEqual(chay(dem, luc(15, 25), 10), [(15, 30)])

    def test_vang_5_phut_thi_dem_lai(self):
        dem = DemNgoi()
        chay(dem, luc(15, 0), 20)
        chay(dem, luc(15, 21), 5, co_nguoi=False)   # phòng trống 15:21–15:26
        self.assertEqual(chay(dem, luc(15, 27), 31), [(15, 57)])

    def test_khong_nhac_trong_gio_nhac_nghi_gia_su(self):
        self.assertTrue(dang_tranh(luc(19, 15)))
        self.assertEqual(chay(DemNgoi(), luc(18, 45), 45), [(19, 25)])

    def test_khong_nhac_ngay_sau_cau_nhac_tam(self):
        self.assertTrue(dang_tranh(luc(18, 3)))
        self.assertFalse(dang_tranh(luc(18, 5)))


if __name__ == "__main__":
    unittest.main()
