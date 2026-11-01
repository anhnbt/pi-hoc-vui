# Màn hình chờ trên TV: kế hoạch làm

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** TV tự nhắc Tùng Lâm từng việc buổi sáng (6:30–7:15, thứ Hai–thứ Sáu) và buổi tối (18:00–22:00), kèm giọng đọc qua loa Pi.

**Architecture:** Toàn bộ "bây giờ màn hình hiện gì, có đọc câu nào" nằm trong một module Python thuần `do_vui/lich.py`, có kiểm thử.
`may_chu.py` đưa trạng thái đó ra qua `GET /man-cho/trang-thai` (JSON), có một luồng nền đọc câu nhắc đúng giờ, và đẩy sự kiện `man_cho` qua SSE `/phim`.
Trang `web/man_cho.html` chỉ vẽ lại JSON mỗi vài giây. Các trang có sẵn (`index.html`, `be_tv.html`) quay về màn chờ khi rảnh.

**Tech Stack:** Python 3.11 stdlib (Pi), `unittest`; HTML/JS thuần chạy trong Chromium kiosk; giọng VieNeu tạo sẵn (vieneu-venv).

**Spec:** `docs/superpowers/specs/2026-11-01-man-hinh-cho-design.md`

## Global Constraints

- Đặt tên tiếng Việt không dấu, chữ thường, `_`, như phần còn lại của dự án. Chữ hiện ra và giọng đọc là tiếng Việt có dấu.
- Bảng màu theo đúng thứ tự: còn sớm `#9FA0FF`, bình thường `#D5E8E6`, nhanh lên `#FFF3E3`, sắp muộn `#FF7171`.
- Buổi sáng chỉ chạy thứ Hai–thứ Sáu và không chạy ngày đã bấm "Hôm nay con nghỉ học". Buổi tối chạy mọi ngày.
- Emoji dùng font `"Noto Color Emoji"`, nếu không DejaVu sẽ vẽ nét đen trắng.
- Giọng đọc tạo sẵn bằng VieNeu vào `web/am_thanh/<ten_file(cau)>`, không tạo lúc chạy.
- Mã trên Pi chạy bằng `/usr/bin/python3` (3.11), chỉ dùng stdlib cộng với pyserial có sẵn.
- `lich.py` không được import gì ngoài stdlib, để chạy kiểm thử được trên máy nào cũng được.

## Review Focus

- **Đổi ngày lúc nửa đêm và file trạng thái cũ:** `nghi_hoc.txt` hay `gia_su.json` ghi ngày hôm qua thì phải coi như không có. Thêm test vào Task 1.
- **Bấm "nghỉ học" sau 7:15:** áp dụng cho sáng hôm sau. Riêng tối thứ Sáu thì áp dụng cho thứ Hai, vì thứ Bảy, Chủ nhật vốn không nhắc. Test ở Task 1 (`ngay_ap_dung_nghi`).
- **Máy chủ khởi động lại giữa buổi** (ví dụ 6:53): không được đọc lại các câu đã qua, chỉ đọc câu đúng phút hiện tại. Test ở Task 1 (`cau_dung_phut`).
- **Đúng 7:15:00 và 22:00:00:** biên giới khoảng thời gian dùng nửa mở `[bắt đầu, kết thúc)`. Test ở Task 1.
- **File trạng thái hỏng hoặc trống** (JSON lỗi): coi như không có, máy chủ không được chết. Test ở Task 1.

---

### Task 1: Lịch và trạng thái màn hình (`lich.py`)

**Files:**
- Create: `do_vui/lich.py`
- Test: `do_vui/tests/test_lich.py`

**Interfaces:**
- Produces:
  - `VIEC_SANG: list[tuple[int, int, str, str, str]]`, gồm `(giờ, phút, emoji, chữ hiện, câu đọc)`, theo thứ tự:
    - 6:30 🚽 "Đi vệ sinh"
    - 6:35 🪥 "Đánh răng, rửa mặt"
    - 6:45 👕 "Thay quần áo"
    - 6:52 💧 "Uống nước nào!"
    - 6:55 📚 "Soạn sách vở"
    - 7:05 🥛 "Lấy hộp sữa tươi"
    - 7:08 🎒 "Mang cặp"
    - 7:10 👟 "Đi giày"

    Câu đọc có dạng "Tùng Lâm ơi, đến giờ <việc> rồi!". Riêng uống nước đọc "Tùng Lâm ơi, uống một cốc nước đầy nhé!".
  - `NHAC_LAI_NUOC = (6, 54, "Con nhớ uống nước chưa? Uống hết cốc nước nhé!")`
  - `VIEC_TOI` = tắm 18:00–18:20 🛁 "Đi tắm thôi!" (đọc "Tùng Lâm ơi, đi tắm sớm thôi con!") và dọn đồ chơi 20:00–20:15 🧸 "Dọn đồ chơi nào!" (đọc "Tùng Lâm ơi, mình dọn đồ chơi gọn gàng nhé!")
  - `MAU = ["#9FA0FF", "#D5E8E6", "#FFF3E3", "#FF7171"]`
  - `trang_thai(bay_gio: datetime, nghi_hoc: bool, co_gia_su: bool | None) -> dict`, trả về các khoá:
    - `che_do` ∈ `"viec"`, `"hoc"`, `"ranh"`, `"ngu_ngon"`, `"den"`, `"do_vui"`
    - `emoji`, `chu`, `mau` (một trong `MAU`, hoặc `"#000000"`)
    - `con_phut: int | None`, `buoc: int | None` (bắt đầu từ 1), `tong: int | None`
    - `tiep_theo: str | None`, `gio: "H:MM"`, `khoa_do_vui: bool`
  - `cau_dung_phut(bay_gio: datetime, nghi_hoc: bool) -> str | None`: câu đọc nếu đúng phút này có lịch đọc, không thì `None`.
  - `ngay_ap_dung_nghi(bay_gio: datetime) -> date`: trước 7:15 thì là hôm nay. Sau 7:15 là ngày đi học kế tiếp (bỏ thứ Bảy, Chủ nhật).
  - `doc_nghi_hoc(duong_dan: str, ngay: date) -> bool`: file chứa một ngày ISO, trùng `ngay` thì `True`. Thiếu hoặc lỗi thì `False`.
  - `doc_gia_su(duong_dan: str, ngay: date) -> bool | None`: file JSON `{"ngay": "YYYY-MM-DD", "co": bool}`. Khác ngày, thiếu hoặc lỗi thì `None`.

**Bảng khung giờ mà `trang_thai` phải trả về** (nửa mở, giờ địa phương):

| Khung giờ | `che_do` | Ghi chú |
|---|---|---|
| 22:05–6:30 | `den` | `mau` là `#000000` |
| 6:30–7:15, ngày đi học, không nghỉ | `viec` | Việc hiện tại là mốc `VIEC_SANG` gần nhất đã qua. `con_phut` tính đến 7:15. Màu: 6:30–6:50 là `MAU[0]`, 6:50–7:05 là `MAU[1]`, 7:05–7:10 là `MAU[2]`, 7:10–7:15 là `MAU[3]`. `khoa_do_vui` bật trong 7:05–7:15. |
| 6:30–18:00, các trường hợp còn lại | `do_vui` | |
| 18:00–18:20, 20:00–20:15 | `viec` | `con_phut` tính đến hết việc. Buổi tối chỉ có 1 bước nên `buoc` và `tong` là `None`. Màu theo phần thời gian đã trôi: <40% `MAU[0]`, <70% `MAU[1]`, <87% `MAU[2]`, còn lại `MAU[3]`. |
| 18:30–20:00 khi `co_gia_su is True` | `hoc` | Hiện 📖 "Đang học với cô". Riêng 19:15–19:20 hiện 🧃 "Nghỉ 5 phút". |
| Các lúc khác trong 18:00–22:00 | `ranh` | `tiep_theo` là mốc kế tiếp trong: "18:00 Đi tắm", "20:00 Dọn đồ chơi", "22:00 Đi ngủ" |
| 22:00–22:05 | `ngu_ngon` | Hiện 🌙 "Chúc cả nhà ngủ ngon" |

- [ ] **Step 1: Viết test (sẽ chạy hỏng)** trong `do_vui/tests/test_lich.py`, dùng `unittest` và `datetime(2026, 11, 2, ...)` (thứ Hai):
  - `test_sang_uong_nuoc`: 6:52 cho `che_do == "viec"`, `chu == "Uống nước nào!"`, `buoc == 4`, `tong == 8`, `con_phut == 23`, `mau == "#D5E8E6"`, `khoa_do_vui is False`.
  - `test_sang_khoa_tu_705`: 7:05 cho `khoa_do_vui is True`, `mau == "#FFF3E3"`. 7:12 cho `mau == "#FF7171"`.
  - `test_715_het_buoi_sang`: 7:15:00 cho `che_do == "do_vui"`.
  - `test_thu_bay_khong_nhac`: `datetime(2026, 11, 7, 6, 40)` cho `"do_vui"`, và `cau_dung_phut` trả `None` lúc 6:35 thứ Bảy.
  - `test_nghi_hoc`: `nghi_hoc=True` lúc 6:40 thứ Hai cho `"do_vui"`, và `cau_dung_phut` trả `None`.
  - `test_toi_tam`: 18:10 cho `chu == "Đi tắm thôi!"`, `con_phut == 10`.
  - `test_toi_gia_su`: 18:40 với `co_gia_su=True` cho `"hoc"`. Cùng giờ với `co_gia_su=None` cho `"ranh"` và `tiep_theo == "20:00 Dọn đồ chơi"`. 19:17 với `True` cho `chu == "Nghỉ 5 phút"`.
  - `test_dem`: 22:00 cho `"ngu_ngon"`, 22:05 cho `"den"`, 5:00 cho `"den"`.
  - `test_cau_dung_phut`: 6:52:30 trả câu uống nước. 6:54 trả `NHAC_LAI_NUOC[2]`. 6:53 trả `None`. 20:00 trả câu dọn đồ chơi vào cả thứ Bảy.
  - `test_ngay_ap_dung_nghi`: thứ Hai 6:00 → thứ Hai. Thứ Hai 21:00 → thứ Ba. Thứ Sáu 21:00 → thứ Hai tuần sau.
  - `test_doc_file_trang_thai`: dùng `tempfile`. Hôm qua, chuỗi rỗng, JSON lỗi và file không tồn tại đều cho `False` hoặc `None`. Đúng ngày thì đọc đúng giá trị.

- [ ] **Step 2: Chạy test để thấy nó hỏng**
  Run: `python -m unittest discover -s do_vui/tests -v`
  Expected: FAIL với `ModuleNotFoundError: No module named 'lich'` (test thêm `do_vui` vào `sys.path`).

- [ ] **Step 3: Viết `do_vui/lich.py`** với các hằng và hàm ở trên. Mỗi mốc thời gian quy ra số phút kể từ nửa đêm, dùng cho cả hai buổi.

- [ ] **Step 4: Chạy lại test**
  Run: `python -m unittest discover -s do_vui/tests -v`
  Expected: tất cả OK.

- [ ] **Step 5: Commit** `do_vui/lich.py do_vui/tests/test_lich.py` với message "Lịch màn hình chờ: việc sáng, tối và trạng thái theo giờ".

### Task 2: Giọng đọc tạo sẵn (`tao_man_cho.py`)

**Files:**
- Create: `do_vui/tao_man_cho.py` (mẫu giống `tao_loi_nhan.py`)

**Interfaces:**
- Consumes: `VIEC_SANG`, `NHAC_LAI_NUOC`, `VIEC_TOI` từ `lich.py`; `AM_THANH`, `ten_file` từ `tao_cau_hoi.py`
- Produces: một file wav trong `web/am_thanh/` cho mỗi câu đọc. Máy chủ tìm file bằng `ten_file(cau)`.

- [ ] **Step 1: Viết `tao_man_cho.py`.** Gom mọi câu đọc, bỏ qua câu đã có file, còn lại tạo bằng `Vieneu`. Đặt `HF_HUB_OFFLINE=1`, in tiến độ `[i/n]`.
- [ ] **Step 2: Chạy trên Pi**
  Run: `ssh wanbi@192.168.1.12 "cd ~/hoc/do_vui && ../vieneu-venv/bin/python tao_man_cho.py"` (chạy nền, khoảng 3 phút)
  Expected: dòng cuối là `Xong!`, và chạy lại lần nữa thì báo `cần tạo giọng 0 câu`.
- [ ] **Step 3: Commit** `do_vui/tao_man_cho.py`.

### Task 3: Máy chủ: trạng thái, nút nghỉ học, đọc đúng giờ

**Files:**
- Modify: `do_vui/may_chu.py`
- Modify: `do_vui/nhac_nghi.py` (ghi `gia_su.json`)

**Interfaces:**
- Consumes: mọi thứ Task 1 cung cấp
- Produces:
  - `GET /man-cho/trang-thai[?gio=YYYY-MM-DDTHH:MM]` trả JSON của `trang_thai(...)`. Tham số `gio` chỉ để thử giao diện.
  - `GET /nghi-hoc` trả `{"ngay": "YYYY-MM-DD", "nghi": bool}` cho ngày mà `ngay_ap_dung_nghi(now)` chỉ ra. `POST /nghi-hoc?nghi=1|0` ghi hoặc xoá `~/hoc/nghi_hoc.txt` cho ngày đó, rồi trả JSON như GET.
  - Sự kiện SSE mới `man_cho`, gửi khi `cau_dung_phut` có câu mới, và lúc 7:05.
  - `nhac_nghi.py` ghi `~/hoc/gia_su.json` = `{"ngay": <hôm nay>, "co": <kết quả>}` ngay khi quyết định xong lúc 18:50.

- [ ] **Step 1: Thêm hai đường dẫn file** `NGHI_HOC = ~/hoc/nghi_hoc.txt`, `GIA_SU = ~/hoc/gia_su.json`, cùng hàm `trang_thai_bay_gio(bay_gio)`. Hàm này ghép `lich.trang_thai` với `doc_nghi_hoc(NGHI_HOC, bay_gio.date())` và `doc_gia_su(GIA_SU, bay_gio.date())`.
- [ ] **Step 2: Thêm route `GET /man-cho/trang-thai` và `GET`/`POST /nghi-hoc`** vào `do_GET`/`do_POST`. Nếu `nghi` khác `0`/`1` thì trả 400.
- [ ] **Step 3: Thêm luồng `nhac_theo_lich()`.** Cứ 15 giây, gọi `cau_dung_phut(now, nghi_hoc)`. Nếu có câu và `(ngày, giờ:phút)` chưa đọc thì `aplay -q` file `ten_file(cau)` và `gui_phim("man_cho")`. Lúc 7:05 của ngày đi học cũng gửi `man_cho`. Thêm `"man_cho"` vào `PHIM_HOP_LE`. Thiếu file wav thì ghi một dòng vào `log.txt`, không làm chết luồng.
- [ ] **Step 4: Sửa `nhac_nghi.py`** để ghi `gia_su.json` ở cả hai nhánh (có và không có buổi học), và cả khi chạy `--thu`.
- [ ] **Step 5: Triển khai lên Pi rồi kiểm tra**
  Run:
  - `curl -s "http://localhost:8080/man-cho/trang-thai?gio=2026-11-02T06:52"`
  - `curl -s -X POST "http://localhost:8080/nghi-hoc?nghi=1"`
  - `curl -s "http://localhost:8080/nghi-hoc"`
  - `curl -s -X POST "http://localhost:8080/nghi-hoc?nghi=0"`

  Expected: JSON có `"chu": "Uống nước nào!"`. Hai lệnh POST và GET giữa chúng trả `"nghi": true`, lệnh POST cuối trả `"nghi": false`. `systemctl --user is-active do-vui` báo `active`.
- [ ] **Step 6: Commit** `do_vui/may_chu.py do_vui/nhac_nghi.py`.

### Task 4: Trang màn hình chờ, và quay về từ các trang khác

**Files:**
- Create: `do_vui/web/man_cho.html`
- Modify: `do_vui/web/index.html`
- Modify: `do_vui/web/be_tv.html`

**Interfaces:**
- Consumes: `GET /man-cho/trang-thai`, sự kiện SSE `man_cho`

- [ ] **Step 1: Viết `man_cho.html`.**
  - Bố cục kiểu "một việc thật to": dòng trên là `gio · còn N phút`, giữa là emoji 45vh và chữ 12vh, dưới là `tong` chấm với chấm thứ `buoc` nổi bật. Khi `ranh` thì thay dòng chấm bằng `tiep_theo`.
  - Nền lấy từ `mau`, chuyển màu 1 giây. Chữ dùng màu sẫm: `#26215C` trên `MAU[0]`, `#04342C` trên `MAU[1]`, `#412402` trên `MAU[2]`, `#4A1B0C` trên `MAU[3]`. `den` là màn đen trống. `ngu_ngon` là nền `#2C2C2A` chữ sáng.
  - Mỗi 5 giây hỏi lại `/man-cho/trang-thai`, truyền tiếp `?gio=` nếu URL trang có tham số này. Khi `che_do == "do_vui"` thì `location = "/"`.
  - Phím và SSE: nếu `khoa_do_vui` thì bỏ qua mọi phím, trừ `be:*` (sang `be_tv.html`) và `camera` (sang `camera.html`). Nếu không khoá thì phím bất kỳ đưa về `"/"`.
- [ ] **Step 2: Sửa `index.html`.**
  - Khi `man !== "choi"` và không có phím nào trong 60 giây, hỏi `/man-cho/trang-thai`. Nếu `che_do !== "do_vui"` thì `location = "/man_cho.html"`.
  - SSE `man_cho`: nếu `man !== "choi"` thì sang màn chờ ngay. Nếu đang chơi thì chỉ sang khi `khoa_do_vui` đang bật (đó là lúc 7:05).
  - Phím `chon` ở màn đầu hoặc màn cuối khi `khoa_do_vui` đang bật: sang màn chờ, không bắt đầu lượt mới.
- [ ] **Step 3: Sửa `be_tv.html`.** Nếu bé không chạm hay bấm gì trong 60 giây và `che_do !== "do_vui"` thì sang màn chờ. SSE `man_cho` không kéo trang của em đi.
- [ ] **Step 4: Kiểm tra bằng trình duyệt** (pane có sẵn, cỡ 1280×720), mở lần lượt `http://192.168.1.12:8080/man_cho.html?gio=` với các giờ sau:

  | `?gio=` | Phải thấy |
  |---|---|
  | `2026-11-02T06:52` | nền `#D5E8E6`, 💧, chấm thứ 4 trong 8 |
  | `2026-11-02T07:12` | nền `#FF7171`; bấm phím vẫn ở lại màn chờ |
  | `2026-11-02T18:10` | 🛁 |
  | `2026-11-02T21:00` | dòng "22:00 Đi ngủ" |
  | `2026-11-02T23:00` | màn đen |
  | `2026-11-02T10:00` | tự chuyển về `/` |

- [ ] **Step 5: Mở lại trò chơi trên TV** bằng `setsid ~/hoc/do_vui/mo_tro_choi.sh`, rồi chụp TV bằng `grim` để xác nhận trang Đố vui vẫn chạy.
- [ ] **Step 6: Commit** ba file web.

### Task 5: Nút "Hôm nay con nghỉ học" và README

**Files:**
- Modify: `do_vui/web/loi_nhan.html`
- Modify: `README.md`

**Interfaces:**
- Consumes: `GET`/`POST /nghi-hoc` của Task 3

- [ ] **Step 1: Thêm khối nút vào `loi_nhan.html`** (trang của bố mẹ, cả khi vào qua Tailscale), đặt trên phần "Câu có sẵn".
  - Khi mở trang thì gọi GET để hiện trạng thái: "Sáng thứ Ba 3/11: con đi học" hoặc "…: con nghỉ học ✅".
  - Một nút bật/tắt gửi POST `nghi=1` hoặc `nghi=0`.
  - Viết JS theo kiểu iOS 12 như phần còn lại của trang (`var`, `function`, không `?.`).
- [ ] **Step 2: README:** thêm mục "Màn hình chờ" (lịch sáng, tối; nút nghỉ học; cron không đổi; chạy `tao_man_cho.py` một lần) và cách chạy test: `python -m unittest discover -s do_vui/tests`.
- [ ] **Step 3: Kiểm tra** ở cỡ điện thoại trong trình duyệt: bấm nút hai lần, trạng thái phải đổi qua lại và `curl /nghi-hoc` trả đúng. Để lại trạng thái `nghi: false`.
- [ ] **Step 4: Commit** `do_vui/web/loi_nhan.html README.md`.
