"""Tạo kho câu hỏi và giọng đọc cho trò Đố vui.

Chạy lâu (Pi 4 mất khoảng 15 giây mỗi câu), nhưng file âm thanh nào có rồi thì bỏ qua,
nên thêm câu mới rồi chạy lại chỉ tạo phần còn thiếu.
"""
import os, json, random, hashlib

os.environ["HF_HUB_OFFLINE"] = "1"  # model đã tải sẵn, không cần mạng

THU_MUC = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(THU_MUC, "web")
AM_THANH = os.path.join(WEB, "am_thanh")

CHINH_TA = [  # (viết đúng, viết sai)
    ("con trâu", "con châu"), ("quả na", "quả la"), ("xe đạp", "se đạp"),
    ("sạch sẽ", "xạch sẽ"), ("nói chuyện", "lói chuyện"), ("trường học", "chường học"),
    ("cái nón", "cái lón"), ("con sâu", "con xâu"), ("chăm chỉ", "trăm chỉ"),
    ("vẽ tranh", "vẻ tranh"), ("suy nghĩ", "suy nghỉ"), ("ngôi sao", "ngôi xao"),
]
VAN = [  # (chữ, vần)
    ("mèo", "eo"), ("hoa", "oa"), ("trăng", "ăng"), ("sách", "ach"), ("bút", "ut"),
    ("chuối", "uôi"), ("thuyền", "uyên"), ("bánh", "anh"), ("gấu", "âu"),
    ("lửa", "ưa"), ("rừng", "ưng"), ("cây", "ây"),
]
KHEN = ["Đúng rồi! Con giỏi quá!", "Chính xác! Tuyệt vời!", "Đúng rồi! Hoan hô con!",
        "Giỏi lắm! Con làm đúng rồi!"]
SAI = ["Chưa đúng rồi, con thử lại nhé!", "Gần đúng rồi, con nghĩ thêm chút nữa nhé!"]
MO_DAU = "Chào con! Mình cùng chơi đố vui nhé. Con bấm nút mũi tên để chọn, rồi bấm nút OK nhé!"
KET_THUC = "Hoàn thành rồi! Con giỏi quá, hẹn con lần sau nhé!"


def sai_gan(dung):
    """Ba đáp án sai nhưng gần đúng, để con phải tính thật chứ không đoán."""
    ung_vien = {dung + d for d in (-10, -2, -1, 1, 2, 10)}
    return random.sample(sorted(x for x in ung_vien if x >= 0), 3)


def cau_toan(a, dau, b, kq):
    ky_hieu = {"cộng": "+", "trừ": "−", "nhân": "×"}[dau]
    return {"loai": "toan", "hien": f"{a} {ky_hieu} {b} = ?", "doc": f"{a} {dau} {b} bằng mấy?",
            "dung": str(kq), "sai": [str(x) for x in sai_gan(kq)]}


def tao_cau_hoi():
    random.seed(2019)
    cau = []
    for _ in range(12):  # cộng có nhớ trong phạm vi 20
        a = random.randint(3, 9)
        b = random.randint(11 - a, 9)
        cau.append(cau_toan(a, "cộng", b, a + b))
    for _ in range(6):  # cộng có nhớ số có hai chữ số
        a, b = random.randint(1, 8) * 10 + random.randint(5, 9), random.randint(5, 9)
        cau.append(cau_toan(a, "cộng", b, a + b))
    for _ in range(12):  # trừ có nhớ trong phạm vi 20
        a = random.randint(11, 18)
        b = random.randint(a - 9, 9)
        cau.append(cau_toan(a, "trừ", b, a - b))
    for a in (2, 5):  # bảng nhân 2 và 5
        for b in random.sample(range(1, 11), 6):
            cau.append(cau_toan(a, "nhân", b, a * b))
    for dung, sai in CHINH_TA:
        cau.append({"loai": "chinh_ta", "hien": "Chữ nào viết đúng?",
                    "doc": f"Con nghe bố đọc nhé: {dung}. Chữ nào viết đúng?",
                    "dung": dung, "sai": [sai]})
    tat_ca_van = [v for _, v in VAN]
    for chu, van in VAN:
        cau.append({"loai": "van", "hien": f"Chữ “{chu}” có vần gì?", "doc": f"Chữ {chu} có vần gì?",
                    "dung": van, "sai": random.sample([v for v in tat_ca_van if v != van], 3)})
    return cau


def ten_file(cau):
    return hashlib.md5(cau.encode()).hexdigest()[:12] + ".wav"


def main():
    cau_hoi = tao_cau_hoi()
    cau_noi = {"mo_dau": MO_DAU, "ket_thuc": KET_THUC, "khen": KHEN, "sai": SAI}

    can_doc = [c["doc"] for c in cau_hoi] + [MO_DAU, KET_THUC] + KHEN + SAI
    os.makedirs(AM_THANH, exist_ok=True)
    con_thieu = [c for c in can_doc if not os.path.exists(os.path.join(AM_THANH, ten_file(c)))]
    print(f"{len(can_doc)} câu, cần tạo giọng {len(con_thieu)} câu", flush=True)
    if con_thieu:
        from vieneu import Vieneu
        tts = Vieneu()
        for i, cau in enumerate(con_thieu, 1):
            tts.save(tts.infer(cau), os.path.join(AM_THANH, ten_file(cau)))
            print(f"[{i}/{len(con_thieu)}] {cau}", flush=True)

    # Trang web chỉ cần biết tên file âm thanh, không cần biết câu chữ được đọc
    def am(cau):
        return "am_thanh/" + ten_file(cau)

    for c in cau_hoi:
        c["am"] = am(c.pop("doc"))
    du_lieu = {"cau_hoi": cau_hoi, "am": {k: [am(x) for x in v] if isinstance(v, list) else am(v)
                                          for k, v in cau_noi.items()}}
    with open(os.path.join(WEB, "cau_hoi.js"), "w", encoding="utf-8") as f:
        f.write("window.DU_LIEU = " + json.dumps(du_lieu, ensure_ascii=False, indent=1) + ";\n")
    print("Xong!", flush=True)


if __name__ == "__main__":
    main()
