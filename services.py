"""业务规则层：字段校验、查询筛选、逾期判定与统计。

所有规则集中在本模块，路由只负责收发表单，便于测试与后续维护。
"""
from datetime import date, datetime

PRIORITIES = ("高", "中", "低")
STATUSES = ("待完成", "进行中", "已完成")

NAME_MAX = 100
COURSE_MAX = 60
DESC_MAX = 1000
SOON_DAYS = 3  # 今日起未来 3 天内到期 → 即将到期


# ---------------------------------------------------------------- 日期工具
def parse_date(value):
    """把 YYYY-MM-DD 解析为 date；非法返回 None。"""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def due_state(due_date, today=None):
    """返回 'overdue'、'soon' 或 None。只判断日期，是否已完成由调用方决定。"""
    today = today or date.today()
    due = parse_date(due_date)
    if due is None:
        return None
    if due < today:
        return "overdue"
    if (due - today).days <= SOON_DAYS:
        return "soon"
    return None


def task_due_flag(task, today=None):
    """未完成任务才显示逾期/即将到期提醒（FR-07）。"""
    if task["status"] == "已完成":
        return None
    return due_state(task["due_date"], today)


# ---------------------------------------------------------------- 表单校验
def validate_task_form(form):
    """校验并规范化任务表单，返回 (data, errors)。

    errors 为字段名 → 错误信息 的字典；为空即通过。
    """
    data = {
        "name": (form.get("name") or "").strip(),
        "course": (form.get("course") or "").strip(),
        "description": (form.get("description") or "").strip(),
        "due_date": (form.get("due_date") or "").strip(),
        "priority": (form.get("priority") or "中").strip() or "中",
        "status": (form.get("status") or "待完成").strip() or "待完成",
    }
    errors = {}

    if not data["name"]:
        errors["name"] = "任务名称不能为空"
    elif len(data["name"]) > NAME_MAX:
        errors["name"] = f"任务名称不能超过 {NAME_MAX} 个字符"

    if not data["course"]:
        errors["course"] = "所属课程不能为空"
    elif len(data["course"]) > COURSE_MAX:
        errors["course"] = f"所属课程不能超过 {COURSE_MAX} 个字符"

    if len(data["description"]) > DESC_MAX:
        errors["description"] = f"任务描述不能超过 {DESC_MAX} 个字符"

    if not data["due_date"]:
        errors["due_date"] = "截止日期不能为空"
    elif parse_date(data["due_date"]) is None:
        errors["due_date"] = "截止日期格式应为 YYYY-MM-DD，且必须是真实存在的日期"

    if data["priority"] not in PRIORITIES:
        errors["priority"] = "优先级只能是 高、中、低"
    if data["status"] not in STATUSES:
        errors["status"] = "状态只能是 待完成、进行中、已完成"

    return data, errors


# ---------------------------------------------------------------- 查询与写入
def fetch_tasks(db, filters=None):
    """按课程、状态、优先级组合筛选任务（FR-06），按截止日期升序。"""
    filters = filters or {}
    sql = "SELECT * FROM tasks"
    conditions, params = [], []
    for field in ("course", "status", "priority"):
        value = (filters.get(field) or "").strip()
        if value:
            conditions.append(f"{field} = ?")
            params.append(value)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY due_date ASC, id ASC"
    return db.execute(sql, params).fetchall()


def fetch_task(db, task_id):
    return db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def fetch_courses(db):
    """筛选下拉框用的课程列表。"""
    rows = db.execute(
        "SELECT DISTINCT course FROM tasks ORDER BY course COLLATE NOCASE"
    ).fetchall()
    return [row["course"] for row in rows]


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_task(db, data):
    now = now_text()
    cursor = db.execute(
        """INSERT INTO tasks (name, course, description, due_date, priority, status,
                              created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["name"],
            data["course"],
            data["description"],
            data["due_date"],
            data["priority"],
            data["status"],
            now,
            now,
        ),
    )
    db.commit()
    return cursor.lastrowid


def update_task(db, task_id, data):
    db.execute(
        """UPDATE tasks SET name = ?, course = ?, description = ?, due_date = ?,
                            priority = ?, status = ?, updated_at = ?
           WHERE id = ?""",
        (
            data["name"],
            data["course"],
            data["description"],
            data["due_date"],
            data["priority"],
            data["status"],
            now_text(),
            task_id,
        ),
    )
    db.commit()


def update_status(db, task_id, status):
    if status not in STATUSES:
        raise ValueError("非法状态值")
    db.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
        (status, now_text(), task_id),
    )
    db.commit()


def delete_task(db, task_id):
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()


# ---------------------------------------------------------------- 统计
def compute_stats(db):
    """总数、完成数、完成率（FR-08）；总数为 0 时完成率为 0%。"""
    row = db.execute(
        """SELECT COUNT(*) AS total,
                  SUM(CASE WHEN status = '已完成' THEN 1 ELSE 0 END) AS completed
           FROM tasks"""
    ).fetchone()
    total = int(row["total"] or 0)
    completed = int(row["completed"] or 0)
    rate = round(completed / total * 100) if total else 0
    return {"total": total, "completed": completed, "rate": rate}
