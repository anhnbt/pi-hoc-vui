"""Máy chủ cho trò Đố vui: phục vụ trang web, và chuyển phím từ điều khiển TV (HDMI-CEC)
hoặc tay cầm điện thoại (/tay-cam) sang trang."""
import array, collections, http.server, json, math, os, queue, re, socket, subprocess, tempfile, threading, time
from urllib.parse import urlparse, parse_qs, quote

import loa_camera
from tao_be import CANH_BAO_KHOC
from tao_cau_hoi import AM_THANH, ten_file

THU_MUC = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(THU_MUC, "web")
CEC = "/dev/cec0"
PHIM_CEC = {  # mã nút điều khiển theo chuẩn CEC
    "0x00": "chon", "0x01": "len", "0x02": "xuong", "0x03": "trai", "0x04": "phai",
    "0x0d": "nghe_lai",  # nút Back/Exit: đọc lại câu hỏi
    "0x71": "xanh_duong", "0x72": "do", "0x73": "xanh_la", "0x74": "vang",
}

PHIM_HOP_LE = set(PHIM_CEC.values()) | {"camera"}

# Camera Imou trong nhà: dùng luồng phụ 640x480 H.264 cho nhẹ. Mật khẩu nằm trong ~/hoc/camera.env
# (dòng CAM_MAT_KHAU=...), không có file đó thì tắt tính năng camera.
CAM_IP = "192.168.1.15"
CAM_ENV = os.path.expanduser("~/hoc/camera.env")

# Báo khi em bé khóc: đo độ to micro camera mỗi nửa giây (chỉ đo, không ghi âm lại).
# Phòng yên lặng khoảng -74 dBFS, người lớn nói chuyện gần camera khoảng -30.
NGUONG_KHOC = float(os.environ.get("NGUONG_KHOC", -25))  # dBFS, to hơn mức này là "ồn"
SO_LAN_ON = 6                # 6 trong 10 lần đo gần nhất (khoảng 3 giây) đều ồn thì báo
NGHI_GIUA_HAI_LAN = 120      # giây, để không báo dồn dập khi bé khóc lâu
NHAT_KY = os.path.expanduser("~/hoc/log.txt")

# Lời nhắn từ trang /loi-nhan: câu có sẵn thì phát giọng VieNeu đã đọc trước (tao_loi_nhan.py),
# câu gõ tay thì đọc ngay bằng Piper chạy thường trực (doc_nhanh.py, trong ~/hoc/venv)
PIPER_PY = os.path.expanduser("~/hoc/venv/bin/python")
LOA_HOP_LE = {"camera", "pi", "ca_hai"}
DAI_TOI_DA = 200  # ký tự

nguoi_nghe = []  # mỗi trang đang mở có một hàng đợi phím
khoa_noi = threading.Lock()  # mỗi lúc chỉ đọc một lời nhắn
doc_nhanh = None


def dia_chi_ip():
    """IP của Pi trong mạng nhà (không gửi gì ra ngoài, chỉ hỏi hệ điều hành đi đường nào)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.168.1.1", 80))
        return s.getsockname()[0]


def gui_phim(phim):
    for q in list(nguoi_nghe):
        q.put(phim)


def dia_chi_camera():
    try:
        with open(CAM_ENV, encoding="utf-8") as f:
            mat_khau = dict(d.strip().split("=", 1) for d in f if "=" in d)["CAM_MAT_KHAU"]
    except (OSError, KeyError):
        return None
    return f"rtsp://admin:{quote(mat_khau, safe='')}@{CAM_IP}:554/cam/realmonitor?channel=1&subtype=1"


def mo_piper():
    """Gọi khi đang giữ khoa_noi. Nạp giọng mất khoảng 10 giây nên máy chủ mở sẵn ngay lúc khởi động."""
    global doc_nhanh
    if doc_nhanh is None or doc_nhanh.poll() is not None:
        doc_nhanh = subprocess.Popen([PIPER_PY, os.path.join(THU_MUC, "doc_nhanh.py")],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        doc_nhanh.stdout.readline()  # "san_sang"


def doc_bang_piper(chu, tep):
    mo_piper()
    doc_nhanh.stdin.write(json.dumps({"chu": chu, "tep": tep}) + "\n")
    doc_nhanh.stdin.flush()
    if doc_nhanh.stdout.readline().strip() != "xong":
        raise RuntimeError("Piper không đọc được")


def noi_loi_nhan(chu, loa):
    with khoa_noi:
        tep = os.path.join(AM_THANH, ten_file(chu))
        tam = None
        if not os.path.exists(tep):
            tam = tep = tempfile.mktemp(suffix=".wav")
            doc_bang_piper(chu, tep)
        try:
            pi = None
            if loa in ("pi", "ca_hai"):
                pi = subprocess.Popen(["aplay", "-q", tep])
            if loa in ("camera", "ca_hai"):
                loa_camera.phat(tep)
            if pi:
                pi.wait()
        finally:
            if tam:
                os.remove(tam)
    with open(NHAT_KY, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Lời nhắn ({loa}): {chu}\n")


def bao_khoc(db):
    gui_phim("camera")  # TV chuyển sang camera, trừ khi anh đang chơi dở một lượt
    subprocess.Popen(["aplay", "-q", os.path.join(AM_THANH, ten_file(CANH_BAO_KHOC))])
    with open(NHAT_KY, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Báo em bé khóc (to nhất {db:.0f} dBFS)\n")


def nghe_khoc():
    lan_truoc = 0
    while True:
        rtsp = dia_chi_camera()
        if not rtsp:
            time.sleep(60)
            continue
        p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-rtsp_transport", "tcp", "-i", rtsp,
             "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        gan_day = collections.deque(maxlen=10)
        to_nhat = -100
        while len(khoi := p.stdout.read(8000)) == 8000:  # nửa giây: 4000 mẫu 16-bit
            mau = array.array("h", khoi)
            db = 20 * math.log10(math.sqrt(sum(x * x for x in mau) / len(mau)) / 32768 or 1e-9)
            gan_day.append(db > NGUONG_KHOC)
            to_nhat = max(to_nhat, db) if any(gan_day) else -100
            if sum(gan_day) >= SO_LAN_ON and time.time() - lan_truoc > NGHI_GIUA_HAI_LAN:
                lan_truoc = time.time()
                bao_khoc(to_nhat)
                gan_day.clear()
        p.kill()
        p.wait()
        time.sleep(10)  # camera mất mạng hoặc khởi động lại: đợi rồi nghe lại


def nghe_cec():
    # Đăng ký Pi với TV là "đầu phát" để TV chuyển phím điều khiển sang
    subprocess.run(["cec-ctl", "-d", CEC, "--playback", "--osd-name", "Do vui"], capture_output=True)
    p = subprocess.Popen(["cec-ctl", "-d", CEC, "--monitor"], stdout=subprocess.PIPE, text=True)
    for dong in p.stdout:
        m = re.search(r"ui-cmd:.*\((0x[0-9a-f]{2})\)\s*$", dong)
        if m and m.group(1) in PHIM_CEC:
            gui_phim(PHIM_CEC[m.group(1)])


class XuLy(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=WEB, **k)

    def tra_loi_chu(self, ma, noi_dung=""):
        self.send_response(ma)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(noi_dung.encode())

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/noi":
            loa = parse_qs(url.query).get("loa", ["camera"])[0]
            do_dai = int(self.headers.get("Content-Length", 0))
            chu = self.rfile.read(min(do_dai, 4 * DAI_TOI_DA)).decode("utf-8", "replace").strip()
            if loa not in LOA_HOP_LE or not chu or len(chu) > DAI_TOI_DA:
                return self.tra_loi_chu(400, "Lời nhắn trống hoặc quá dài")
            try:
                noi_loi_nhan(chu, loa)
            except Exception as loi:
                return self.tra_loi_chu(500, f"Không đọc được: {loi}")
            return self.tra_loi_chu(200, "Đã đọc")
        phim = parse_qs(url.query).get("phim", [""])[0]
        # Phím Đố vui, hoặc "be:<mã hình>" từ tay cầm Bé tập nói
        hop_le = phim in PHIM_HOP_LE or re.fullmatch(r"be:[a-z_]+", phim)
        if url.path != "/bam" or not hop_le:
            return self.tra_loi_chu(400)
        gui_phim(phim)
        self.tra_loi_chu(200)

    def do_GET(self):
        if self.path == "/tay-cam":
            self.path = "/tay_cam.html"
        if self.path == "/be":
            self.path = "/be_tay_cam.html"
        if self.path == "/loi-nhan":
            self.path = "/loi_nhan.html"
        if self.path == "/dia-chi":
            return self.tra_loi_chu(200, f"http://{dia_chi_ip()}:8080/tay-cam")
        if urlparse(self.path).path == "/camera.mjpg":
            return self.phat_camera()
        if self.path != "/phim":
            return super().do_GET()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        q = queue.Queue()
        nguoi_nghe.append(q)
        try:
            while True:
                try:
                    self.wfile.write(f"data: {q.get(timeout=15)}\n\n".encode())
                except queue.Empty:
                    self.wfile.write(b": con song\n\n")  # giữ kết nối, và phát hiện trang đã đóng
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            nguoi_nghe.remove(q)

    def phat_camera(self):
        """Chromium không phát được RTSP, nên ffmpeg đổi sang MJPEG để thẻ <img> hiện thẳng.
        Mỗi trang xem có một ffmpeg riêng, tắt ngay khi trang đóng."""
        rtsp = dia_chi_camera()
        if not rtsp:
            return self.tra_loi_chu(404, "Chưa có ~/hoc/camera.env")
        p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-rtsp_transport", "tcp", "-i", rtsp,
             "-an", "-r", "12", "-q:v", "5", "-f", "mpjpeg", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=ffmpeg")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            while khoi := p.stdout.read1(65536):
                self.wfile.write(khoi)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            p.kill()
            p.wait()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Thread(target=nghe_cec, daemon=True).start()
    threading.Thread(target=nghe_khoc, daemon=True).start()

    def mo_san_piper():
        with khoa_noi:
            mo_piper()
    threading.Thread(target=mo_san_piper, daemon=True).start()
    http.server.ThreadingHTTPServer(("0.0.0.0", 8080), XuLy).serve_forever()
