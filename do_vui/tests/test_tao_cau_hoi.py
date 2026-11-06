import datetime, os, re, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tao_cau_hoi import cau_toan, cau_sai_gan_day, tuan_nay, SO_CAU

DE = cau_toan(202645)
TINH = {"+": lambda a, b: a + b, "−": lambda a, b: a - b}


def so(chu):
    return [int(x) for x in re.findall(r"\d+", chu)]


class TestKhoCauToan(unittest.TestCase):
    def test_so_cau_moi_dang_dung_nhu_dinh(self):
        for dang, n in SO_CAU.items():
            self.assertEqual(sum(c["dang"] == dang for c in DE), n, dang)

    def test_lua_chon_khac_nhau_va_khong_am(self):
        for c in DE:
            lua_chon = [c["dung"], *c["sai"]]
            self.assertEqual(len(set(lua_chon)), len(lua_chon), c)
            self.assertGreaterEqual(len(lua_chon), 3, c)
            self.assertFalse(any(x.startswith("-") for x in lua_chon), c)
            self.assertTrue(all(n <= 100 for x in [c["hien"], *lua_chon] for n in so(x)), c)

    def test_phep_tinh_dap_an_dung_that(self):
        for c in DE:
            m = re.fullmatch(r"(\d+) ([+−]) (\d+) = \?", c["hien"])
            if m:
                self.assertEqual(int(c["dung"]), TINH[m[2]](int(m[1]), int(m[3])), c)
            m = re.fullmatch(r"\? ([+−]) (\d+) = (\d+)", c["hien"])
            if m:
                self.assertEqual(TINH[m[1]](int(c["dung"]), int(m[2])), int(m[3]), c)
            m = re.fullmatch(r"(\d+) ([+−]) \? = (\d+)", c["hien"])
            if m:
                self.assertEqual(TINH[m[2]](int(m[1]), int(c["dung"])), int(m[3]), c)
            m = re.fullmatch(r"(\d+) \? (\d+)", c["hien"])
            if m:
                a, b = int(m[1]), int(m[2])
                self.assertEqual(c["dung"], ">" if a > b else "<" if a < b else "=", c)

    def test_khong_trung_cau(self):
        self.assertEqual(len({c["doc"] for c in DE}), len(DE))

    def test_loi_van_du_chu_va_dap_an_dung(self):
        for c in DE:
            if c["dang"] != "loi_van":
                continue
            self.assertNotIn("{", c["hien"])
            self.assertTrue(c["hien"].endswith("?"), c)
            a, b = so(c["hien"])[:2]
            hoi = c["hien"].rsplit(".", 1)[-1]
            cong = "tất cả" in hoi or "nhiều hơn" in c["hien"] and "nhiều hơn" not in hoi or "nặng hơn" in c["hien"]
            self.assertEqual(int(c["dung"]), a + b if cong else abs(a - b), c)

    def test_khong_con_bang_nhan(self):
        self.assertFalse(any("×" in c["hien"] or "nhân" in c["doc"] for c in DE))

    def test_de_doi_theo_tuan(self):
        self.assertNotEqual([c["doc"] for c in cau_toan(202645)], [c["doc"] for c in cau_toan(202646)])
        self.assertEqual([c["doc"] for c in cau_toan(202645)], [c["doc"] for c in DE])
        self.assertEqual(tuan_nay(datetime.date(2026, 11, 6)), 202645)


class TestGiuCauSai(unittest.TestCase):
    def test_giu_cau_toan_sai_trong_7_ngay(self):
        cu = [{"id": "a", "loai": "toan"}, {"id": "b", "loai": "toan"}, {"id": "c", "loai": "toan"},
              {"id": "d", "loai": "van"}]
        ket_qua = [{"id": "a", "dung": False, "ngay": "2026-11-05"},
                   {"id": "b", "dung": True, "ngay": "2026-11-05"},
                   {"id": "c", "dung": False, "ngay": "2026-10-20"},
                   {"id": "d", "dung": False, "ngay": "2026-11-05"}]
        giu = cau_sai_gan_day(cu, ket_qua, datetime.date(2026, 11, 8))
        self.assertEqual([c["id"] for c in giu], ["a"])


if __name__ == "__main__":
    unittest.main()
