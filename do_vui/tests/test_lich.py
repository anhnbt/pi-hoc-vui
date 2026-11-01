import os, sys, tempfile, unittest
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lich

T2 = (2026, 11, 2)   # thứ Hai
T7 = (2026, 11, 7)   # thứ Bảy


def tt(gio, phut, giay=0, ngay=T2, nghi_hoc=False, co_gia_su=None):
    return lich.trang_thai(datetime(*ngay, gio, phut, giay), nghi_hoc, co_gia_su)


class TestLich(unittest.TestCase):
    def test_sang_uong_nuoc(self):
        t = tt(6, 52)
        self.assertEqual(t["che_do"], "viec")
        self.assertEqual(t["chu"], "Uống nước nào!")
        self.assertEqual(t["buoc"], 4)
        self.assertEqual(t["tong"], 8)
        self.assertEqual(t["con_phut"], 23)
        self.assertEqual(t["mau"], "#D5E8E6")
        self.assertIs(t["khoa_do_vui"], False)
        self.assertEqual(t["gio"], "6:52")

    def test_sang_khoa_tu_705(self):
        t = tt(7, 5)
        self.assertIs(t["khoa_do_vui"], True)
        self.assertEqual(t["mau"], "#FFF3E3")
        self.assertEqual(tt(7, 12)["mau"], "#FF7171")

    def test_715_het_buoi_sang(self):
        self.assertEqual(tt(7, 15, 0)["che_do"], "do_vui")

    def test_thu_bay_khong_nhac(self):
        self.assertEqual(tt(6, 40, ngay=T7)["che_do"], "do_vui")
        self.assertIsNone(lich.cau_dung_phut(datetime(*T7, 6, 35), False))

    def test_nghi_hoc(self):
        self.assertEqual(tt(6, 40, nghi_hoc=True)["che_do"], "do_vui")
        self.assertIsNone(lich.cau_dung_phut(datetime(*T2, 6, 35), True))

    def test_toi_tam(self):
        t = tt(18, 10)
        self.assertEqual(t["che_do"], "viec")
        self.assertEqual(t["chu"], "Đi tắm thôi!")
        self.assertEqual(t["con_phut"], 10)
        self.assertIsNone(t["buoc"])
        self.assertIsNone(t["tong"])

    def test_toi_gia_su(self):
        self.assertEqual(tt(18, 40, co_gia_su=True)["che_do"], "hoc")
        t = tt(18, 40, co_gia_su=None)
        self.assertEqual(t["che_do"], "ranh")
        self.assertEqual(t["tiep_theo"], "20:00 Dọn đồ chơi")
        self.assertEqual(tt(19, 17, co_gia_su=True)["chu"], "Nghỉ 5 phút")

    def test_dem(self):
        self.assertEqual(tt(22, 0)["che_do"], "ngu_ngon")
        t = tt(22, 5)
        self.assertEqual(t["che_do"], "den")
        self.assertEqual(t["mau"], "#000000")
        self.assertEqual(tt(5, 0)["che_do"], "den")

    def test_cau_dung_phut(self):
        nuoc = "Tùng Lâm ơi, uống một cốc nước đầy nhé!"
        self.assertEqual(lich.cau_dung_phut(datetime(*T2, 6, 52, 30), False), nuoc)
        self.assertEqual(lich.cau_dung_phut(datetime(*T2, 6, 54), False), lich.NHAC_LAI_NUOC[2])
        self.assertIsNone(lich.cau_dung_phut(datetime(*T2, 6, 53), False))
        self.assertEqual(lich.cau_dung_phut(datetime(*T7, 20, 0), False),
                         "Tùng Lâm ơi, mình dọn đồ chơi gọn gàng nhé!")

    def test_ngay_ap_dung_nghi(self):
        self.assertEqual(lich.ngay_ap_dung_nghi(datetime(*T2, 6, 0)), date(2026, 11, 2))
        self.assertEqual(lich.ngay_ap_dung_nghi(datetime(*T2, 21, 0)), date(2026, 11, 3))
        self.assertEqual(lich.ngay_ap_dung_nghi(datetime(2026, 11, 6, 21, 0)), date(2026, 11, 9))
        self.assertEqual(lich.ngay_ap_dung_nghi(datetime(2026, 11, 7, 6, 0)), date(2026, 11, 9))   # thứ bảy
        self.assertEqual(lich.ngay_ap_dung_nghi(datetime(2026, 11, 8, 21, 0)), date(2026, 11, 9))  # chủ nhật

    def test_doc_file_trang_thai(self):
        hom_nay, hom_qua = date(2026, 11, 2), date(2026, 11, 1)
        with tempfile.TemporaryDirectory() as d:
            def ghi(ten, noi_dung):
                p = os.path.join(d, ten)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(noi_dung)
                return p
            self.assertIs(lich.doc_nghi_hoc(ghi("a", "2026-11-02\n"), hom_nay), True)
            self.assertIs(lich.doc_nghi_hoc(ghi("b", "2026-11-01\n"), hom_nay), False)
            self.assertIs(lich.doc_nghi_hoc(ghi("c", ""), hom_nay), False)
            self.assertIs(lich.doc_nghi_hoc(os.path.join(d, "khong_co"), hom_nay), False)
            self.assertIs(lich.doc_gia_su(ghi("d", '{"ngay": "2026-11-02", "co": true}'), hom_nay), True)
            self.assertIs(lich.doc_gia_su(ghi("e", '{"ngay": "2026-11-02", "co": false}'), hom_nay), False)
            self.assertIsNone(lich.doc_gia_su(ghi("f", '{"ngay": "2026-11-01", "co": true}'), hom_nay))
            self.assertIsNone(lich.doc_gia_su(ghi("g", ""), hom_nay))
            self.assertIsNone(lich.doc_gia_su(ghi("h", "{hong"), hom_nay))
            self.assertIsNone(lich.doc_gia_su(os.path.join(d, "khong_co"), hom_nay))
            self.assertIsNone(lich.doc_gia_su(ghi("i", "[]"), hom_nay))


if __name__ == "__main__":
    unittest.main()
