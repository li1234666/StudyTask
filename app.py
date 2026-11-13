"""StudyTask 个人学习任务管理系统 —— Flask 应用入口。

需求依据：《软件工程》实验指导书附录 A（SRS）。
运行：python app.py  或  flask --app app run
"""
import os

from flask import Flask, flash, redirect, render_template, request, url_for

import db as db_module
from services import (
    PRIORITIES,
    STATUSES,
    compute_stats,
    create_task,
    delete_task,
    fetch_courses,
    fetch_task,
    fetch_tasks,
    task_due_flag,
    update_status,
    update_task,
    validate_task_form,
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "studytask-local-dev-key"),
        DATABASE=os.path.join(app.instance_path, "studytask.db"),
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db_module.init_app(app)
    with app.app_context():
        db_module.init_db()

    # ------------------------------------------------------------ 页面路由
    @app.route("/")
    def index():
        """任务列表 + 统计卡片 + 组合筛选（FR-02、FR-06、FR-08）。"""
        filters = {
            "course": (request.args.get("course") or "").strip(),
            "status": (request.args.get("status") or "").strip(),
            "priority": (request.args.get("priority") or "").strip(),
        }
        rows = fetch_tasks(db_module.get_db(), filters)
        stats = compute_stats(db_module.get_db())
        courses = fetch_courses(db_module.get_db())
        tasks = [
            {"row": row, "flag": task_due_flag(row)} for row in rows
        ]
        has_filter = any(filters.values())
        return render_template(
            "index.html",
            tasks=tasks,
            stats=stats,
            filters=filters,
            courses=courses,
            priorities=PRIORITIES,
            statuses=STATUSES,
            has_filter=has_filter,
        )

    @app.route("/tasks/new", methods=("GET", "POST"))
    def task_new():
        """新建任务，含必填项与长度、日期格式校验（FR-01）。"""
        form = {"name": "", "course": "", "description": "", "due_date": "",
                "priority": "中", "status": "待完成"}
        if request.method == "POST":
            form.update({k: request.form.get(k, "") for k in form})
            data, errors = validate_task_form(request.form)
            if errors:
                return render_template(
                    "form.html", mode="create", form=data, errors=errors,
                    priorities=PRIORITIES, statuses=STATUSES
                ), 400
            task_id = create_task(db_module.get_db(), data)
            flash("任务已创建。", "success")
            return redirect(url_for("task_detail", task_id=task_id))
        return render_template(
            "form.html", mode="create", form=form, errors={},
            priorities=PRIORITIES, statuses=STATUSES
        )

    @app.route("/tasks/<int:task_id>")
    def task_detail(task_id):
        """任务详情页（FR-02）。"""
        task = fetch_task(db_module.get_db(), task_id)
        if task is None:
            return render_template("error.html", code=404,
                                   message="任务不存在或已被删除。"), 404
        return render_template("detail.html", task=task,
                               flag=task_due_flag(task),
                               statuses=STATUSES, priorities=PRIORITIES)

    @app.route("/tasks/<int:task_id>/edit", methods=("GET", "POST"))
    def task_edit(task_id):
        """编辑任务各字段（FR-03）。"""
        task = fetch_task(db_module.get_db(), task_id)
        if task is None:
            return render_template("error.html", code=404,
                                   message="任务不存在或已被删除。"), 404

        form = {key: task[key] for key in
                ("name", "course", "description", "due_date", "priority", "status")}
        if request.method == "POST":
            form.update({k: request.form.get(k, "") for k in form})
            data, errors = validate_task_form(request.form)
            if errors:
                return render_template(
                    "form.html", mode="edit", form=data, errors=errors,
                    task_id=task_id, priorities=PRIORITIES, statuses=STATUSES
                ), 400
            update_task(db_module.get_db(), task_id, data)
            flash("任务已保存。", "success")
            return redirect(url_for("task_detail", task_id=task_id))
        return render_template(
            "form.html", mode="edit", form=form, errors={},
            task_id=task_id, priorities=PRIORITIES, statuses=STATUSES
        )

    @app.route("/tasks/<int:task_id>/status", methods=("POST",))
    def task_status(task_id):
        """调整任务状态：待完成 / 进行中 / 已完成（FR-05）。"""
        task = fetch_task(db_module.get_db(), task_id)
        if task is None:
            return render_template("error.html", code=404,
                                   message="任务不存在或已被删除。"), 404
        status = (request.form.get("status") or "").strip()
        if status not in STATUSES:
            flash("状态值不合法，未做修改。", "error")
            return redirect(url_for("task_detail", task_id=task_id))
        update_status(db_module.get_db(), task_id, status)
        flash(f"状态已更新为「{status}」。", "success")
        back = request.form.get("back")
        if back == "list":
            return redirect(url_for("index"))
        return redirect(url_for("task_detail", task_id=task_id))

    @app.route("/tasks/<int:task_id>/delete", methods=("GET", "POST"))
    def task_delete(task_id):
        """删除任务：先进入确认页，确认后才真正删除（FR-04）。"""
        task = fetch_task(db_module.get_db(), task_id)
        if task is None:
            return render_template("error.html", code=404,
                                   message="任务不存在或已被删除。"), 404
        if request.method == "POST":
            delete_task(db_module.get_db(), task_id)
            flash("任务已删除。", "success")
            return redirect(url_for("index"))
        return render_template("confirm_delete.html", task=task)

    # ------------------------------------------------------------ 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404,
                               message="页面不存在。"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("error.html", code=500,
                               message="服务器内部错误，请检查输入后重试。"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
