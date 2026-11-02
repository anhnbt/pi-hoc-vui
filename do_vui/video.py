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

khoa_phat = threading.Lock()
dang_phat = {"ten": None, "p": None}
_do_dai = {}  # (tên, giờ sửa) -> số giây, để không gọi ffprobe mỗi lần mở danh sách


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
    if khoa not in _do_dai:
        try:
            ra = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", p],
                                capture_output=True, text=True, timeout=20).stdout
            _do_dai[khoa] = round(float(json.loads(ra)["format"]["duration"]))
        except (ValueError, KeyError, subprocess.TimeoutExpired):
            _do_dai[khoa] = None
    return _do_dai[khoa]


def danh_sach():
    os.makedirs(THU_MUC, exist_ok=True)
    ds = []
    for ten in os.listdir(THU_MUC):
        p = os.path.join(THU_MUC, ten)
        if ten.startswith(".") or not os.path.isfile(p) or not ten_an_toan(ten):
            continue
        ds.append({"ten": ten, "mb": round(os.path.getsize(p) / 2**20, 1),
                   "ngay": time.strftime("%d/%m %H:%M", time.localtime(os.path.getmtime(p))),
                   "giay": so_giay(ten), "_gio": os.path.getmtime(p)})
    ds.sort(key=lambda v: v.pop("_gio"), reverse=True)  # mới gửi lên trước
    return {"video": ds, "dang_phat": ten_dang_phat(), "con_trong_mb": con_trong() // 2**20}


def ten_dang_phat():
    p = dang_phat["p"]
    return dang_phat["ten"] if p and p.poll() is None else None


def phat(ten):
    """Phát toàn màn hình trên TV, có tiếng; hết video VLC tự tắt, TV về màn đang hiện trước đó."""
    p = duong_dan(ten)
    if not p:
        return False
    with khoa_phat:
        dung()
        moi_truong = dict(os.environ, XDG_RUNTIME_DIR=f"/run/user/{os.getuid()}", WAYLAND_DISPLAY="wayland-0")
        dang_phat["ten"] = os.path.basename(p)
        dang_phat["p"] = subprocess.Popen(
            ["cvlc", "--fullscreen", "--play-and-exit", "--no-video-title-show", "--no-osd", p],
            env=moi_truong, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return True


def dung():
    p = dang_phat["p"]
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    dang_phat["ten"] = dang_phat["p"] = None


def xoa(ten):
    p = duong_dan(ten)
    if not p:
        return False
    if ten_dang_phat() == os.path.basename(p):
        dung()
    os.remove(p)
    anh = os.path.join(ANH_NHO, os.path.basename(p) + ".jpg")
    if os.path.exists(anh):
        os.remove(anh)
    return True
