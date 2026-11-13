#!/usr/bin/env bash
# StudyTask 一键部署脚本（Ubuntu / Debian / CentOS 通用，含开机自启）
# 用法：curl -fsSL https://raw.githubusercontent.com/li1234666/StudyTask/main/deploy.sh | bash
set -e

REPO="https://github.com/li1234666/StudyTask.git"
DIR="$HOME/StudyTask"
PORT=5000

echo "==> 1/6 安装依赖"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y git python3 python3-venv python3-pip curl
elif command -v yum >/dev/null 2>&1; then
  sudo yum install -y git python3 python3-pip curl
fi

echo "==> 2/6 获取代码"
if [ -d "$DIR/.git" ]; then
  cd "$DIR" && git pull --ff-only || git fetch --all
else
  git clone "$REPO" "$DIR" && cd "$DIR"
fi
cd "$DIR"

echo "==> 3/6 创建虚拟环境并安装依赖"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt gunicorn

echo "==> 4/6 写入 systemd 服务（开机自启、崩溃自动重启）"
sudo tee /etc/systemd/system/studytask.service >/dev/null <<EOF
[Unit]
Description=StudyTask Flask app (gunicorn)
After=network.target

[Service]
Type=simple
User=$(id -un)
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/gunicorn -w 2 -b 0.0.0.0:$PORT app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable studytask >/dev/null 2>&1 || true
sudo systemctl restart studytask

echo "==> 5/6 等待服务就绪"
sleep 3

echo "==> 6/6 自检"
if curl -sI "http://127.0.0.1:$PORT" | head -1 | grep -q "200"; then
  IP=$(curl -s --max-time 5 ifconfig.me || echo "<公网IP>")
  echo "服务已启动并设置开机自启"
  echo "本机地址：http://127.0.0.1:$PORT"
  echo "公网地址：http://$IP:$PORT   （若打不开，请到控制台放行 TCP $PORT 端口）"
else
  echo "启动失败，查看日志："
  sudo journalctl -u studytask -n 20 --no-pager
  exit 1
fi
