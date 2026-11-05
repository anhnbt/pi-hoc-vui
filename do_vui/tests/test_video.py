import os, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import video
from video import ten_an_toan, ly_do_tu_choi, hang_tu, vi_tri_sau, TOI_DA, CHUA_TRONG

GB = 1024 ** 3


class TestVideo(unittest.TestCase):
    def test_ten_video_iphone_giu_nguyen(self):
        self.assertEqual(ten_an_toan("IMG_1674.MOV"), "IMG_1674.mov")

    def test_bo_duong_dan_de_khong_ghi_ra_ngoai_thu_muc(self):
        self.assertEqual(ten_an_toan("../../.bashrc.mp4"), "bashrc.mp4")
        self.assertEqual(ten_an_toan("C:\\a\\b\\con gái.mp4"), "con gái.mp4")

    def test_khong_phai_video_thi_tu_choi(self):
        self.assertIsNone(ten_an_toan("anh.jpg"))
        self.assertIsNone(ten_an_toan(".mov"))
        self.assertIsNone(ten_an_toan(""))

    def test_gioi_han_kich_thuoc_va_cho_trong(self):
        self.assertIsNone(ly_do_tu_choi(50 * 2**20, 4 * GB))
        self.assertIn("quá lớn", ly_do_tu_choi(TOI_DA + 1, 10 * GB))
        self.assertIn("sắp đầy", ly_do_tu_choi(200 * 2**20, CHUA_TRONG + 100 * 2**20))
        self.assertEqual(ly_do_tu_choi(0, 4 * GB), "Video trống")


class TestHangPhat(unittest.TestCase):
    def test_bam_phat_mot_video_thi_phat_tu_do_tro_xuong(self):
        ds = ["c.mov", "b.mov", "a.mov"]
        self.assertEqual(hang_tu(ds, "b.mov"), ["b.mov", "a.mov"])
        self.assertEqual(hang_tu(ds, ""), ds)

    def test_het_hang_thi_dung_tru_khi_bat_lap(self):
        self.assertEqual(vi_tri_sau(0, 3, False), 1)
        self.assertIsNone(vi_tri_sau(2, 3, False))
        self.assertEqual(vi_tri_sau(2, 3, True), 0)
        self.assertIsNone(vi_tri_sau(0, 0, True))

    def test_bo_qua_video_da_bi_xoa_trong_luc_cho(self):
        with tempfile.TemporaryDirectory() as thu_muc:
            for ten in ("a.mov", "c.mov"):
                open(os.path.join(thu_muc, ten), "w").close()
            cu = video.THU_MUC, dict(video.dang_phat)
            try:
                video.THU_MUC = thu_muc
                video.dang_phat.update(ds=["b.mov", "c.mov", "a.mov"], vi_tri=0, lap=False)
                self.assertEqual(video._video_toi_luot(), "c.mov")
                video.dang_phat.update(ds=["c.mov", "b.mov"], vi_tri=1)
                self.assertIsNone(video._video_toi_luot())
            finally:
                video.THU_MUC = cu[0]
                video.dang_phat.update(cu[1])


if __name__ == "__main__":
    unittest.main()
