"""Tạo dữ liệu và giọng đọc cho trò Bé tập nói (cho bé khoảng 2 tuổi).

Mỗi từ được đọc theo kiểu bố mẹ nói với bé: gọi tên, thêm tiếng kêu hoặc một câu ngắn,
rồi nhắc lại đúng một từ cho bé bắt chước.
"""
import json, os

from tao_cau_hoi import AM_THANH, WEB, ten_file

# Không dùng hình bộ phận cơ thể rời (mắt, mũi, tay, chân…): bé 2 tuổi nhìn thấy sợ
NHOM = [  # (tên nhóm, emoji đại diện, màu nền, [(mã, emoji, chữ hiện, câu đọc)])
    ("Con vật", "🐱", "#ffb84d", [
        ("meo", "🐱", "con mèo", "Con mèo. Meo meo! Mèo."),
        ("cho", "🐶", "con chó", "Con chó. Gâu gâu! Chó."),
        ("ga", "🐔", "con gà", "Con gà. Ò ó o! Gà."),
        ("vit", "🦆", "con vịt", "Con vịt. Cạp cạp! Vịt."),
        ("bo", "🐮", "con bò", "Con bò. Ùm bò! Bò."),
        ("lon", "🐷", "con lợn", "Con lợn. Ụt ịt! Lợn."),
        ("ca", "🐟", "con cá", "Con cá. Cá bơi bơi! Cá."),
        ("voi", "🐘", "con voi", "Con voi. Voi to lắm! Voi."),
    ]),
    ("Nhà mình", "👨‍👩‍👧", "#ff8fab", [
        ("bo_bo", "👨", "Ba", "Ba đây! Ba yêu con. Ba."),
        ("me", "👩", "mẹ", "Mẹ đây! Mẹ yêu con. Mẹ."),
        ("ong", "👴", "ông", "Ông đây! Ông bế con nào. Ông."),
        ("ba", "👵", "bà", "Bà đây! Bà thơm con nào. Bà."),
        ("anh", "👦", "Anh Khoai Tây", "Anh Khoai Tây đây! Anh chơi với em. Anh."),
        ("em_be", "👶", "Dâu Tây", "Dâu Tây đây! Dâu Tây là con đấy. Dâu Tây."),
    ]),
    ("Ăn uống", "🍌", "#8fd694", [
        ("chuoi", "🍌", "quả chuối", "Quả chuối. Chuối ngọt lắm! Chuối."),
        ("tao", "🍎", "quả táo", "Quả táo. Táo đỏ đỏ! Táo."),
        ("com", "🍚", "cơm", "Cơm. Con ăn cơm nhé! Cơm."),
        ("sua", "🥛", "sữa", "Sữa. Con uống sữa nhé! Sữa."),
        ("nuoc", "💧", "nước", "Nước. Con uống nước nhé! Nước."),
        ("banh", "🍰", "bánh", "Cái bánh. Bánh ngon quá! Bánh."),
    ]),
    ("Đồ chơi", "⚽", "#7ec8f5", [
        ("bong", "⚽", "quả bóng", "Quả bóng. Lăn lăn lăn! Bóng."),
        ("o_to", "🚗", "ô tô", "Ô tô. Bim bim! Ô tô."),
        ("gau", "🧸", "gấu bông", "Gấu bông. Ôm ôm! Gấu."),
        ("may_bay", "✈️", "máy bay", "Máy bay. Vù vù! Máy bay."),
        ("sach", "📖", "quyển sách", "Quyển sách. Mình đọc sách nhé! Sách."),
        ("giay", "👟", "đôi giày", "Đôi giày. Đi giày đi chơi nào! Giày."),
    ]),
]
# Ảnh riêng thay cho emoji: đặt web/anh/<mã>.jpg (ví dụ ảnh của bé cho em_be). Thư mục này không đưa lên git.
ANH = os.path.join(WEB, "anh")
# Trò "Ai đây?": TV hiện ảnh cả nhà web/anh/ca_nha.jpg, hỏi từng người; bé chạm ảnh tròn trên điện thoại.
# (mã ảnh tròn, tên gọi, vị trí mặt trong ảnh cả nhà theo % chiều ngang và chiều dọc)
AI_DAY = [
    ("bo_bo", "Ba", 66.9, 29.7),
    ("me", "Mẹ", 30.7, 35.3),
    ("anh", "Anh Khoai Tây", 46.4, 52.6),
    ("em_be", "Dâu Tây", 62.9, 39.0),
]
AI_DAY_KHEN = "Giỏi quá! Cả nhà mình đây!"


def cau_ai_day(ten):
    return {"hoi": f"{ten} đâu nhỉ?", "dung": f"Đúng rồi! {ten} đây!", "sai": f"Đây là {ten}!"}


CHAO = "Chào bé! Mình cùng tập nói nhé!"
CANH_BAO_KHOC = "Bố mẹ ơi! Em bé đang khóc đấy!"  # may_chu.py đọc khi micro camera nghe tiếng khóc


def main():
    can_doc = [CHAO, CANH_BAO_KHOC] + [doc for *_, muc in NHOM for *_, doc in muc]
    can_doc += [AI_DAY_KHEN] + [c for _, ten, *_ in AI_DAY for c in cau_ai_day(ten).values()]
    os.makedirs(AM_THANH, exist_ok=True)
    con_thieu = [c for c in can_doc if not os.path.exists(os.path.join(AM_THANH, ten_file(c)))]
    print(f"{len(can_doc)} câu, cần tạo giọng {len(con_thieu)} câu", flush=True)
    if con_thieu:
        from vieneu import Vieneu
        tts = Vieneu()
        for i, cau in enumerate(con_thieu, 1):
            tts.save(tts.infer(cau), os.path.join(AM_THANH, ten_file(cau)))
            print(f"[{i}/{len(con_thieu)}] {cau}", flush=True)

    du_lieu = {
        "chao": "am_thanh/" + ten_file(CHAO),
        "nhom": [{"ten": ten, "emoji": emoji, "mau": mau,
                  "muc": [{"ma": ma, "emoji": e, "chu": chu, "am": "am_thanh/" + ten_file(doc),
                           **({"anh": f"anh/{ma}.jpg"} if os.path.exists(os.path.join(ANH, f"{ma}.jpg")) else {})}
                          for ma, e, chu, doc in muc]}
                 for ten, emoji, mau, muc in NHOM],
    }
    if os.path.exists(os.path.join(ANH, "ca_nha.jpg")):  # chỉ có trò "Ai đây?" khi đã đặt ảnh cả nhà
        du_lieu["ai_day"] = {
            "khen": "am_thanh/" + ten_file(AI_DAY_KHEN),
            "nguoi": [{"ma": ma, "ten": ten, "x": x, "y": y, "anh": f"anh/{ma}.jpg",
                       **{k: "am_thanh/" + ten_file(c) for k, c in cau_ai_day(ten).items()}}
                      for ma, ten, x, y in AI_DAY],
        }
    with open(os.path.join(WEB, "be_du_lieu.js"), "w", encoding="utf-8") as f:
        f.write("window.BE = " + json.dumps(du_lieu, ensure_ascii=False, indent=1) + ";\n")
    print("Xong!", flush=True)


if __name__ == "__main__":
    main()
