# Cài trò Đố vui: máy chủ tự chạy khi bật Pi, và lệnh mở trò chơi toàn màn hình
set -e
cd ~/hoc/do_vui

dpkg -s fonts-noto-color-emoji > /dev/null 2>&1 || sudo -n apt-get install -y -q fonts-noto-color-emoji

mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/do-vui.service <<'EOF'
[Unit]
Description=Do vui - may chu tro choi

[Service]
ExecStart=/usr/bin/python3 %h/hoc/do_vui/may_chu.py
Restart=always

[Install]
WantedBy=default.target
EOF

cat > ~/hoc/do_vui/mo_tro_choi.sh <<'EOF'
#!/bin/bash
# Mở trò chơi toàn màn hình trên TV (thoát bằng Alt+F4)
export WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/$(id -u)
HO_SO="$HOME/.config/do-vui-chromium"
pkill -f "user-data-dir=$HO_SO" || true
# Lúc mới bật Pi, đợi máy chủ trò chơi chạy xong (tối đa 60 giây)
for i in $(seq 1 60); do curl -s -o /dev/null http://localhost:8080/ && break; sleep 1; done
# Hồ sơ Chromium riêng, để không nhập chung vào cửa sổ Chromium đang mở (sẽ mất toàn màn hình)
exec chromium --user-data-dir="$HO_SO" --kiosk http://localhost:8080 \
  --noerrdialogs --disable-infobars --no-first-run --disable-features=Translate --lang=vi \
  --autoplay-policy=no-user-gesture-required --password-store=basic > /dev/null 2>&1
EOF
chmod +x ~/hoc/do_vui/mo_tro_choi.sh

# Tự mở trò chơi trên TV mỗi khi bật Pi (xóa file này nếu không muốn nữa)
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/do-vui.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Đố vui
Exec=$HOME/hoc/do_vui/mo_tro_choi.sh
EOF

export XDG_RUNTIME_DIR=/run/user/$(id -u)
systemctl --user daemon-reload
systemctl --user enable --now do-vui.service
systemctl --user restart do-vui.service
sleep 1
systemctl --user is-active do-vui.service
curl -s -o /dev/null -w "Trang web: HTTP %{http_code}\n" http://localhost:8080/
