import os, random, subprocess, datetime, time

os.environ["HF_HUB_OFFLINE"] = "1"  # model đã tải sẵn, không cần mạng
from vieneu import Vieneu

THU = ["thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ nhật"]

hom_nay = datetime.date.today()
a, b = random.randint(1, 10), random.randint(1, 10)
cac_cau = [
    f"Chào buổi sáng! Hôm nay là {THU[hom_nay.weekday()]}, ngày {hom_nay.day} tháng {hom_nay.month}.",
    f"Câu đố hôm nay: {a} cộng {b} bằng mấy?",
    f"Đáp án là {a + b}. Con trả lời đúng không nào? Chúc con một ngày vui vẻ!",
]

# Pi 4 tạo giọng chậm, nên tạo sẵn hết rồi mới phát
tts = Vieneu()
cac_file = []
for i, cau in enumerate(cac_cau):
    file = f"/tmp/chao_sang_{i}.wav"
    tts.save(tts.infer(cau), file)
    cac_file.append(file)


def phat(file):
    subprocess.run(["aplay", "-q", file], check=True)


phat(cac_file[0])
phat(cac_file[1])
time.sleep(15)  # cho con 15 giây suy nghĩ
phat(cac_file[2])
