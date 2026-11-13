# 实验一提交说明

## 提交时填写的两项

| 项目 | 内容 |
| --- | --- |
| 代码仓库地址 | <https://github.com/li1234666/StudyTask> |
| 网站 Web 地址 | <http://8.163.15.55/>（已部署在阿里云服务器，公网可直接访问） |

> 也可以在本地运行（见第二节），本地地址为 `http://127.0.0.1:5000`。公网部署方式见第四节。

## 一、仓库里有什么

| 材料 | 位置 |
| --- | --- |
| 可运行源码 | `app.py`、`db.py`、`services.py`、`templates/`、`static/`、`run_server.py` |
| 自动化测试 | `tests/test_app.py`（18 条） |
| 运行说明 | `README.md` |
| 需求验收表 | `docs/需求验收表.docx` |
| AI 协作记录 | `AI_DEV_LOG.md` |
| 实验报告（4 页） | `docs/实验一实验报告.docx` |
| 答辩演示（9 页） | `docs/实验一答辩演示.pptx` |
| 运行截图 | `docs/screenshots/` |

分支 `main`，验收版本标签 `baseline-v1`。

## 二、启动网站

```bash
git clone https://github.com/li1234666/StudyTask.git
cd StudyTask
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

浏览器打开 <http://127.0.0.1:5000>。答辩演示顺序：新建任务 → 空名称提交看校验 → 组合筛选 → 昨日到期看“已逾期” → 明日到期看“即将到期” → 改状态看统计 → 删除先取消再确认 → 重启服务看数据仍在。

## 三、提交前自检

- [ ] `python -m pytest -v` 显示 18 passed
- [ ] 仓库首页能看到源码、`docs/`、`README.md`、`AI_DEV_LOG.md`
- [ ] 标签页能看到 `baseline-v1`
- [ ] 仓库地址在浏览器无痕窗口能匿名打开
- [ ] 网站地址 <http://8.163.15.55/> 能打开（实测返回 200，任务列表正常）

## 四、公网部署方式（已完成）

线上环境：阿里云轻量应用服务器，Ubuntu 24.04 / 2 vCPU 2 GiB，公网 IP `8.163.15.55`，站点地址 <http://8.163.15.55/>。

服务由 systemd 托管，开机自启、异常自动重启：

```bash
# 状态与日志
systemctl status studytask
journalctl -u studytask -n 50 --no-pager
# 重启
systemctl restart studytask
```

部署命令（服务器上执行）：

```bash
git clone https://github.com/li1234666/StudyTask.git
cd StudyTask
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt gunicorn
gunicorn -w 2 -b 0.0.0.0:80 app:app
```

仓库根目录的 `deploy.sh` 已封装完整流程（装依赖 → 拉代码 → 建虚拟环境 → 注册 systemd 服务 → 自检）。

## 五、更新仓库

```bash
git clone https://github.com/li1234666/StudyTask.git
# 修改文件后
git add -A
git commit -m "说明本次改动"
git push
```
