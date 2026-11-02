import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from video import ten_an_toan, ly_do_tu_choi, TOI_DA, CHUA_TRONG

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


if __name__ == "__main__":
    unittest.main()
