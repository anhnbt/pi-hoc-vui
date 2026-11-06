"""Tạo kho câu hỏi và giọng đọc cho trò Đố vui.

Câu Toán bám chương trình Toán 2 Kết nối tri thức, nửa đầu học kì I. Đề đổi theo tuần (số ngẫu nhiên lấy
theo số tuần trong năm); câu con trả lời sai trong 7 ngày qua được giữ sang đề mới.

Chạy lâu (Pi 4 mất khoảng 15 giây mỗi câu), nhưng file âm thanh nào có rồi thì bỏ qua,
nên chạy lại chỉ tạo phần còn thiếu. cau_hoi.js được ghi trước khi tạo giọng: câu chưa có giọng vẫn hiện chữ.
"""
import os, json, random, hashlib, datetime

os.environ["HF_HUB_OFFLINE"] = "1"  # model đã tải sẵn, không cần mạng

THU_MUC = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(THU_MUC, "web")
AM_THANH = os.path.join(WEB, "am_thanh")
CAU_HOI_JS = os.path.join(WEB, "cau_hoi.js")
KET_QUA = os.path.expanduser("~/hoc/ket_qua.jsonl")  # máy chủ ghi mỗi lần con trả lời

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

# Số câu mỗi dạng Toán trong một đề tuần
SO_CAU = {"qua_10": 50, "so_thieu": 25, "so_100": 40, "thanh_phan": 20, "pham_vi_100": 30,
          "loi_van": 70, "don_vi": 15}

TEN = ["Lan", "Minh", "Hoa", "Nam", "Mai", "Bình", "An", "Hà", "Linh", "Tuấn"]
NGUOI_CHO = ["mẹ", "bố", "bà", "ông", "cô giáo"]
DO_VAT = ["cái kẹo", "cái bút chì", "quả cam", "quả táo", "viên bi", "quyển vở", "bông hoa", "cái nhãn vở"]


def sai_gan(dung, bay=()):
    """Ba đáp án sai nhưng gần đúng, để con phải tính thật chứ không đoán.
    bay: đáp án sai hay gặp (ví dụ cộng nhầm thay vì trừ), luôn được đưa vào trước."""
    sai = [x for x in dict.fromkeys(bay) if x != dung and 0 <= x <= 100][:3]
    ung_vien = sorted({dung + d for d in (-10, -2, -1, 1, 2, 10)} - {dung, *sai})
    return sai + random.sample([x for x in ung_vien if 0 <= x <= 100], 3 - len(sai))


def cau(dang, hien, doc, dung, sai):
    return {"loai": "toan", "dang": dang, "hien": hien, "doc": doc, "dung": str(dung), "sai": [str(x) for x in sai]}


def cau_tinh(dang, a, dau, b, kq):
    ky_hieu = {"cộng": "+", "trừ": "−"}[dau]
    return cau(dang, f"{a} {ky_hieu} {b} = ?", f"{a} {dau} {b} bằng mấy?", kq, sai_gan(kq))


# ---- Các dạng câu Toán: mỗi hàm trả về một câu ngẫu nhiên ----

def qua_10():
    """Cộng, trừ qua 10 trong phạm vi 20 (bảng cộng, bảng trừ)."""
    if random.random() < 0.5:
        a = random.randint(2, 9)
        b = random.randint(max(2, 11 - a), 9)
        return cau_tinh("qua_10", a, "cộng", b, a + b)
    a = random.randint(11, 18)
    b = random.randint(a - 9, 9)
    return cau_tinh("qua_10", a, "trừ", b, a - b)


def so_thieu():
    """Tìm số còn thiếu trong phép cộng, trừ phạm vi 20."""
    a = random.randint(2, 9)
    b = random.randint(max(2, 11 - a), 9)
    c = a + b
    kieu = random.randrange(4)
    if kieu == 0:
        return cau("so_thieu", f"? + {b} = {c}", f"Số nào cộng {b} bằng {c}?", a, sai_gan(a, [c + b]))
    if kieu == 1:
        return cau("so_thieu", f"{a} + ? = {c}", f"{a} cộng mấy bằng {c}?", b, sai_gan(b, [c + a]))
    if kieu == 2:
        return cau("so_thieu", f"{c} − ? = {a}", f"{c} trừ mấy bằng {a}?", b, sai_gan(b, [c + a]))
    return cau("so_thieu", f"? − {b} = {a}", f"Số nào trừ {b} bằng {a}?", c, sai_gan(c, [a - b]))


def so_100():
    """Số đến 100: liền trước, liền sau, chục và đơn vị, lớn nhất, bé nhất, so sánh."""
    kieu = random.randrange(5)
    if kieu == 0:
        n = random.randint(11, 99)
        if random.random() < 0.5:
            return cau("so_100", f"Số liền sau của {n} là số nào?", f"Số liền sau của {n} là số nào?",
                       n + 1, sai_gan(n + 1, [n - 1, n + 10]))
        return cau("so_100", f"Số liền trước của {n} là số nào?", f"Số liền trước của {n} là số nào?",
                   n - 1, sai_gan(n - 1, [n + 1, n - 10]))
    if kieu == 1:
        c, d = random.sample(range(1, 10), 2)
        n = c * 10 + d
        dung = f"{c} chục {d} đơn vị"
        sai = [f"{d} chục {c} đơn vị", f"{c} chục {c} đơn vị", f"{d} chục {d} đơn vị"]
        return {"loai": "toan", "dang": "so_100", "hien": f"Số {n} gồm mấy chục, mấy đơn vị?",
                "doc": f"Số {n} gồm mấy chục và mấy đơn vị?", "dung": dung, "sai": sai}
    if kieu == 2:
        c, d = random.randint(1, 9), random.randint(0, 9)
        n = c * 10 + d
        return cau("so_100", f"Số gồm {c} chục và {d} đơn vị là số nào?",
                   f"Số gồm {c} chục và {d} đơn vị là số nào?", n,
                   sai_gan(n, [d * 10 + c] if d else [c]))
    if kieu == 3:
        c, d = random.sample(range(1, 10), 2)
        so = list(dict.fromkeys([c * 10 + d, d * 10 + c, c * 10 + c, d * 10 + d]))
        lon = random.random() < 0.5
        dung = max(so) if lon else min(so)
        ten = "lớn nhất" if lon else "bé nhất"
        hien = ", ".join(map(str, so))
        return cau("so_100", f"Số nào {ten}?\n{hien}", f"Trong các số {hien}, số nào {ten}?", dung,
                   [x for x in so if x != dung])
    a, b = random.randint(10, 99), random.randint(10, 99)
    if random.random() < 0.4:
        b = (a % 10) * 10 + a // 10 if a % 10 else a  # đảo chữ số: 56 và 65, dễ nhầm nhất
    if random.random() < 0.15:
        b = a
    dau = ">" if a > b else "<" if a < b else "="
    return {"loai": "toan", "dang": "so_100", "hien": f"{a} ? {b}",
            "doc": f"Con chọn dấu lớn hơn, bé hơn hay bằng: {a} và {b}?",
            "dung": dau, "sai": [x for x in (">", "<", "=") if x != dau]}


def thanh_phan():
    """Tên gọi thành phần: số hạng, tổng, số bị trừ, số trừ, hiệu."""
    a = random.randint(5, 9)
    b = random.randint(11 - a, 9)
    if random.random() < 0.5:
        return cau("thanh_phan", f"Tổng của {a} và {b} là bao nhiêu?", f"Tổng của {a} và {b} là bao nhiêu?",
                   a + b, sai_gan(a + b, [a - b]))
    c = a + b
    if random.random() < 0.5:
        return cau("thanh_phan", f"Hiệu của {c} và {b} là bao nhiêu?", f"Hiệu của {c} và {b} là bao nhiêu?",
                   a, sai_gan(a, [c + b]))
    return cau("thanh_phan", f"Số bị trừ là {c}, số trừ là {a}.\nHiệu là bao nhiêu?",
               f"Số bị trừ là {c}, số trừ là {a}. Hiệu là bao nhiêu?", b, sai_gan(b, [c + a]))


def pham_vi_100():
    """Cộng, trừ trong phạm vi 100: phần lớn không nhớ, một phần ba có nhớ (sắp học sau giữa kì)."""
    co_nho = random.random() < 1 / 3
    if random.random() < 0.5:
        if co_nho:  # 47 + 6
            a = random.randint(1, 8) * 10 + random.randint(5, 9)
            b = random.randint(10 - a % 10, 9)
        else:  # 34 + 25
            a1, a2 = random.randint(1, 8), random.randint(0, 8)
            b = random.randint(0, 9 - a1) * 10 + random.randint(1, 9 - a2)
            a = a1 * 10 + a2
        return cau_tinh("pham_vi_100", a, "cộng", b, a + b)
    if co_nho:  # 42 − 7
        a = random.randint(2, 9) * 10 + random.randint(0, 4)
        b = random.randint(a % 10 + 1, 9)
    else:  # 68 − 25
        a1, a2 = random.randint(2, 9), random.randint(1, 9)
        b = random.randint(0, a1 - 1) * 10 + random.randint(1, a2)
        a = a1 * 10 + a2
    return cau_tinh("pham_vi_100", a, "trừ", b, a - b)


def so_hai(phep):
    """Cặp số cho bài lời văn: phần lớn trong phạm vi 20 có qua 10, đôi khi số tròn chục."""
    if random.random() < 0.8:
        a = random.randint(4, 9)
        b = random.randint(max(2, 11 - a), 9)
    else:
        a, b = random.randint(2, 6) * 10, random.randint(1, 3) * 10
    return (a, b) if phep == "cong" else (a + b, b)


def loi_van():
    """Toán có lời văn: thêm, bớt, gộp, nhiều hơn, ít hơn, đơn vị đo."""
    A, B = random.sample(TEN, 2)
    vat = random.choice(DO_VAT)
    kieu = random.randrange(9)
    if kieu == 0:
        a, b = so_hai("cong")
        de = (f"{A} có {a} {vat}, {random.choice(NGUOI_CHO)} cho {A} thêm {b} {vat}. "
              f"Hỏi {A} có tất cả bao nhiêu {vat}?")
        kq, bay = a + b, [a - b]
    elif kieu == 1:
        a, b = so_hai("tru")
        de = f"{A} có {a} {vat}, {A} cho bạn {b} {vat}. Hỏi {A} còn lại bao nhiêu {vat}?"
        kq, bay = a - b, [a + b]
    elif kieu == 2:
        a, b = so_hai("tru")
        de = f"Trên cây có {a} con chim, có {b} con bay đi. Hỏi trên cây còn lại bao nhiêu con chim?"
        kq, bay = a - b, [a + b]
    elif kieu == 3:
        a, b = so_hai("cong")
        de = f"Lớp em có {a} bạn nam và {b} bạn nữ. Hỏi lớp em có tất cả bao nhiêu bạn?"
        kq, bay = a + b, [a - b]
    elif kieu == 4:
        a, b = so_hai("cong")
        de = f"{A} có {a} {vat}. {B} có nhiều hơn {A} {b} {vat}. Hỏi {B} có bao nhiêu {vat}?"
        kq, bay = a + b, [a - b]
    elif kieu == 5:
        a, b = so_hai("tru")
        de = f"{A} có {a} {vat}. {B} có ít hơn {A} {b} {vat}. Hỏi {B} có bao nhiêu {vat}?"
        kq, bay = a - b, [a + b]
    elif kieu == 6:
        a, b = so_hai("tru")
        de = f"{A} có {a} {vat}, {B} có {b} {vat}. Hỏi {A} có nhiều hơn {B} bao nhiêu {vat}?"
        kq, bay = a - b, [a + b]
    elif kieu == 7:
        a, b = so_hai("tru")
        de = f"{B} có {b} {vat}, {A} có {a} {vat}. Hỏi {B} có ít hơn {A} bao nhiêu {vat}?"
        kq, bay = a - b, [a + b]
    else:
        a, b = so_hai("tru")
        de = random.choice([
            f"Thùng to có {a} lít nước, thùng nhỏ có ít hơn thùng to {b} lít nước. Hỏi thùng nhỏ có bao nhiêu lít nước?",
            f"Bao gạo cân nặng {a - b} ki-lô-gam, bao ngô nặng hơn bao gạo {b} ki-lô-gam. Hỏi bao ngô cân nặng bao nhiêu ki-lô-gam?",
            f"Sợi dây dài {a} đề-xi-mét, bố cắt đi {b} đề-xi-mét. Hỏi sợi dây còn lại dài bao nhiêu đề-xi-mét?",
        ])
        kq = a if "nặng hơn" in de else a - b
        bay = [a - 2 * b] if "nặng hơn" in de else [a + b]
    return cau("loi_van", de, de, kq, sai_gan(kq, bay))


def don_vi():
    """Đề-xi-mét, ki-lô-gam, lít."""
    kieu = random.randrange(4)
    if kieu == 0:
        a = random.randint(1, 9)
        return cau("don_vi", f"{a} dm = ? cm", f"{a} đề-xi-mét bằng bao nhiêu xăng-ti-mét?", a * 10,
                   sai_gan(a * 10, [a, a * 100]))
    if kieu == 1:
        a = random.randint(1, 9)
        return cau("don_vi", f"{a * 10} cm = ? dm", f"{a * 10} xăng-ti-mét bằng bao nhiêu đề-xi-mét?", a,
                   sai_gan(a, [a * 10, a * 100]))
    a = random.randint(5, 15)
    b = random.randint(2, 9)
    don, doc_don = ("kg", "ki-lô-gam") if kieu == 2 else ("l", "lít")
    if random.random() < 0.5:
        kq, hien, doc = a + b, f"{a} {don} + {b} {don} = ?", f"{a} {doc_don} cộng {b} {doc_don} bằng bao nhiêu?"
    else:
        a = max(a, b + 1)
        kq, hien, doc = a - b, f"{a} {don} − {b} {don} = ?", f"{a} {doc_don} trừ {b} {doc_don} bằng bao nhiêu?"
    return {"loai": "toan", "dang": "don_vi", "hien": hien, "doc": doc, "dung": f"{kq} {don}",
            "sai": [f"{x} {don}" for x in sai_gan(kq)]}


DANG = {"qua_10": qua_10, "so_thieu": so_thieu, "so_100": so_100, "thanh_phan": thanh_phan,
        "pham_vi_100": pham_vi_100, "loi_van": loi_van, "don_vi": don_vi}


def tuan_nay(ngay=None):
    nam, tuan, _ = (ngay or datetime.date.today()).isocalendar()
    return nam * 100 + tuan


def cau_toan(hat_giong):
    random.seed(hat_giong)
    cau_hoi, da_co = [], set()
    for dang, so in SO_CAU.items():
        lan = 0
        while sum(c["dang"] == dang for c in cau_hoi) < so and lan < so * 50:
            lan += 1
            c = DANG[dang]()
            if c["doc"] not in da_co:
                da_co.add(c["doc"])
                cau_hoi.append(c)
    return cau_hoi


def cau_tieng_viet():
    random.seed(2019)
    cau = []
    for dung, sai in CHINH_TA:
        cau.append({"loai": "chinh_ta", "hien": "Chữ nào viết đúng?",
                    "doc": f"Con nghe bố đọc nhé: {dung}. Chữ nào viết đúng?",
                    "dung": dung, "sai": [sai]})
    tat_ca_van = [v for _, v in VAN]
    for chu, van in VAN:
        cau.append({"loai": "van", "hien": f"Chữ “{chu}” có vần gì?", "doc": f"Chữ {chu} có vần gì?",
                    "dung": van, "sai": random.sample([v for v in tat_ca_van if v != van], 3)})
    return cau


def cau_sai_gan_day(cau_cu, ket_qua, hom_nay=None):
    """Câu Toán trong đề cũ mà con trả lời sai trong 7 ngày qua: giữ sang đề mới."""
    tu = (hom_nay or datetime.date.today()) - datetime.timedelta(days=7)
    sai = {k["id"] for k in ket_qua if not k.get("dung") and k.get("ngay", "") >= tu.isoformat()}
    return [c for c in cau_cu if c.get("loai") == "toan" and c.get("id") in sai]


def doc_de_cu():
    try:
        with open(CAU_HOI_JS, encoding="utf-8") as f:
            noi_dung = f.read()
        return json.loads(noi_dung[noi_dung.index("{"):noi_dung.rindex("}") + 1])["cau_hoi"]
    except (OSError, ValueError, KeyError):
        return []


def doc_ket_qua():
    try:
        with open(KET_QUA, encoding="utf-8") as f:
            return [json.loads(dong) for dong in f if dong.strip()]
    except (OSError, ValueError):
        return []


def ten_file(cau):
    return hashlib.md5(cau.encode()).hexdigest()[:12] + ".wav"


def am(cau):
    return "am_thanh/" + ten_file(cau)


def main():
    de_cu = doc_de_cu()
    giu_lai = cau_sai_gan_day(de_cu, doc_ket_qua())
    cau_hoi = cau_toan(tuan_nay()) + cau_tieng_viet()
    for c in cau_hoi:
        c["id"] = ten_file(c["doc"])[:12]
        c["am"] = am(c.pop("doc"))
    da_co = {c["id"] for c in cau_hoi}
    cau_hoi = [c for c in giu_lai if c["id"] not in da_co] + cau_hoi
    print(f"Đề tuần {tuan_nay()}: {len(cau_hoi)} câu, giữ lại {len(giu_lai)} câu con làm sai", flush=True)

    cau_noi = {"mo_dau": MO_DAU, "ket_thuc": KET_THUC, "khen": KHEN, "sai": SAI}
    du_lieu = {"cau_hoi": cau_hoi, "am": {k: [am(x) for x in v] if isinstance(v, list) else am(v)
                                          for k, v in cau_noi.items()}}
    tam = CAU_HOI_JS + ".tam"
    with open(tam, "w", encoding="utf-8") as f:
        f.write("window.DU_LIEU = " + json.dumps(du_lieu, ensure_ascii=False, indent=1) + ";\n")
    os.replace(tam, CAU_HOI_JS)

    # Giọng đọc của câu đề cũ không còn dùng thì xoá (chỉ xoá file thuộc đề cũ, không đụng file của trò khác)
    dang_dung = {c["am"] for c in cau_hoi}
    for c in de_cu:
        p = os.path.join(WEB, c.get("am", ""))
        if c.get("am") and c["am"] not in dang_dung and os.path.isfile(p):
            os.remove(p)

    # Câu đọc lưu trong đề chỉ là tên file, nên tạo lại danh sách câu cần đọc từ hàm sinh
    can_doc = {}
    for c in cau_toan(tuan_nay()) + cau_tieng_viet():
        can_doc[ten_file(c["doc"])] = c["doc"]
    for cau in [MO_DAU, KET_THUC] + KHEN + SAI:
        can_doc[ten_file(cau)] = cau
    os.makedirs(AM_THANH, exist_ok=True)
    con_thieu = [cau for f, cau in can_doc.items() if not os.path.exists(os.path.join(AM_THANH, f))]
    print(f"Cần tạo giọng {len(con_thieu)} câu", flush=True)
    if con_thieu:
        from vieneu import Vieneu
        tts = Vieneu()
        for i, cau in enumerate(con_thieu, 1):
            tam = os.path.join(AM_THANH, "dang_tao.wav")
            tts.save(tts.infer(cau), tam)
            os.replace(tam, os.path.join(AM_THANH, ten_file(cau)))  # TV không phát phải file đang ghi dở
            print(f"[{i}/{len(con_thieu)}] {cau}", flush=True)
    print("Xong!", flush=True)


if __name__ == "__main__":
    main()
