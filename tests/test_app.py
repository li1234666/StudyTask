"""StudyTask 自动化测试：覆盖指导书 2.5 节 T1—T10 及边界情况。

运行：pytest -v
"""
import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from services import compute_stats  # noqa: E402


def day(offset=0):
    return (date.today() + timedelta(days=offset)).isoformat()


@pytest.fixture
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test_studytask.db"),
        "SECRET_KEY": "test-key",
    })


@pytest.fixture
def client(app):
    return app.test_client()


def new_task(client, name="链表实验报告", course="数据结构", due=None,
             priority="高", status="待完成", description=""):
    return client.post("/tasks/new", data={
        "name": name, "course": course, "due_date": due or day(1),
        "priority": priority, "status": status, "description": description,
    })


def count_tasks(client):
    """通过列表页统计空状态或行数，避免依赖内部接口。"""
    html = client.get("/").get_data(as_text=True)
    return html.count('class="link link-danger"')


# ---------------------------------------------------------------- T1
def test_t1_create_task_visible_in_list(client):
    resp = new_task(client, name="数据结构实验一", course="数据结构", due=day(1), priority="高")
    assert resp.status_code == 302
    html = client.get("/").get_data(as_text=True)
    assert "数据结构实验一" in html
    assert "数据结构" in html
    assert day(1) in html


# ---------------------------------------------------------------- T2
def test_t2_empty_name_rejected_without_dirty_data(client):
    resp = new_task(client, name="   ")
    assert resp.status_code == 400
    body = resp.get_data(as_text=True)
    assert "任务名称不能为空" in body
    assert count_tasks(client) == 0


def test_t2b_invalid_date_and_name_too_long(client):
    resp = new_task(client, due="2026-02-30")
    assert resp.status_code == 400
    assert "截止日期格式应为 YYYY-MM-DD" in resp.get_data(as_text=True)

    resp = new_task(client, name="任" * 101)
    assert resp.status_code == 400
    assert "任务名称不能超过 100 个字符" in resp.get_data(as_text=True)
    assert count_tasks(client) == 0


# ---------------------------------------------------------------- T3
def test_t3_edit_description_and_priority_persist(client):
    new_task(client, name="SQL 综合练习")
    task_id = 1
    resp = client.post(f"/tasks/{task_id}/edit", data={
        "name": "SQL 综合练习", "course": "数据库原理", "due_date": day(2),
        "priority": "低", "status": "待完成", "description": "完成第 4 章全部习题",
    })
    assert resp.status_code == 302
    detail = client.get(f"/tasks/{task_id}").get_data(as_text=True)
    assert "完成第 4 章全部习题" in detail
    assert "prio-低" in detail


# ---------------------------------------------------------------- T4
def test_t4_status_flow_pending_in_progress_done(client):
    new_task(client, name="进程调度实验", course="操作系统")
    for expected in ("进行中", "已完成"):
        resp = client.post("/tasks/1/status", data={"status": expected, "back": "list"})
        assert resp.status_code == 302
        assert f"badge-{expected}" in client.get("/tasks/1").get_data(as_text=True)

    # 持久化：重新建连接再查
    detail = client.get("/tasks/1").get_data(as_text=True)
    assert "badge-已完成" in detail


def test_t4b_illegal_status_ignored(client):
    new_task(client, name="网络实验", course="计算机网络")
    resp = client.post("/tasks/1/status", data={"status": "已删除"})
    assert resp.status_code == 302
    assert "badge-待完成" in client.get("/tasks/1").get_data(as_text=True)


# ---------------------------------------------------------------- T5
def test_t5_filter_by_course_status_priority(client):
    new_task(client, name="数据结构作业甲", course="数据结构", priority="高")
    new_task(client, name="数据结构作业乙", course="数据结构", priority="低", status="已完成")
    new_task(client, name="操作系统作业丙", course="操作系统", priority="高", status="已完成")

    html = client.get("/?course=数据结构").get_data(as_text=True)
    assert "数据结构作业甲" in html and "数据结构作业乙" in html
    assert "操作系统作业丙" not in html

    html = client.get("/?status=已完成").get_data(as_text=True)
    assert "数据结构作业乙" in html and "操作系统作业丙" in html
    assert "数据结构作业甲" not in html

    html = client.get("/?priority=高").get_data(as_text=True)
    assert "数据结构作业甲" in html and "操作系统作业丙" in html
    assert "数据结构作业乙" not in html

    html = client.get("/?course=数据结构&status=已完成&priority=低").get_data(as_text=True)
    assert "数据结构作业乙" in html
    assert "数据结构作业甲" not in html and "操作系统作业丙" not in html


# ---------------------------------------------------------------- T6 / T7
def test_t6_overdue_marked_for_unfinished_task(client):
    new_task(client, name="已逾期作业", due=day(-1))
    html = client.get("/").get_data(as_text=True)
    assert "已逾期" in html


def test_t7_soon_marked_within_three_days(client):
    new_task(client, name="明天到期作业", due=day(1))
    html = client.get("/").get_data(as_text=True)
    assert "即将到期" in html


def test_t7b_completed_task_has_no_due_flag(client):
    new_task(client, name="已完成的旧作业", due=day(-1), status="已完成")
    html = client.get("/").get_data(as_text=True)
    assert "已逾期" not in html


# ---------------------------------------------------------------- T8
def test_t8_stats_total_completed_rate(client):
    for i in range(5):
        status = "已完成" if i < 2 else "待完成"
        new_task(client, name=f"作业{i}", status=status, due=day(i + 1))
    html = client.get("/").get_data(as_text=True)
    assert '<div class="stat-value">5</div>' in html
    assert '<div class="stat-value">2</div>' in html
    assert '<div class="stat-value">40%</div>' in html


def test_t8b_zero_tasks_rate_is_zero_percent(client):
    html = client.get("/").get_data(as_text=True)
    assert '<div class="stat-value">0%</div>' in html


def test_t8c_stats_are_correct_in_service_layer(app):
    with app.app_context():
        from db import get_db
        from services import create_task, validate_task_form
        db = get_db()
        for i in range(5):
            data, errors = validate_task_form({
                "name": f"任务{i}", "course": "软件工程", "due_date": day(i),
                "priority": "中", "status": "已完成" if i < 2 else "待完成",
            })
            assert errors == {}
            create_task(db, data)
        stats = compute_stats(db)
        assert stats == {"total": 5, "completed": 2, "rate": 40}


# ---------------------------------------------------------------- T9
def test_t9_delete_requires_confirmation(client):
    new_task(client, name="待删除任务")
    # 取消：只打开确认页，不提交 → 任务仍在
    confirm = client.get("/tasks/1/delete").get_data(as_text=True)
    assert "确认删除" in confirm
    assert count_tasks(client) == 1
    # 确认：提交删除 → 任务消失
    resp = client.post("/tasks/1/delete")
    assert resp.status_code == 302
    assert count_tasks(client) == 0
    assert client.get("/tasks/1").status_code == 404


# ---------------------------------------------------------------- T10
def test_t10_data_survives_restart(tmp_path):
    db_file = str(tmp_path / "persist.db")
    app1 = create_app({"TESTING": True, "DATABASE": db_file, "SECRET_KEY": "k"})
    client1 = app1.test_client()
    new_task(client1, name="重启后仍存在", course="软件工程")

    # 模拟关闭并重启：新建应用实例，指向同一数据库文件
    app2 = create_app({"TESTING": True, "DATABASE": db_file, "SECRET_KEY": "k"})
    client2 = app2.test_client()
    html = client2.get("/").get_data(as_text=True)
    assert "重启后仍存在" in html
    assert '<div class="stat-value">1</div>' in html


# ---------------------------------------------------------------- 其他边界
def test_description_over_1000_rejected(client):
    resp = new_task(client, description="描" * 1001)
    assert resp.status_code == 400
    assert "任务描述不能超过 1000 个字符" in resp.get_data(as_text=True)


def test_missing_task_returns_404_page(client):
    resp = client.get("/tasks/999")
    assert resp.status_code == 404
    assert "任务不存在或已被删除" in resp.get_data(as_text=True)


def test_unknown_page_returns_404_page(client):
    resp = client.get("/no-such-page")
    assert resp.status_code == 404
