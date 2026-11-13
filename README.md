# StudyTask 个人学习任务管理系统

《软件工程》实验一交付物。基于教师提供的 SRS（指导书附录 A）实现，**单用户、本地运行**的学习任务管理 Web 应用。

技术栈：Python 3.11+ / Flask 3 / SQLite（标准库 sqlite3）/ 原生 HTML+CSS（无前端框架）。

## 功能对照（2.3 节核心功能清单）

| 编号 | 功能 | 实现位置 |
| --- | --- | --- |
| P1-F01 | 新建任务（名称、课程、描述、截止日期、优先级），必填校验 | `app.py::task_new`、`services.py::validate_task_form` |
| P1-F02 | 查看 / 编辑 / 删除（删除需二次确认页） | `task_detail`、`task_edit`、`task_delete` + `confirm_delete.html` |
| P1-F03 | 状态：待完成 / 进行中 / 已完成，变更持久保存 | `task_status`、`services.py::update_status` |
| P1-F04 | 按课程、状态、优先级（可组合）筛选 | `services.py::fetch_tasks` |
| P1-F05 | 逾期 / 即将到期识别（未完成任务，3 天内为即将到期） | `services.py::due_state`、`task_due_flag` |
| P1-F06 | 统计总数、完成数、完成率（无任务时 0%） | `services.py::compute_stats` |
| P1-F07 | 本地持久化（SQLite，重启不丢数据） | `db.py`、`instance/studytask.db` |

## 从零开始运行

```bash
# 1. 进入项目目录
cd StudyTask

# 2. 创建虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate
# macOS / Linux: python3 -m venv .venv && source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动（首次启动自动建库建表）
python app.py
```

浏览器打开 <http://127.0.0.1:5000> 即可使用。默认端口 5000，如需修改见 `app.py` 末尾的 `app.run(...)`。

> 也可用 Flask 命令启动：`flask --app app run --port 5000`。
> 手动初始化数据库（可选）：`flask --app app init-db`。

## 运行自动化测试

```bash
python -m pytest -v
```

测试使用临时数据库，不会影响 `instance/studytask.db` 中的真实数据。18 条用例全部通过，覆盖指导书 2.5 节 T1—T10 及边界情况（非法日期、超长字段、非法状态、404 页面等）。

## 仓库与版本管理

远程仓库：<https://github.com/li1234666/StudyTask>（公开仓库，分支 `main`，验收版本标签 `baseline-v1`）。

指导书要求提交的材料都在仓库里：源码（`app.py`/`db.py`/`services.py`、`templates/`、`static/`）、`tests/`、`README.md`、`SUBMIT.md`、`AI_DEV_LOG.md`，以及 `docs/` 下的实验报告、需求验收表、答辩 PPT 与运行截图。

`.gitignore` 已排除 `.venv/`、`instance/`、`__pycache__/`、`.pytest_cache/`、WPS 临时锁文件 `~$*` 等，仓库中不含数据库文件与凭据。

更新代码时先克隆仓库，改完后 `git add -A`、`git commit -m "说明"`、`git push` 即可。

## 目录结构

```
StudyTask/
├── app.py                  # 应用入口与全部路由
├── db.py                   # SQLite 连接与建表脚本
├── services.py             # 业务规则：校验、筛选、逾期判定、统计
├── run_server.py           # 无重载模式启动脚本（便于后台运行）
├── templates/              # base / index / form / detail / confirm_delete / error
├── static/style.css        # 页面样式
├── tests/test_app.py       # pytest 自动化测试（T1—T10 + 边界）
├── docs/                   # 实验报告、需求验收表、答辩 PPT、运行截图
├── instance/studytask.db   # 运行时生成的数据库（不入库，见 .gitignore）
├── requirements.txt
├── AI_DEV_LOG.md           # 关键 AI 协作记录
└── README.md
```

> 说明：本机未安装 Git 客户端，仓库的 `.git` 已由 dulwich 生成（提交、分支、标签均真实存在）。安装 Git 后即可直接 `git push`，无需重新 `init`。

## 数据表

```
tasks(
  id 主键自增, name 1-100字, course 1-60字, description ≤1000字,
  due_date 'YYYY-MM-DD', priority 高/中/低（默认中）,
  status 待完成/进行中/已完成（默认待完成）,
  created_at, updated_at
)
```

## 关键规则说明

- **逾期**：未完成且 `due_date < 今天`；**即将到期**：未完成且 `今天 ≤ due_date ≤ 今天+3 天`；已完成任务不显示任何到期提醒（FR-07）。
- **筛选**：课程、状态、优先级可任意组合，条件为空表示不限。
- **删除**：先进入确认页，确认后才执行删除；取消则原任务保留（FR-04）。
- **完成率**：`已完成 / 总数`，四舍五入取整；总数为 0 时显示 0%。

## 已知限制

1. 单用户本地应用，无登录、无多用户与权限控制（SRS 范围外，未实现）。
2. 使用 Flask 开发服务器，仅适合本地演示，未做生产级部署。
3. 日期按服务器本地时区取“今天”，跨时区使用需另行处理。
4. 未提供数据导出/备份入口，备份可直接复制 `instance/studytask.db`。

## 常见问题

- **端口被占用**：修改 `app.py` 中 `app.run(port=...)` 的端口，或用 `flask --app app run --port 5001`。
- **想清空演示数据**：删除 `instance/studytask.db` 后重新启动，系统会自动重建空库。
- **Windows 下中文显示异常**：使用 Python 3.11+，页面已声明 UTF-8，无需额外设置。
