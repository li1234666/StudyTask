# 实验一提交说明

## 提交时填写的两项

| 项目 | 内容 |
| --- | --- |
| 代码仓库地址 | <https://github.com/li1234666/StudyTask> |
| 网站 Web 地址 | `http://127.0.0.1:5000`（本机运行，按下一节启动） |

> 若课程要求公网可访问的地址，需按第四节部署到云服务器或托管平台，并把地址替换为公网地址。

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
- [ ] 网站地址在本机能打开（部署到公网时换成公网地址并实测）

## 四、部署到公网（仅在需要公网地址时）

以云服务器（Ubuntu）为例：

```bash
git clone https://github.com/li1234666/StudyTask.git
cd StudyTask
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

放行云服务器安全组的 5000 端口后，地址写成 `http://<服务器公网IP>:5000`；长期运行建议配 systemd 与 Nginx。

## 五、更新仓库

```bash
git clone https://github.com/li1234666/StudyTask.git
# 修改文件后
git add -A
git commit -m "说明本次改动"
git push
```
