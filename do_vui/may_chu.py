"""Máy chủ cho trò Đố vui: phục vụ trang web, và chuyển phím từ điều khiển TV (HDMI-CEC)
hoặc tay cầm điện thoại (/tay-cam) sang trang."""
import http.server, os, queue, re, socket, subprocess, threading
from urllib.parse import urlparse, parse_qs

THU_MUC = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(THU_MUC, "web")
CEC = "/dev/cec0"
PHIM_CEC = {  # mã nút điều khiển theo chuẩn CEC
    "0x00": "chon", "0x01": "len", "0x02": "xuong", "0x03": "trai", "0x04": "phai",
    "0x0d": "nghe_lai",  # nút Back/Exit: đọc lại câu hỏi
    "0x71": "xanh_duong", "0x72": "do", "0x73": "xanh_la", "0x74": "vang",
}

PHIM_HOP_LE = set(PHIM_CEC.values())

nguoi_nghe = []  # mỗi trang đang mở có một hàng đợi phím


def dia_chi_ip():
    """IP của Pi trong mạng nhà (không gửi gì ra ngoài, chỉ hỏi hệ điều hành đi đường nào)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("192.168.1.1", 80))
        return s.getsockname()[0]


def gui_phim(phim):
    for q in list(nguoi_nghe):
        q.put(phim)


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
        phim = parse_qs(url.query).get("phim", [""])[0]
        if url.path != "/bam" or phim not in PHIM_HOP_LE:
            return self.tra_loi_chu(400)
        gui_phim(phim)
        self.tra_loi_chu(200)

    def do_GET(self):
        if self.path == "/tay-cam":
            self.path = "/tay_cam.html"
        if self.path == "/dia-chi":
            return self.tra_loi_chu(200, f"http://{dia_chi_ip()}:8080/tay-cam")
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

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Thread(target=nghe_cec, daemon=True).start()
    http.server.ThreadingHTTPServer(("0.0.0.0", 8080), XuLy).serve_forever()
