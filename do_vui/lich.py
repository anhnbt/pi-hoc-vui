"""Lịch màn hình chờ trên TV: lúc nào hiện việc gì, và câu nhắc nào cần đọc.

Chỉ dùng thư viện chuẩn. Mọi mốc giờ quy ra số phút kể từ nửa đêm.
"""
import json
from datetime import date, datetime, timedelta

# (giờ, phút, emoji, chữ hiện, câu đọc)
VIEC_SANG = [
    (6, 30, "🚽", "Đi vệ sinh", "Tùng Lâm ơi, đến giờ đi vệ sinh rồi!"),
    (6, 35, "🪥", "Đánh răng, rửa mặt", "Tùng Lâm ơi, đến giờ đánh răng, rửa mặt rồi!"),
    (6, 45, "👕", "Thay quần áo", "Tùng Lâm ơi, đến giờ thay quần áo rồi!"),
    (6, 52, "💧", "Uống nước nào!", "Tùng Lâm ơi, uống một cốc nước đầy nhé!"),
    (6, 55, "📚", "Soạn sách vở", "Tùng Lâm ơi, đến giờ soạn sách vở rồi!"),
    (7, 5, "🥛", "Lấy hộp sữa tươi", "Tùng Lâm ơi, đến giờ lấy hộp sữa tươi rồi!"),
    (7, 8, "🎒", "Mang cặp", "Tùng Lâm ơi, đến giờ mang cặp rồi!"),
    (7, 10, "👟", "Đi giày", "Tùng Lâm ơi, đến giờ đi giày rồi!"),
]
NHAC_LAI_NUOC = (6, 54, "Con nhớ uống nước chưa? Uống hết cốc nước nhé!")

# (giờ bắt đầu, phút, giờ hết, phút, emoji, chữ hiện, câu đọc)
VIEC_TOI = [
    (18, 0, 18, 20, "🛁", "Đi tắm thôi!", "Tùng Lâm ơi, đi tắm sớm thôi con!"),
    (20, 0, 20, 15, "🧸", "Dọn đồ chơi nào!", "Tùng Lâm ơi, mình dọn đồ chơi gọn gàng nhé!"),
]

MAU = ["#9FA0FF", "#D5E8E6", "#FFF3E3", "#FF7171"]
DEN = "#000000"

HET_SANG = 7 * 60 + 15
BAT_DAU_SANG = 6 * 60 + 30
KHOA_DO_VUI_TU = 7 * 60 + 5
GIA_SU_TU, GIA_SU_DEN = 18 * 60 + 30, 20 * 60
NGHI_TU, NGHI_DEN = 19 * 60 + 15, 19 * 60 + 20
NGU_NGON, TAT_MAN = 22 * 60, 22 * 60 + 5
# Mốc trong buổi tối để ghi "tiếp theo"
MOC_TOI = [(18 * 60, "18:00 Đi tắm"), (20 * 60, "20:00 Dọn đồ chơi"), (22 * 60, "22:00 Đi ngủ")]


def _phut(g, p):
    return g * 60 + p


def _ket_qua(che_do, emoji, chu, mau, gio, con_phut=None, buoc=None, tong=None,
             tiep_theo=None, khoa_do_vui=False):
    return {"che_do": che_do, "emoji": emoji, "chu": chu, "mau": mau, "con_phut": con_phut,
            "buoc": buoc, "tong": tong, "tiep_theo": tiep_theo, "gio": gio,
            "khoa_do_vui": khoa_do_vui}


def _con_phut(den_phut, giay_nay):
    """Số phút còn lại, làm tròn lên khi còn lẻ giây."""
    return -(-(den_phut * 60 - giay_nay) // 60)


def _co_buoi_sang(bay_gio, nghi_hoc):
    return bay_gio.weekday() < 5 and not nghi_hoc


def trang_thai(bay_gio, nghi_hoc, co_gia_su):
    giay = bay_gio.hour * 3600 + bay_gio.minute * 60 + bay_gio.second
    phut = giay // 60
    gio = f"{bay_gio.hour}:{bay_gio.minute:02d}"

    if phut >= TAT_MAN or phut < BAT_DAU_SANG:
        return _ket_qua("den", "", "", DEN, gio)
    if NGU_NGON <= phut < TAT_MAN:
        return _ket_qua("ngu_ngon", "🌙", "Chúc cả nhà ngủ ngon", MAU[0], gio)

    if BAT_DAU_SANG <= phut < HET_SANG and _co_buoi_sang(bay_gio, nghi_hoc):
        buoc = max(i for i, v in enumerate(VIEC_SANG) if _phut(v[0], v[1]) <= phut)
        _, _, emoji, chu, _ = VIEC_SANG[buoc]
        mau = MAU[0] if phut < 6 * 60 + 50 else MAU[1] if phut < KHOA_DO_VUI_TU \
            else MAU[2] if phut < 7 * 60 + 10 else MAU[3]
        return _ket_qua("viec", emoji, chu, mau, gio, _con_phut(HET_SANG, giay),
                        buoc + 1, len(VIEC_SANG), None, phut >= KHOA_DO_VUI_TU)

    if phut < 18 * 60:
        return _ket_qua("do_vui", "🎮", "Đố vui", MAU[0], gio)

    for g, p, g2, p2, emoji, chu, _ in VIEC_TOI:
        dau, het = _phut(g, p), _phut(g2, p2)
        if dau <= phut < het:
            troi = (giay - dau * 60) / ((het - dau) * 60)
            mau = MAU[0] if troi < 0.40 else MAU[1] if troi < 0.70 else MAU[2] if troi < 0.87 else MAU[3]
            return _ket_qua("viec", emoji, chu, mau, gio, _con_phut(het, giay))

    if co_gia_su is True and GIA_SU_TU <= phut < GIA_SU_DEN:
        if NGHI_TU <= phut < NGHI_DEN:
            return _ket_qua("hoc", "🧃", "Nghỉ 5 phút", MAU[1], gio)
        return _ket_qua("hoc", "📖", "Đang học với cô", MAU[1], gio)

    tiep = next(ten for moc, ten in MOC_TOI if moc > phut)
    return _ket_qua("ranh", "🌆", "Rảnh rỗi", MAU[0], gio, tiep_theo=tiep)


def cau_dung_phut(bay_gio, nghi_hoc):
    """Câu cần đọc đúng phút này (bỏ qua giây), không có thì None."""
    gp = (bay_gio.hour, bay_gio.minute)
    if _co_buoi_sang(bay_gio, nghi_hoc):
        for g, p, _, _, cau in VIEC_SANG:
            if (g, p) == gp:
                return cau
        if gp == NHAC_LAI_NUOC[:2]:
            return NHAC_LAI_NUOC[2]
    for g, p, _, _, _, _, cau in VIEC_TOI:
        if (g, p) == gp:
            return cau
    return None


def ngay_ap_dung_nghi(bay_gio):
    """Ngày mà cờ nghỉ học đang nói tới: trước 7:15 là hôm nay, sau đó là ngày đi học kế tiếp."""
    hom_nay = bay_gio.date()
    if bay_gio.hour * 60 + bay_gio.minute < HET_SANG:
        return hom_nay
    ngay = hom_nay + timedelta(days=1)
    while ngay.weekday() >= 5:
        ngay += timedelta(days=1)
    return ngay


def doc_nghi_hoc(duong_dan, ngay):
    try:
        with open(duong_dan, encoding="utf-8") as f:
            return date.fromisoformat(f.read().strip()) == ngay
    except (OSError, ValueError):
        return False


def doc_gia_su(duong_dan, ngay):
    try:
        with open(duong_dan, encoding="utf-8") as f:
            d = json.load(f)
        if date.fromisoformat(d["ngay"]) != ngay:
            return None
        return bool(d["co"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
