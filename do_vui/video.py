"""Video gia đình gửi từ điện thoại (trang /video), phát toàn màn hình trên TV bằng VLC.

Video nằm trong ~/hoc/video, ngoài thư mục web và không đưa lên git. Ảnh xem trước nằm trong
~/hoc/video/.anh. Trình duyệt trên Pi không phát được video iPhone (HEVC) nên dùng VLC.
"""
import json, os, re, shutil, subprocess, threading, time

THU_MUC = os.path.expanduser("~/hoc/video")
ANH_NHO = os.path.join(THU_MUC, ".anh")
DUOI_HOP_LE = (".mov", ".mp4", ".m4v")
TOI_DA = 500 * 1024 * 1024          # mỗi video
CHUA_TRONG = 1024 * 1024 * 1024     # thẻ nhớ phải còn trống chừng này sau khi nhận video

khoa_phat = threading.RLock()
# Hàng phát: ds là các tên theo thứ tự phát, vi_tri là video đang chiếu. Mỗi lần bấm phát/dừng thì
# lan tăng lên, luồng phát của lần cũ thấy lan đã đổi thì tự thôi.
dang_phat = {"ten": None, "p": None, "ds": [], "vi_tri": 0, "lap": False, "lan": 0}
_do_dai = {}  # (tên, giờ sửa) -> số giây, để không gọi ffprobe mỗi lần mở danh sách
_khoa_do_dai = threading.Lock()


def ten_an_toan(ten):
    """Tên file gửi lên -> tên lưu trên Pi, hoặc None nếu không phải video. Bỏ đường dẫn và ký tự lạ."""
    ten = os.path.basename(ten.replace("\\", "/")).strip()
    goc, duoi = os.path.splitext(ten)
    goc = re.sub(r"[^\w\- ]", "_", goc).strip(" ._")[:80]
    if not goc or duoi.lower() not in DUOI_HOP_LE:
        return None
    return goc + duoi.lower()


def ly_do_tu_choi(do_dai, con_trong):
    """Câu báo lỗi nếu không nhận được video cỡ do_dai byte, None nếu nhận được."""
    if do_dai <= 0:
        return "Video trống"
    if do_dai > TOI_DA:
        return f"Video quá lớn ({do_dai // 2**20} MB), tối đa {TOI_DA // 2**20} MB"
    if con_trong - do_dai < CHUA_TRONG:
        return f"Thẻ nhớ Pi sắp đầy (còn {con_trong // 2**20} MB trống)"
    return None


def duong_dan(ten):
    ten = ten_an_toan(ten or "")
    if not ten:
        return None
    p = os.path.join(THU_MUC, ten)
    return p if os.path.isfile(p) else None


def con_trong():
    os.makedirs(THU_MUC, exist_ok=True)
    return shutil.disk_usage(THU_MUC).free


def luu(nguon, do_dai, ten):
    """Đọc do_dai byte từ nguon vào ~/hoc/video. Trả về tên đã lưu; trùng tên thì thêm (2), (3)..."""
    ten = ten_an_toan(ten)
    goc, duoi = os.path.splitext(ten)
    so = 1
    while os.path.exists(os.path.join(THU_MUC, ten)):
        so += 1
        ten = f"{goc} ({so}){duoi}"
    tam = os.path.join(THU_MUC, f".dang_gui_{time.time_ns()}")
    try:
        with open(tam, "wb") as f:
            con = do_dai
            while con > 0:
                khoi = nguon.read(min(con, 1 << 20))
                if not khoi:
                    raise IOError("Mất kết nối giữa chừng")
                f.write(khoi)
                con -= len(khoi)
        os.replace(tam, os.path.join(THU_MUC, ten))
    finally:
        if os.path.exists(tam):
            os.remove(tam)
    tao_anh_nho(ten)
    return ten


def tao_anh_nho(ten):
    os.makedirs(ANH_NHO, exist_ok=True)
    anh = os.path.join(ANH_NHO, ten + ".jpg")
    if not os.path.exists(anh):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.5", "-i", os.path.join(THU_MUC, ten),
                        "-frames:v", "1", "-vf", "scale=320:-2", anh], timeout=60)
    return anh if os.path.exists(anh) else None


def so_giay(ten):
    p = os.path.join(THU_MUC, ten)
    khoa = (ten, os.path.getmtime(p))
    # Mỗi lần chỉ một ffprobe: Pi đang bận thì ffprobe chậm, trang /video hỏi lại mỗi 4 giây
    # sẽ chồng thêm ffprobe mới lên, Pi càng quá tải
    with _khoa_do_dai:
        return _so_giay(p, khoa)


def _so_giay(p, khoa):
    if khoa not in _do_dai:
        try:
            ra = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
                                capture_output=True, text=True, timeout=20).stdout
            _do_dai[khoa] = round(float(json.loads(ra)["format"]["duration"]))
        except (ValueError, KeyError, subprocess.TimeoutExpired):
            _do_dai[khoa] = None
    return _do_dai[khoa]


def cac_ten():
    """Tên các video, mới gửi lên trước: cũng là thứ tự phát lần lượt."""
    os.makedirs(THU_MUC, exist_ok=True)
    ds = [t for t in os.listdir(THU_MUC)
          if not t.startswith(".") and os.path.isfile(os.path.join(THU_MUC, t)) and ten_an_toan(t)]
    return sorted(ds, key=lambda t: os.path.getmtime(os.path.join(THU_MUC, t)), reverse=True)


def danh_sach():
    ds = []
    for ten in cac_ten():
        p = os.path.join(THU_MUC, ten)
        ds.append({"ten": ten, "mb": round(os.path.getsize(p) / 2**20, 1),
                   "ngay": time.strftime("%d/%m %H:%M", time.localtime(os.path.getmtime(p))),
                   "giay": so_giay(ten)})
    dang = ten_dang_phat()
    return {"video": ds, "dang_phat": dang, "lap": dang_phat["lap"], "con_trong_mb": con_trong() // 2**20,
            "thu_tu": f"{dang_phat['vi_tri'] + 1}/{len(dang_phat['ds'])}" if dang else None}


def ten_dang_phat():
    p = dang_phat["p"]
    return dang_phat["ten"] if p and p.poll() is None else None


def hang_tu(ds, ten):
    """Hàng phát khi bấm ▶ ở video ten: video đó rồi các video bên dưới; ten rỗng là cả danh sách."""
    return ds[ds.index(ten):] if ten in ds else list(ds)


def vi_tri_sau(vi_tri, so_video, lap):
    """Video phát tiếp theo, None khi hết hàng mà không lặp."""
    if vi_tri + 1 < so_video:
        return vi_tri + 1
    return 0 if lap and so_video else None


def phat(ten=""):
    """Phát lần lượt trên TV, toàn màn hình, có tiếng, bắt đầu từ video ten (rỗng: từ video đầu).
    Hết hàng thì TV về màn đang hiện trước đó."""
    if ten and not duong_dan(ten):
        return False
    ds = hang_tu(cac_ten(), ten_an_toan(ten) if ten else "")
    if not ds:
        return False
    with khoa_phat:
        dung()
        dang_phat.update(ds=ds, vi_tri=0)
        lan = dang_phat["lan"]
    threading.Thread(target=_chay_hang, args=(lan,), daemon=True).start()
    return True


def _sang_video_sau():
    sau = vi_tri_sau(dang_phat["vi_tri"], len(dang_phat["ds"]), dang_phat["lap"])
    if sau == 0:
        dang_phat["ds"] = cac_ten()  # vòng lặp mới: có cả video vừa gửi lên
    dang_phat["vi_tri"] = len(dang_phat["ds"]) if sau is None else sau


def _video_toi_luot():
    """Tên video tới lượt, bỏ qua video đã bị xoá trong lúc chờ; None khi hết hàng."""
    for _ in range(1000):
        ds, i = dang_phat["ds"], dang_phat["vi_tri"]
        if i >= len(ds):
            return None
        if os.path.isfile(os.path.join(THU_MUC, ds[i])):
            return ds[i]
        _sang_video_sau()
    return None


def _chay_hang(lan):
    moi_truong = dict(os.environ, XDG_RUNTIME_DIR=f"/run/user/{os.getuid()}", WAYLAND_DISPLAY="wayland-0")
    while True:
        with khoa_phat:
            if dang_phat["lan"] != lan:
                return
            ten = _video_toi_luot()
            if not ten:
                return dung()
            p = subprocess.Popen(
                ["cvlc", "--fullscreen", "--play-and-exit", "--no-video-title-show", "--no-osd",
                 os.path.join(THU_MUC, ten)],
                env=moi_truong, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            dang_phat.update(ten=ten, p=p)
        bat_dau = time.time()
        p.wait()
        if time.time() - bat_dau < 2:
            time.sleep(2)  # VLC không mở được tệp: đừng mở lại liên tục khi đang lặp
        with khoa_phat:
            if dang_phat["lan"] != lan:
                return
            _sang_video_sau()


def _tat(p):
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


def tiep():
    """Bỏ qua video đang chiếu; luồng phát tự sang video sau."""
    _tat(dang_phat["p"])


def dat_lap(bat):
    dang_phat["lap"] = bool(bat)


def dung():
    """Dừng cả hàng phát."""
    with khoa_phat:
        dang_phat["lan"] += 1
        p = dang_phat["p"]
        dang_phat.update(ten=None, p=None, ds=[], vi_tri=0)
        _tat(p)


def xoa(ten):
    p = duong_dan(ten)
    if not p:
        return False
    if ten_dang_phat() == os.path.basename(p):
        tiep()  # xoá video đang chiếu thì sang video sau
    os.remove(p)
    anh = os.path.join(ANH_NHO, os.path.basename(p) + ".jpg")
    if os.path.exists(anh):
        os.remove(anh)
    return True
