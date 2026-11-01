# Màn hình chờ trên TV: nhắc việc buổi sáng và buổi tối

## Mục đích

Pi luôn cắm vào TV ở phòng khách. Hai khung giờ có người qua lại nhiều nhất là sáng 6:30–7:15 (chuẩn bị cho Tùng Lâm, lớp 2, đi học)
và tối 18:00–22:00. Hiện giờ, lúc không ai chơi, TV chỉ đứng ở màn bắt đầu trò Đố vui.

Bố mẹ muốn TV **tự nhắc Tùng Lâm từng việc theo giờ**, để con tự nhìn mà làm, bố mẹ đỡ phải giục.
Con **không cần bấm gì**: màn hình tự chuyển việc khi đến giờ.
Việc quan trọng nhất buổi sáng là **uống nước**.

## Mục tiêu

- Sáng thứ Hai–thứ Sáu, 6:30–7:15: lần lượt nhắc 8 việc, mỗi lần một việc thật to.
- Tối mọi ngày, 18:00–22:00: nhắc đi tắm, dọn đồ chơi, và hiện đồng hồ cùng việc sắp tới lúc rảnh.
- Nhìn từ xa (phòng khách, đang đánh răng hay thay đồ) vẫn đọc được.

## Không làm

- Không có nút "đã xong" hay chấm điểm: chỉ nhắc theo giờ (bố mẹ đã chọn như vậy).
- Không giao việc cho em gái (hơn 2 tuổi, chưa giao việc được).
- Không thêm việc ăn sáng: Tùng Lâm ăn sáng ở cổng trường sau khi ra khỏi nhà.

## Sẽ là thất bại nếu

- Màn hình chờ chen ngang khi Tùng Lâm đang chơi dở một lượt Đố vui, hoặc khi em đang chơi Bé tập nói.
- Nhắc sai ngày: nhắc đi học vào thứ Bảy hoặc Chủ nhật.
- Chữ nhỏ, đứng xa không đọc được, hoặc màu chói lúc vừa ngủ dậy.

## Giao diện (bố mẹ đã chọn)

**Kiểu "một việc thật to"**, giống mặt đồng hồ thông minh, chiếm toàn màn hình:
- trên cùng: giờ hiện tại và "còn N phút" (đến 7:15 buổi sáng, đến hết việc đang nhắc buổi tối);
- giữa: emoji màu thật to (font Noto Color Emoji, như trang Bé tập nói) và tên việc thật to;
- dưới: dãy chấm cho biết đang ở việc thứ mấy trong buổi.

**Màu nền đổi theo thời gian còn lại**, dùng đúng bảng bố mẹ chọn, theo thứ tự:

| Giai đoạn | Màu nền |
|---|---|
| Còn sớm | `#9FA0FF` |
| Bình thường | `#D5E8E6` |
| Nhanh lên | `#FFF3E3` |
| Sắp muộn | `#FF7171` |

Chữ dùng màu sẫm cùng tông với nền, để đủ tương phản.

## Lịch buổi sáng (thứ Hai–thứ Sáu)

| Giờ | Việc |
|---|---|
| 6:30 | Đi vệ sinh |
| 6:35 | Đánh răng, rửa mặt |
| 6:45 | Thay quần áo |
| 6:52 | **Uống nước** (nhắc lại lần nữa sau 2 phút) |
| 6:55 | Soạn sách vở |
| 7:05 | Lấy hộp sữa tươi |
| 7:08 | Mang cặp |
| 7:10 | Đi giày |
| 7:15 | Ra khỏi nhà (ăn sáng ở cổng trường) |

Bố mẹ đã đồng ý với các mốc giờ này.
Giai đoạn màu buổi sáng: còn sớm 6:30–6:50, bình thường 6:50–7:05, nhanh lên 7:05–7:10, sắp muộn 7:10–7:15.

Lời chào sáng có sẵn lúc 6:44 (`chao_sang.py`, cron, đọc thứ ngày tháng và một câu đố cộng) vẫn giữ nguyên. Lúc đó màn hình vẫn hiện việc đang làm.

## Lịch buổi tối (mọi ngày)

| Giờ | Màn hình |
|---|---|
| 18:00–18:20 | 🛁 "Đi tắm thôi!" |
| 18:30–20:00, hôm có gia sư | Lặng lẽ hiện "Đang học với cô". Lúc 19:15–19:20 hiện "Nghỉ 5 phút", trùng với câu nhắc qua loa camera của `nhac_nghi.py`. |
| 20:00–20:15 | 🧸 "Dọn đồ chơi nào!", màu đổi dần qua 4 giai đoạn trong 15 phút |
| 20:28 | Lời chúc ngủ ngon có sẵn (`chuc_ngu_ngon.py`) vẫn giữ |
| Lúc rảnh | Đồng hồ to và một dòng "Tiếp theo: 20:00 dọn đồ chơi" |
| Từ 22:00 | Nền tối, chữ "Chúc cả nhà ngủ ngon", sau đó màn hình đen hẳn để không chói phòng |

"Hôm có gia sư" do `nhac_nghi.py` quyết định (đếm người qua camera trong 18:30–18:50). Hôm không có cô thì 18:30–20:00 là lúc rảnh.

## Giọng nói

Khi chuyển sang việc mới, loa Pi đọc tên việc bằng giọng VieNeu đã tạo sẵn, giống các câu khác trong dự án (tạo trước, không tạo lúc chạy).
Riêng "uống nước" thì đọc lại thêm một lần sau 2 phút.

## Nút "Hôm nay con nghỉ học" (bố mẹ đã chọn)

Trên trang điện thoại có một nút "Hôm nay con nghỉ học", để bố mẹ bấm vào ngày nghỉ lễ, nghỉ hè hay ốm.
Bấm rồi thì sáng hôm đó không nhắc việc đi học, cả trên màn hình lẫn qua giọng đọc. Nút chỉ có hiệu lực trong ngày, hôm sau tự trở lại bình thường.
Bấm từ tối hôm trước cho sáng hôm sau cũng được. Buổi tối (tắm, dọn đồ chơi) vẫn nhắc như thường.

## Nhường chỗ cho trò chơi

- **Từ 7:05 đến 7:15** (giai đoạn "nhanh lên" và "sắp muộn"), trò Đố vui bị khoá: bấm phím không bắt đầu lượt mới, màn hình nhắc việc giữ nguyên. Lượt đang chơi dở lúc 7:05 thì dừng lại để nhường cho màn nhắc việc. *(Bố mẹ chọn khoá từ 7:05; dừng lượt dở là Claude tự quyết.)*
- Ai bấm phím (bàn phím, hộp nút Arduino, tay cầm điện thoại) hoặc chạm hình Bé tập nói thì màn hình chờ nhường chỗ, như các màn khác đang làm.
- Ngoài 7:05–7:15, đang chơi dở một lượt Đố vui thì màn hình chờ không được tự chen vào. Hết lượt, hoặc đứng yên một lúc, thì màn hình chờ quay lại.
- Báo khóc (camera) vẫn được chuyển TV sang camera như hiện nay.

## Ràng buộc từ hệ thống hiện có

- TV chạy Chromium kiosk mở `http://localhost:8080` (`do_vui/mo_tro_choi.sh`). Trang hiện tại nhận phím qua SSE `/phim` từ `may_chu.py`.
- Các trang chuyển qua lại bằng `location = ...`: `index.html` (Đố vui), `be_tv.html`, `camera.html`.
- Giọng đọc tạo sẵn bằng VieNeu (`vieneu-venv`, chạy chậm khoảng 4 lần thời gian thực) và lưu vào `web/am_thanh/` theo `ten_file()` của `tao_cau_hoi.py`.
- Múi giờ của Pi là Asia/Ho_Chi_Minh.
- **Pi không bật hay tắt được TV**: dây micro-HDMI hiện tại không có CEC. TV phải đang bật thì người trong nhà mới thấy màn hình, còn giọng đọc qua loa Pi thì vẫn nghe được dù TV tắt.
  *(Chưa hỏi được bố mẹ có để TV bật từ 6:30 không. Bản thiết kế không dựa vào việc TV bật, nên giọng đọc phải tự đứng được một mình.)*

## Claude tự quyết (bố mẹ chưa xác nhận)

- **Giọng nhắc do máy chủ phát**, không phải trang màn hình chờ, nên giọng vẫn vang lên kể cả khi đang chơi Đố vui. Chơi xong quay lại màn hình chờ thì màn hiện đúng việc của lúc đó (không phát lại những câu đã lỡ).
- **18:30–18:50**, khi chưa biết hôm đó có cô hay không, màn hình hiện như lúc rảnh (đồng hồ và việc tiếp theo). `nhac_nghi.py` ghi kết quả vào một file trạng thái lúc 18:50, và màn hình đọc file đó.
- **Sau 22:00**, "màn hình đen" là một trang đen, không tắt TV qua HDMI-CEC, vì CEC trên dây hiện tại không hoạt động.

## Để người làm tự quyết

- Màn hình chờ là trang mới hay gắn vào trang hiện có, và cách nó quay về sau khi chơi.
- Cách `nhac_nghi.py` báo "hôm nay có gia sư" cho màn hình (ví dụ một file trạng thái).
- Ngoài 6:30–7:15 và 18:00–22:00 (ban ngày, đêm khuya trước 6:30): mình đề xuất giữ màn bắt đầu Đố vui như hiện nay vào ban ngày, và màn đen trước 6:30. *(Claude tự quyết, bố mẹ chưa xác nhận.)*
- Bố cục chi tiết, cỡ chữ, hiệu ứng chuyển màu và emoji cụ thể cho từng việc.
