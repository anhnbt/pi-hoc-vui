"""Tạo dữ liệu và giọng đọc cho trò Bé tập nói (cho bé khoảng 2 tuổi).

Mỗi từ được đọc theo kiểu bố mẹ nói với bé: gọi tên, thêm tiếng kêu hoặc một câu ngắn,
rồi nhắc lại đúng một từ cho bé bắt chước.
"""
import json, os

from tao_cau_hoi import AM_THANH, WEB, ten_file

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
        ("bo_bo", "👨", "bố", "Bố đây! Bố yêu con. Bố."),
        ("me", "👩", "mẹ", "Mẹ đây! Mẹ yêu con. Mẹ."),
        ("ong", "👴", "ông", "Ông đây! Ông bế con nào. Ông."),
        ("ba", "👵", "bà", "Bà đây! Bà thơm con nào. Bà."),
        ("anh", "👦", "anh", "Anh trai đây! Anh chơi với em. Anh."),
        ("em_be", "👶", "em bé", "Em bé! Em bé là con đấy. Bé."),
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
    ("Cơ thể", "👀", "#c9a7ff", [
        ("mat", "👀", "mắt", "Mắt đâu? Mắt đây! Mắt."),
        ("mui", "👃", "mũi", "Mũi đâu? Mũi đây! Mũi."),
        ("tai", "👂", "tai", "Tai đâu? Tai đây! Tai."),
        ("mieng", "👄", "miệng", "Miệng đâu? Miệng đây! Miệng."),
        ("tay", "✋", "tay", "Tay đâu? Tay đây! Vỗ tay nào!"),
        ("chan", "🦶", "chân", "Chân đâu? Chân đây! Chân."),
    ]),
]
CHAO = "Chào bé! Mình cùng tập nói nhé!"


def main():
    can_doc = [CHAO] + [doc for *_, muc in NHOM for *_, doc in muc]
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
                  "muc": [{"ma": ma, "emoji": e, "chu": chu, "am": "am_thanh/" + ten_file(doc)}
                          for ma, e, chu, doc in muc]}
                 for ten, emoji, mau, muc in NHOM],
    }
    with open(os.path.join(WEB, "be_du_lieu.js"), "w", encoding="utf-8") as f:
        f.write("window.BE = " + json.dumps(du_lieu, ensure_ascii=False, indent=1) + ";\n")
    print("Xong!", flush=True)


if __name__ == "__main__":
    main()
