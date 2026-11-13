#!/usr/bin/env bash
# StudyTask 一键部署脚本（Ubuntu / Debian / CentOS 通用）
# 用法：curl -fsSL https://raw.githubusercontent.com/li1234666/StudyTask/main/deploy.sh | bash
set -e

REPO="https://github.com/li1234666/StudyTask.git"
DIR="$HOME/StudyTask"

echo "==> 1/5 安装依赖"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y git python3 python3-venv python3-pip
elif command -v yum >/dev/null 2>&1; then
  sudo yum install -y git python3 python3-pip
fi

echo "==> 2/5 获取代码"
if [ -d "$DIR/.git" ]; then
  cd "$DIR" && git pull --ff-only
else
  git clone "$REPO" "$DIR" && cd "$DIR"
fi
cd "$DIR"

echo "==> 3/5 创建虚拟环境并安装依赖"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt gunicorn

echo "==> 4/5 启动服务"
pkill -f "gunicorn app:app" >/dev/null 2>&1 || true
sleep 1
nohup gunicorn -w 2 -b 0.0.0.0:5000 app:app > "$DIR/app.log" 2>&1 &
sleep 3

echo "==> 5/5 自检"
if curl -sI http://127.0.0.1:5000 | head -1 | grep -q "200"; then
  echo "服务已启动：http://127.0.0.1:5000"
  echo "请到云服务器控制台放行 TCP 5000 端口，然后用浏览器访问 http://<公网IP>:5000"
else
  echo "启动失败，最后 20 行日志："
  tail -20 "$DIR/app.log"
  exit 1
fi
