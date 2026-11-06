# Ôn thi Toán, bạn đồng hành và pháo hoa

Ngày: 2026-11-06. Đã duyệt từng phần trong buổi brainstorm.

## Mục tiêu

Đố vui chỉ có 66 câu cố định, con gặp lại câu cũ sau vài hôm. Anh Khoai Tây (lớp 2, Kết nối tri thức)
thi giữa học kì I môn Toán thứ Hai 9/11/2026. Đợt này: kho câu Toán lớn, đổi theo tuần, có toán lời văn;
thêm bạn đồng hành và pháo hoa cho vui.

Để đợt sau: Tiếng Việt thêm dạng, Hiểu biết chung, Tiếng Anh, mở khoá dần bạn đồng hành theo sao cộng dồn
(lúc đầu 3 bạn, mỗi 10 sao mở thêm một bạn).

## Kho câu Toán (`do_vui/tao_cau_hoi.py`)

Mỗi dạng là một hàm trả về một câu ngẫu nhiên; `SO_CAU` định số câu mỗi dạng, tổng 250:

| Dạng | Số câu |
|---|---|
| `qua_10`: cộng, trừ qua 10 trong phạm vi 20 | 50 |
| `so_thieu`: `? + 6 = 14`, `15 − ? = 8` | 25 |
| `so_100`: liền trước/sau, chục và đơn vị, lớn nhất/bé nhất, điền dấu | 40 |
| `thanh_phan`: tổng, hiệu, số bị trừ, số trừ | 20 |
| `pham_vi_100`: cộng trừ phạm vi 100, một phần ba có nhớ | 30 |
| `loi_van`: thêm, bớt, gộp, nhiều hơn, ít hơn, đo lít/kg/dm | 70 |
| `don_vi`: dm ↔ cm, cộng trừ kg, lít | 15 |

- Bỏ bảng nhân (học kì II).
- Đáp án sai gần đúng; bài nhiều hơn/ít hơn luôn có đáp án "cộng nhầm thay vì trừ". Không số âm, không quá 100.
- Số ngẫu nhiên theo tuần ISO (`tuan_nay()`), cùng tuần sinh lại ra cùng đề.
- Mỗi câu có `id` (12 ký tự đầu của tên file giọng) và `dang`.
- Câu Toán con trả lời sai trong 7 ngày qua (theo `~/hoc/ket_qua.jsonl`) được giữ sang đề mới.
- `cau_hoi.js` được ghi trước khi tạo giọng: câu chưa có giọng vẫn hiện chữ. Giọng ghi vào file tạm rồi đổi tên.
- Giọng của câu đề cũ không còn dùng thì xoá; không đụng file giọng của trò khác.
- Cron trên Pi: 0:30 sáng thứ Hai (tuần ISO bắt đầu thứ Hai, Pi rảnh lúc đó).

## Máy chủ

`POST /ket-qua?id=<12 hex>&dung=0|1` ghi một dòng `{"id", "dung", "ngay"}` vào `~/hoc/ket_qua.jsonl`.
TV chỉ báo lần trả lời đầu tiên của mỗi câu. Gửi lỗi thì bỏ qua.

## TV (`do_vui/web/index.html`)

- Luồng: màn đầu → chọn bạn (3 bạn: khủng long, mèo, gấu; nhớ lần trước) → chọn chế độ → chơi → cuối.
  Bấm OK ba lần là vào chơi. Nút màu trên tay cầm chọn thẳng.
- Ôn thi Toán: 10 câu, 3 câu lời văn, 7 câu lấy xoay vòng các dạng còn lại. Đố vui trộn: 6 toán, 2 chính tả, 2 vần.
- Câu dài hơn 40 ký tự hiện chữ nhỏ, căn trái; đáp án dài hơn 6 ký tự hiện chữ nhỏ.
- Bạn đồng hành ở góc trái dưới trong vòng tròn trắng, có bong bóng lời nói:
  câu mới chớp mắt, chọn ô thì nhìn theo, đúng thì mắt sao/cười, sai thì ngạc nhiên/chóng mặt,
  đúng 3 câu liền thì lấp lánh, 20 giây không bấm thì ngủ gật, hết lượt thì thả tim.
- Pháo hoa (`canvas-confetti`, chạy trong worker, ít mảnh): đúng thì một chùm ở ô đáp án, 3 câu liền bắn từ
  hai góc, hết lượt bắn 2 giây + 0,3 giây mỗi sao. Không có tiếng pháo.
- Ảnh bạn đồng hành lấy từ repo viettyping, thu còn 540px (`web/ban/`).

## Kiểm thử

`do_vui/tests/test_tao_cau_hoi.py`: số câu mỗi dạng, đáp án đúng thật, lựa chọn khác nhau và trong 0–100,
không trùng câu, lời văn không còn chỗ trống, không còn bảng nhân, đề đổi theo tuần, giữ câu sai trong 7 ngày.
Thử tay trên trình duyệt: chọn bạn, chọn chế độ, câu lời văn, pháo hoa.
