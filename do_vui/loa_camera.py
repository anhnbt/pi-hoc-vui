"""Phát một file âm thanh ra loa camera Imou/Dahua, qua kênh ngược (backchannel) của RTSP theo chuẩn ONVIF.

Camera chỉ báo có kênh này khi đường dẫn có "proto=Onvif" và yêu cầu có dòng "Require: ...backchannel".
Âm thanh gửi đi là G.711 A-law 8 kHz, mỗi gói 20 ms, gói trong chính kết nối RTSP (interleaved).

Chạy thử:  python3 loa_camera.py <file.wav>
"""
import hashlib, os, random, re, socket, struct, subprocess, sys, time

CAM_IP = "192.168.1.15"
CAM_ENV = os.path.expanduser("~/hoc/camera.env")
YEU_CAU = "Require: www.onvif.org/ver20/backchannel\r\n"


def doc_mat_khau():
    with open(CAM_ENV, encoding="utf-8") as f:
        return dict(d.strip().split("=", 1) for d in f if "=" in d)["CAM_MAT_KHAU"]


def md5(x):
    return hashlib.md5(x.encode()).hexdigest()


class Rtsp:
    def __init__(self, ip, mat_khau):
        self.url = f"rtsp://{ip}:554/cam/realmonitor?channel=1&subtype=1&unicast=true&proto=Onvif"
        self.mat_khau = mat_khau
        self.s = socket.create_connection((ip, 554), timeout=5)
        self.cseq = 0
        self.xac_thuc = None  # (realm, nonce), có sau lần đầu camera trả 401

    def hoi(self, phuong_thuc, uri, them=""):
        for _ in range(2):  # lần đầu có thể bị 401 để lấy nonce, lần sau gửi kèm digest
            self.cseq += 1
            dong = f"{phuong_thuc} {uri} RTSP/1.0\r\nCSeq: {self.cseq}\r\nUser-Agent: pi-hoc-vui\r\n{them}"
            if self.xac_thuc:
                realm, nonce = self.xac_thuc
                tra = md5(f"{md5(f'admin:{realm}:{self.mat_khau}')}:{nonce}:{md5(f'{phuong_thuc}:{uri}')}")
                dong += (f'Authorization: Digest username="admin", realm="{realm}", nonce="{nonce}", '
                         f'uri="{uri}", response="{tra}"\r\n')
            self.s.sendall((dong + "\r\n").encode())
            dau, than = self.doc_tra_loi()
            m = re.search(r'realm="([^"]+)".*?nonce="([^"]+)"', dau, re.S)
            if " 401 " in dau.splitlines()[0] and m:
                self.xac_thuc = m.groups()
                continue
            if " 200 " not in dau.splitlines()[0]:
                raise RuntimeError(f"{phuong_thuc}: {dau.splitlines()[0]}")
            return dau, than
        raise RuntimeError(f"{phuong_thuc}: camera từ chối mật khẩu")

    def doc_tra_loi(self):
        tl = b""
        while b"\r\n\r\n" not in tl:
            khoi = self.s.recv(4096)
            if not khoi:
                raise RuntimeError("camera đóng kết nối")
            tl += khoi
        dau, _, than = tl.partition(b"\r\n\r\n")
        dau = dau.decode(errors="replace")
        m = re.search(r"Content-Length:\s*(\d+)", dau, re.I)
        while m and len(than) < int(m.group(1)):
            than += self.s.recv(4096)
        return dau, than.decode(errors="replace")


def tim_kenh_nguoc(sdp):
    """Trả về (đường dẫn control, payload type của PCMA/8000) của track sendonly."""
    for phan in sdp.split("m=")[1:]:
        if "a=sendonly" in phan:
            control = re.search(r"a=control:(\S+)", phan).group(1)
            pt = re.search(r"a=rtpmap:(\d+) PCMA/8000", phan, re.I).group(1)
            return control, int(pt)
    raise RuntimeError("camera không có kênh gửi âm thanh")


def phat(duong_dan, ip=CAM_IP, mat_khau=None):
    """Phát file âm thanh (định dạng nào ffmpeg đọc được) ra loa camera; chạy xong mới trả về."""
    alaw = subprocess.run(["ffmpeg", "-v", "error", "-i", duong_dan, "-ar", "8000", "-ac", "1", "-f", "alaw", "-"],
                          capture_output=True, check=True).stdout
    r = Rtsp(ip, mat_khau or doc_mat_khau())
    try:
        _, sdp = r.hoi("DESCRIBE", r.url, YEU_CAU + "Accept: application/sdp\r\n")
        control, pt = tim_kenh_nguoc(sdp)
        uri = control if control.startswith("rtsp://") else r.url.split("?")[0].rstrip("/") + "/" + control
        dau, _ = r.hoi("SETUP", uri, YEU_CAU + "Transport: RTP/AVP/TCP;unicast;interleaved=0-1\r\n")
        phien = re.search(r"Session:\s*([^;\r\n]+)", dau).group(1)
        r.hoi("PLAY", r.url, YEU_CAU + f"Session: {phien}\r\nRange: npt=0.000-\r\n")

        ssrc, so_thu_tu, bat_dau = random.getrandbits(32), random.getrandbits(16), time.monotonic()
        for i in range(0, len(alaw), 160):  # 160 mẫu = 20 ms
            goi = struct.pack("!BBHII", 0x80, pt, (so_thu_tu + i // 160) & 0xFFFF, i, ssrc) + alaw[i:i + 160]
            r.s.sendall(b"$\x00" + struct.pack("!H", len(goi)) + goi)
            cho = bat_dau + (i + 160) / 8000 - time.monotonic()  # gửi đúng nhịp thời gian thực
            if cho > 0:
                time.sleep(cho)
        time.sleep(0.5)  # để camera phát hết đoạn cuối trong bộ đệm
        r.hoi("TEARDOWN", r.url, f"Session: {phien}\r\n")
    finally:
        r.s.close()


if __name__ == "__main__":
    phat(sys.argv[1])
    print("Đã phát xong")
