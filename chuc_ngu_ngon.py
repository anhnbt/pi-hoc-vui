import os, random, subprocess, datetime, time

os.environ["HF_HUB_OFFLINE"] = "1"  # model đã tải sẵn, không cần mạng
from vieneu import Vieneu

THU = ["thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy", "Chủ nhật"]
CA_DAO = [
    "Công cha như núi Thái Sơn, nghĩa mẹ như nước trong nguồn chảy ra.",
    "Bầu ơi thương lấy bí cùng, tuy rằng khác giống nhưng chung một giàn.",
    "Nhiễu điều phủ lấy giá gương, người trong một nước phải thương nhau cùng.",
    "Ai ơi bưng bát cơm đầy, dẻo thơm một hạt, đắng cay muôn phần.",
    "Một cây làm chẳng nên non, ba cây chụm lại nên hòn núi cao.",
    "Anh em như thể tay chân, rách lành đùm bọc, dở hay đỡ đần.",
    "Muốn sang thì bắc cầu kiều, muốn con hay chữ thì yêu lấy thầy.",
    "Có công mài sắt, có ngày nên kim.",
    "Ăn quả nhớ kẻ trồng cây.",
    "Đi một ngày đàng, học một sàng khôn.",
    "Lời chào cao hơn mâm cỗ.",
    "Uống nước nhớ nguồn.",
]

ngay_mai = datetime.date.today() + datetime.timedelta(days=1)
if ngay_mai.weekday() < 5:
    nhac_ngay_mai = f"Ngày mai là {THU[ngay_mai.weekday()]}, con đi học. Con nhớ chuẩn bị cặp sách nhé."
else:
    nhac_ngay_mai = f"Ngày mai là {THU[ngay_mai.weekday()]}, con được nghỉ học. Ngủ thật ngon để mai đi chơi nhé."
ca_dao = random.choice(CA_DAO)

cac_cau = [
    "Đến giờ chuẩn bị đi ngủ rồi con ơi!",
    nhac_ngay_mai,
    "Câu ca dao tối nay là:",
    ca_dao,
    "Con nhớ đi đánh răng, đi vệ sinh, rồi lên giường nhé. Chúc con ngủ ngon!",
]

# Pi 4 tạo giọng chậm, nên tạo sẵn hết rồi mới phát
tts = Vieneu()
cac_file = []
for i, cau in enumerate(cac_cau):
    file = f"/tmp/chuc_ngu_ngon_{i}.wav"
    tts.save(tts.infer(cau), file)
    cac_file.append(file)


def phat(file):
    subprocess.run(["aplay", "-q", file], check=True)


for file in cac_file[:4]:
    phat(file)
time.sleep(2)
phat(cac_file[3])  # đọc lại câu ca dao cho con dễ nhớ
time.sleep(1)
phat(cac_file[4])
