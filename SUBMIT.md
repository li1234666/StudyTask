# 实验一提交说明

## 需要在答题框里填写的两项

| 项目 | 内容 |
| --- | --- |
| 代码仓库地址 | `https://github.com/<你的账号>/StudyTask`（建好远程仓库并推送后即为真实地址） |
| 网站 Web 地址 | `http://127.0.0.1:5000`（本机运行地址，启动方法见下） |

> 如果课程要求填写**公网可访问**的地址，需要把项目部署到云服务器或托管平台，见文末「部署到公网」一节；仅本机运行时，请填写本机地址并在说明里注明“本地运行、现场演示”。

## 一、先把仓库推到 GitHub

本机未安装 Git 客户端，但仓库的 `.git` 已由工具生成，提交与标签都是真实的（`0bc285e`，`baseline-v1`，分支 `main`），安装 Git 后无需重新初始化。

1. 在 GitHub 网页新建仓库：仓库名 `StudyTask`，**不要**勾选 “Add a README file”，其余保持默认。
2. 在项目目录内执行（把 `<你的账号>` 换成自己的）：

```bash
git remote add origin https://github.com/<你的账号>/StudyTask.git
git push -u origin main
git push origin baseline-v1
```

3. 刷新仓库页面，确认 27 个文件与 `docs/` 下的报告、验收表、PPT 都在，并能在标签列表里看到 `baseline-v1`。

仓库里不应出现 `.venv/`、`instance/studytask.db`、`__pycache__/` 或任何 `.env`、令牌文件——`.gitignore` 已排除。

## 二、启动网站并取地址

```bash
cd StudyTask
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

浏览器访问 <http://127.0.0.1:5000>。答辩时按「现场演示路径」逐项操作即可：

新建任务 → 空名称提交看校验 → 组合筛选 → 昨日到期看“已逾期” → 明日到期看“即将到期” → 改状态看统计 → 删除先取消再确认 → 重启服务看数据仍在。

## 三、提交前自检

- [ ] `python -m pytest -v` 为 18 passed
- [ ] `docs/` 内有实验报告（4 页）、需求验收表、答辩 PPT
- [ ] 根目录有 `README.md`、`requirements.txt`、`AI_DEV_LOG.md`、`.gitignore`
- [ ] 仓库地址可匿名打开，且不需要登录
- [ ] 网站地址在本机能打开（公网部署时换公网地址并实际访问一次）

## 四、部署到公网（仅在需要公网地址时）

以云服务器（Ubuntu 为例）为例，粗略步骤如下，具体按服务器环境调整：

```bash
# 服务器上
git clone https://github.com/<你的账号>/StudyTask.git
cd StudyTask
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt gunicorn
# 让服务监听所有网卡
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

然后在云服务器安全组放行 5000 端口，提交地址写成 `http://<服务器公网IP>:5000`。若要长期运行，建议配合 systemd 或 `nohup`，并在前面加 Nginx 反向代理。

注意：SQLite 数据文件位于 `instance/studytask.db`，部署后由服务首次启动时自动创建。
