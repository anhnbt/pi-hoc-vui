// Hộp nút bấm cho trò Đố vui, chạy trên Arduino Nano cắm USB vào Pi.
// Mỗi nút nối từ một chân xuống GND (dùng điện trở kéo lên có sẵn trong chip, không cần điện trở ngoài).
// Bấm nút thì gửi tên phím qua USB cho may_chu.py, kêu "bíp" và nháy đèn trên mạch.
//
// Nạp từ Pi (tắt máy chủ trước vì nó đang giữ cổng USB):
//   systemctl --user stop do-vui
//   arduino-cli compile -u -p /dev/ttyUSB0 -b arduino:avr:nano:cpu=atmega328old ~/hoc/arduino/hop_nut
//   systemctl --user start do-vui

const int SO_NUT = 6;
const int NUT[SO_NUT] = {2, 3, 4, 5, 6, 7};
const char* PHIM[SO_NUT] = {"do", "xanh_la", "vang", "xanh_duong", "chon", "nghe_lai"};
const int COI = 8;                     // còi chip: chân + vào D8, chân - vào GND
const unsigned long CHONG_NAY = 40;    // ms: tiếp điểm nút nảy vài lần khi bấm, bỏ qua các lần nảy đó

bool dang_nhan[SO_NUT];
unsigned long lan_doi[SO_NUT];
unsigned long tat_den = 0;

void bip(int tan_so, int dai) {
  // tone() kêu được với cả còi có mạch dao động sẵn lẫn còi thường
  tone(COI, tan_so, dai);
  digitalWrite(LED_BUILTIN, HIGH);
  tat_den = millis() + dai;
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < SO_NUT; i++) pinMode(NUT[i], INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  bip(1500, 80);  // kêu một tiếng khi cắm điện, để biết hộp đã sẵn sàng
}

void loop() {
  unsigned long bay_gio = millis();
  for (int i = 0; i < SO_NUT; i++) {
    bool nhan = digitalRead(NUT[i]) == LOW;
    if (nhan != dang_nhan[i] && bay_gio - lan_doi[i] > CHONG_NAY) {
      dang_nhan[i] = nhan;
      lan_doi[i] = bay_gio;
      if (nhan) {
        Serial.println(PHIM[i]);
        bip(2500, 50);
      }
    }
  }
  if (tat_den && bay_gio > tat_den) {
    digitalWrite(LED_BUILTIN, LOW);
    tat_den = 0;
  }
}
