"""生成实验一答辩演示文稿：实验一答辩演示.pptx"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent
SHOT = OUT / "screenshots"

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x24, 0x5C, 0x9C)
LIGHT = RGBColor(0xF2, 0xF5, 0xF9)
GREY = RGBColor(0x5A, 0x67, 0x78)
DARK = RGBColor(0x22, 0x2B, 0x36)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0xC0, 0x39, 0x2B)
FONT = "微软雅黑"

SW, SH = Inches(13.333), Inches(7.5)


def style_run(run, size=16, bold=False, color=DARK, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", font)


def textbox(slide, left, top, width, height, text, size=16, bold=False, color=DARK,
            align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line=1.25):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line_text in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        r = p.add_run()
        r.text = line_text
        style_run(r, size, bold, color)
    return box


def rect(slide, left, top, width, height, fill, line=None, radius=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(0.75)
    shp.shadow.inherit = False
    return shp


def title_bar(slide, title, subtitle=None):
    rect(slide, 0, 0, SW, Inches(0.1), NAVY)
    textbox(slide, Inches(0.75), Inches(0.45), Inches(11.8), Inches(0.6), title,
            size=28, bold=True, color=NAVY)
    rect(slide, Inches(0.78), Inches(1.12), Inches(0.55), Inches(0.05), BLUE)
    if subtitle:
        textbox(slide, Inches(0.78), Inches(1.24), Inches(11.5), Inches(0.4), subtitle,
                size=14, color=GREY)


def footer(slide, page):
    textbox(slide, Inches(0.78), Inches(6.95), Inches(9.0), Inches(0.3),
            "《软件工程》实验一 · StudyTask", size=10, color=GREY)
    textbox(slide, Inches(11.9), Inches(6.95), Inches(0.7), Inches(0.3), str(page),
            size=10, color=GREY, align=PP_ALIGN.RIGHT)


def bullets(slide, left, top, width, height, items, size=15, gap=10, color=DARK):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_top = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        p.line_spacing = 1.3
        r = p.add_run()
        r.text = "· " + item
        style_run(r, size, False, color)
    return box


def add_table(slide, left, top, width, rows, col_widths, header=True, font_size=11,
              row_height=0.34):
    shape = slide.shapes.add_table(len(rows), len(rows[0]), left, top, width,
                                   Inches(row_height * len(rows)))
    table = shape.table
    table.first_row = header
    for i, w in enumerate(col_widths):
        table.columns[i].width = Inches(w)
    for r, row in enumerate(rows):
        table.rows[r].height = Inches(row_height)
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY if (header and r == 0) else WHITE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c < len(row) - 1 else PP_ALIGN.CENTER
            run = p.add_run()
            run.text = str(value)
            style_run(run, font_size, header and r == 0,
                      WHITE if (header and r == 0) else DARK)
    return table


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
blank = prs.slide_layouts[6]

# ------------------------------------------------------------------ 1 封面
s = prs.slides.add_slide(blank)
rect(s, 0, 0, SW, SH, NAVY)
rect(s, Inches(0.9), Inches(2.15), Inches(0.09), Inches(1.75), BLUE)
textbox(s, Inches(1.15), Inches(1.95), Inches(11.0), Inches(0.9),
        "实验一：AI 驱动的个人学习任务管理系统", size=38, bold=True, color=WHITE)
textbox(s, Inches(1.15), Inches(2.85), Inches(11.0), Inches(0.6),
        "StudyTask · 需求文档驱动的 AI 自动开发与人工验收", size=18, color=RGBColor(0xC9, 0xD8, 0xE8))
textbox(s, Inches(1.15), Inches(4.35), Inches(11.0), Inches(0.4),
        "计算机科学与技术 2024 级　　班级：　　　　　学号：　　　　　姓名：　　　　　",
        size=14, color=RGBColor(0xC9, 0xD8, 0xE8))
textbox(s, Inches(1.15), Inches(4.85), Inches(11.0), Inches(0.4),
        "提交日期：2026-11-10　　指导教师：林卫中、赵丽萍",
        size=14, color=RGBColor(0xC9, 0xD8, 0xE8))
notes(s, "各位老师好，我汇报的是实验一：AI 驱动的个人学习任务管理系统 StudyTask。"
         "这个实验的核心问题是：AI 能否按照给定的需求文档开发出可验收的软件，"
         "以及哪些错误必须由人来发现。项目采用 Flask 加 SQLite，单用户本地运行。")

# ------------------------------------------------------------------ 2 目标与边界
s = prs.slides.add_slide(blank)
title_bar(s, "实验目标与需求边界", "先读需求、再交给 AI：范围清楚，验收才有依据")
textbox(s, Inches(0.78), Inches(1.85), Inches(5.4), Inches(0.35), "实验目标",
        size=18, bold=True, color=NAVY)
bullets(s, Inches(0.78), Inches(2.32), Inches(5.4), Inches(3.6), [
    "掌握把完整 SRS 转化为 AI 开发任务的流程",
    "产出可本地运行、可复现验收的 Web 应用",
    "走通“运行、测试、缺陷反馈、修复”闭环",
    "分清 AI 的编码工作与人的验证责任",
], size=15, gap=12)

rect(s, Inches(6.55), Inches(1.85), Inches(6.0), Inches(2.05), LIGHT, line=RGBColor(0xD6, 0xDE, 0xE8))
textbox(s, Inches(6.85), Inches(2.0), Inches(5.4), Inches(0.3), "本项目实现（P1-F01 至 F07）",
        size=16, bold=True, color=BLUE)
textbox(s, Inches(6.85), Inches(2.4), Inches(5.4), Inches(1.4),
        "任务增删改查　|　三种状态　|　课程/状态/优先级组合筛选\n"
        "逾期与即将到期提醒　|　总数与完成率统计　|　SQLite 本地持久化",
        size=13.5, color=DARK, line=1.4)

rect(s, Inches(6.55), Inches(4.1), Inches(6.0), Inches(1.5), RGBColor(0xFD, 0xEA, 0xEA),
     line=RGBColor(0xE6, 0xB8, 0xB8))
textbox(s, Inches(6.85), Inches(4.25), Inches(5.4), Inches(0.3), "明确不实现（范围外）",
        size=16, bold=True, color=ACCENT)
textbox(s, Inches(6.85), Inches(4.65), Inches(5.4), Inches(0.8),
        "账号注册、多用户权限、邮件/短信推送\n第三方日历同步、移动端 App、云部署",
        size=13.5, color=DARK, line=1.4)

textbox(s, Inches(0.78), Inches(5.95), Inches(11.8), Inches(0.4),
        "验收依据：指导书 2.5 节 T1—T10 十条用例 + 附录 A 的 FR-01 至 FR-10",
        size=14, bold=True, color=NAVY)
footer(s, 2)
notes(s, "先看目标：这个实验不只是写一个能跑的页面，而是完整走一遍需求驱动的开发流程。"
         "我首先划清了边界：只做任务管理、状态、筛选、提醒和统计这七项功能，"
         "拒绝登录、多人协作、推送等范围外功能，避免项目膨胀。"
         "验收依据就是指导书里的十条用例和附录 A 的十条功能需求。")

# ------------------------------------------------------------------ 3 系统结构
s = prs.slides.add_slide(blank)
title_bar(s, "系统结构与技术选型", "规则从页面里剥离：路由只收发，业务层可单独测试")

layers = [
    ("浏览器页面（原生 HTML / CSS，无前端框架）", Inches(1.2), Inches(1.65), Inches(4.3)),
    ("路由层　app.py　表单收发、页面渲染、跳转", Inches(1.2), Inches(2.6), Inches(4.3)),
    ("业务层　services.py　校验、筛选、到期判定、统计", Inches(1.2), Inches(3.55), Inches(4.3)),
    ("数据层　db.py　连接管理、建表、CRUD", Inches(1.2), Inches(4.5), Inches(4.3)),
    ("SQLite　instance/studytask.db", Inches(1.2), Inches(5.45), Inches(4.3)),
]
for text, left, top, width in layers:
    rect(s, left, top, width, Inches(0.72), LIGHT, line=RGBColor(0xC7, 0xD4, 0xE3), radius=True)
    textbox(s, left + Inches(0.18), top + Inches(0.16), width - Inches(0.3), Inches(0.4),
            text, size=13, color=DARK)

for y in (2.37, 3.32, 4.27, 5.22):
    textbox(s, Inches(3.15), Inches(y), Inches(0.5), Inches(0.3), "↓",
            size=18, color=BLUE, align=PP_ALIGN.CENTER)

rect(s, Inches(5.95), Inches(1.65), Inches(6.55), Inches(2.6), WHITE, line=RGBColor(0xD6, 0xDE, 0xE8))
textbox(s, Inches(6.2), Inches(1.8), Inches(6.0), Inches(0.35), "技术选型（均满足最低要求）",
        size=16, bold=True, color=NAVY)
add_table(s, Inches(6.2), Inches(2.25), Inches(6.0), [
    ["项目", "选型"],
    ["语言 / 环境", "Python 3.13.16 + venv"],
    ["Web 框架", "Flask 3.1.3"],
    ["数据库", "SQLite 3（标准库 sqlite3）"],
    ["自动化测试", "pytest 9.2.0"],
    ["版本控制", "Git（已提交，标签 baseline-v1）"],
], [1.8, 4.2], font_size=11.5, row_height=0.33)

rect(s, Inches(5.95), Inches(4.5), Inches(6.55), Inches(1.7), LIGHT, line=RGBColor(0xD6, 0xDE, 0xE8))
textbox(s, Inches(6.2), Inches(4.65), Inches(6.0), Inches(0.35), "数据表 tasks（单表，8 个字段）",
        size=16, bold=True, color=NAVY)
textbox(s, Inches(6.2), Inches(5.05), Inches(6.05), Inches(1.0),
        "name / course / description / due_date /\npriority / status / created_at / updated_at",
        size=13, color=GREY, line=1.4)
footer(s, 3)
notes(s, "系统分四层：页面只负责展示，app.py 只负责接收表单和跳转，"
         "真正规则都在 services.py，数据访问在 db.py。"
         "这样剥离的好处是规则可以单独写单元测试，后面改规则不用动路由。"
         "数据只有一张 tasks 表，八个字段，首次启动自动建表。")

# ------------------------------------------------------------------ 4 核心功能
s = prs.slides.add_slide(blank)
title_bar(s, "核心功能实现", "七项功能逐条对应需求编号，不留“顺便实现”的多余功能")
add_table(s, Inches(0.78), Inches(1.75), Inches(11.75), [
    ["编号", "功能", "关键实现", "对应需求"],
    ["P1-F01", "新建任务", "名称/课程/日期必填校验，错误回填不写库", "FR-01"],
    ["P1-F02", "查看、编辑、删除", "列表 + 详情页；删除走服务端确认页", "FR-02/03/04"],
    ["P1-F03", "任务状态", "待完成 → 进行中 → 已完成，写库持久保存", "FR-05"],
    ["P1-F04", "组合筛选", "课程、状态、优先级任意组合，空值不限", "FR-06"],
    ["P1-F05", "逾期 / 即将到期", "未完成任务：早于今天为逾期，3 天内为即将到期", "FR-07"],
    ["P1-F06", "基础统计", "总数、已完成数、完成率；总数为 0 显示 0%", "FR-08"],
    ["P1-F07", "本地持久化", "SQLite 文件，重启后数据不丢", "FR-09"],
], [1.2, 2.5, 6.5, 1.55], font_size=12, row_height=0.52)
textbox(s, Inches(0.78), Inches(5.9), Inches(11.75), Inches(0.8),
        "界面全中文，错误以字段级提示呈现，非法输入不会造成应用崩溃（FR-10）。",
        size=14, color=GREY)
footer(s, 4)
notes(s, "这张表是功能对照：每一项功能都能追到需求编号。"
         "重点说两个：删除不是弹窗确认，而是先进入确认页、提交后才真正删除，"
         "这样确认流程可以被截图和自动化测试验证；"
         "到期提醒只对未完成任务生效，这一点在需求第七十九条有明确要求。")

# ------------------------------------------------------------------ 5 关键规则 + 截图
s = prs.slides.add_slide(blank)
title_bar(s, "关键规则：逾期判定与页面反馈", "以“今天”为界，只提醒还没做完的事")
bullets(s, Inches(0.78), Inches(1.7), Inches(6.6), Inches(3.9), [
    "逾期：未完成且截止日期早于今天 → 显示“已逾期”",
    "即将到期：未完成且今天起 3 天内到期 → 显示“即将到期”",
    "已完成任务不显示任何到期提醒，避免已完成事项干扰判断",
    "统计按全库计算：总数 5、已完成 2 → 完成率 40%",
    "筛选与统计同时呈现，改条件后列表即时收敛",
], size=14.5, gap=12)
textbox(s, Inches(0.78), Inches(5.5), Inches(6.6), Inches(1.0),
        "上图可见：昨日到期的链表报告标红“已逾期”，两条 3 天内\n"
        "到期的任务标黄“即将到期”，已完成任务提醒列为“—”。",
        size=12.5, color=GREY, line=1.35)
pic = s.shapes.add_picture(str(SHOT / "01-list.png"), Inches(8.0), Inches(1.65), width=Inches(4.3))
textbox(s, Inches(8.0), Inches(1.65 + 4.3 * 666 / 506), Inches(4.3), Inches(0.3),
        "图 1　任务列表与统计卡片", size=11, color=GREY, align=PP_ALIGN.CENTER)
footer(s, 5)
notes(s, "这里看实际界面。五条任务里，昨天到期的没完成，标了红色已逾期；"
         "明后天到期的两条标了黄色即将到期；两条已完成的不给任何提醒。"
         "统计卡片显示总数五、完成二、完成率百分之四十，和需求一致。")

# ------------------------------------------------------------------ 6 测试与验收
s = prs.slides.add_slide(blank)
title_bar(s, "测试与验收结果", "T1—T10 全部通过，自动化用例 18 条可复现")

cards = [("10 / 10", "验收用例通过", "T1 至 T10"), ("18 / 18", "pytest 用例通过", "含边界场景"),
         ("0", "重启后数据丢失", "FR-09 实测")]
x = 0.78
for value, label, sub in cards:
    rect(s, Inches(x), Inches(1.7), Inches(3.1), Inches(1.35), LIGHT, line=RGBColor(0xD6, 0xDE, 0xE8))
    textbox(s, Inches(x + 0.15), Inches(1.82), Inches(2.8), Inches(0.55), value,
            size=26, bold=True, color=BLUE)
    textbox(s, Inches(x + 0.15), Inches(2.4), Inches(2.8), Inches(0.3), label, size=12.5, color=DARK)
    textbox(s, Inches(x + 0.15), Inches(2.68), Inches(2.8), Inches(0.3), sub, size=10.5, color=GREY)
    x += 3.35

bullets(s, Inches(0.78), Inches(3.35), Inches(6.9), Inches(3.0), [
    "T1 新建 / T2 空名称拦截 / T3 编辑保留 / T4 状态流转",
    "T5 组合筛选 / T6 逾期 / T7 即将到期 / T8 统计 5·2·40%",
    "T9 删除取消与确认 / T10 重启后数据仍在",
    "边界补充：2026-02-30 非法日期、101 字名称、1001 字描述、404 页面",
    "真实重启验证：停止进程再启动，列表、筛选与统计不变",
], size=13.5, gap=8)
add_table(s, Inches(8.1), Inches(3.45), Inches(4.4), [
    ["命令", "结果"],
    ["python -m pytest -v", "18 passed"],
    ["python app.py", "127.0.0.1:5000"],
], [2.6, 1.8], font_size=11, row_height=0.38)
footer(s, 6)
notes(s, "验收结果是十条用例全过，自动化测试十八条全过。"
         "除了正常流程，还测了非法日期、超长字段、非法状态和不存在的页面。"
         "T10 是真实重启验证：把服务进程停掉再启动，数据还在，说明持久化是真的。")

# ------------------------------------------------------------------ 7 问题与修复
s = prs.slides.add_slide(blank)
title_bar(s, "三个真实问题与修复", "都不是语法错误，而是规则细节与验证方式的问题")

problems = [
    ("问题 1　日期只判空、不判真实性", "输入 2026-02-30 也能保存成功",
     "要求追加日期解析校验；修复后返回 400 且不写库"),
    ("问题 2　已完成任务仍被标“已逾期”", "首版逾期判定只比较日期，忽略状态",
     "把状态判断加入到期标记，并补用例锁定行为"),
    ("问题 3　测试断言用了不可区分数据", "任务名 A/B/C，字母 C 命中 HTML 文本",
     "改用中文可区分任务名，18 条用例恢复全部通过"),
]
y = 1.7
for title, symptom, fix in problems:
    rect(s, Inches(0.78), Inches(y), Inches(11.7), Inches(1.42), LIGHT, line=RGBColor(0xD6, 0xDE, 0xE8))
    textbox(s, Inches(1.0), Inches(y + 0.14), Inches(5.2), Inches(0.35), title,
            size=15, bold=True, color=NAVY)
    textbox(s, Inches(1.0), Inches(y + 0.6), Inches(5.1), Inches(0.6), "现象：" + symptom,
            size=12.5, color=ACCENT, line=1.3)
    textbox(s, Inches(6.3), Inches(y + 0.14), Inches(5.9), Inches(0.35), "人工判断与修复",
            size=13, bold=True, color=BLUE)
    textbox(s, Inches(6.3), Inches(y + 0.55), Inches(5.9), Inches(0.7), fix,
            size=12.5, color=DARK, line=1.3)
    y += 1.72
textbox(s, Inches(0.78), Inches(6.55), Inches(11.7), Inches(0.35),
        "另有模板标签闭合笔误与后台启动参数被拆分两处问题，均在验收前发现并修正。",
        size=11.5, color=GREY)
footer(s, 7)
notes(s, "三个问题都不是跑不起来，而是跑起来了但不符合需求。"
         "第一个是日期只判空不判真假；第二个是已完成任务还标逾期，直接违反需求第七条；"
         "第三个其实是测试本身的问题：任务名用 A、B、C，字母 C 和页面 HTML 撞了，导致误报。"
         "这些靠 AI 自己发现不了，只能人对着需求逐条核对。")

# ------------------------------------------------------------------ 8 反思
s = prs.slides.add_slide(blank)
title_bar(s, "分工与反思", "AI 完成“能运行的代码”，人负责“是否真的合格”")
rect(s, Inches(0.78), Inches(1.75), Inches(5.5), Inches(3.9), LIGHT, line=RGBColor(0xD6, 0xDE, 0xE8))
textbox(s, Inches(1.0), Inches(1.9), Inches(5.0), Inches(0.35), "AI 承担", size=17, bold=True, color=BLUE)
bullets(s, Inches(1.0), Inches(2.35), Inches(5.0), Inches(3.0), [
    "项目骨架与三层结构",
    "数据表、路由与页面模板",
    "校验、筛选、统计函数",
    "pytest 用例初稿",
], size=13.5, gap=8)

rect(s, Inches(6.55), Inches(1.75), Inches(5.95), Inches(3.9), RGBColor(0xE9, 0xF3, 0xEC),
     line=RGBColor(0xB7, 0xE4, 0xC7))
textbox(s, Inches(6.8), Inches(1.9), Inches(5.4), Inches(0.35), "人工决策", size=17, bold=True,
        color=RGBColor(0x27, 0x67, 0x49))
bullets(s, Inches(6.8), Inches(2.35), Inches(5.5), Inches(3.0), [
    "范围裁剪：拒绝范围外功能",
    "规则核对：对照 FR-07 修正提醒逻辑",
    "确认流程改造：否决前端弹窗",
    "测试断言有效性、启动真实性验证",
], size=13.5, gap=8)

rect(s, Inches(0.78), Inches(5.85), Inches(11.7), Inches(0.75), NAVY, radius=True)
textbox(s, Inches(1.05), Inches(6.02), Inches(11.2), Inches(0.45),
        "结论：AI 的输出始终是待验证产物，验收责任仍在开发者；需求细节只能由人守住。",
        size=14.5, bold=True, color=WHITE)
footer(s, 8)
notes(s, "最后是分工。AI 把规范变成结构完整的代码，速度快、覆盖全；"
         "但范围边界、规则细节、测试是否有判断力、服务是否真的起来，这些都得人来定。"
         "一句话总结：AI 能交付“能运行的代码”，交付不了“合格的软件”。")

# ------------------------------------------------------------------ 9 演示路径
s = prs.slides.add_slide(blank)
title_bar(s, "现场演示路径", "按验收用例顺序演示，每一步都能当场核对结果")
steps = ["新建一条明日到期的高优先级任务", "名称为空提交，观察校验提示",
         "按课程 / 状态 / 优先级筛选", "新增昨日到期任务，确认逾期标识",
         "将任务状态改为已完成，观察统计变化", "删除任务：先取消，再确认",
         "重启服务，刷新页面确认数据仍在"]
y = 1.7
for i, step in enumerate(steps, start=1):
    rect(s, Inches(0.78), Inches(y), Inches(0.55), Inches(0.55), NAVY, radius=True)
    textbox(s, Inches(0.78), Inches(y + 0.1), Inches(0.55), Inches(0.35), str(i),
            size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    textbox(s, Inches(1.55), Inches(y + 0.12), Inches(9.8), Inches(0.4), step, size=14, color=DARK)
    y += 0.68

rect(s, Inches(11.1), Inches(1.7), Inches(1.5), Inches(4.6), LIGHT, line=RGBColor(0xD6, 0xDE, 0xE8))
textbox(s, Inches(11.2), Inches(1.85), Inches(1.3), Inches(4.3),
        "启 动\n\npython\napp.py\n\n访 问\n\n127.0.0.1\n:5000",
        size=10.5, color=GREY, line=1.3, align=PP_ALIGN.CENTER)
textbox(s, Inches(0.78), Inches(6.5), Inches(11.0), Inches(0.35), "谢谢各位老师，请批评指正。",
        size=14, bold=True, color=NAVY)
footer(s, 9)
notes(s, "最后是演示路径，按验收用例顺序来：新建、校验、筛选、逾期、状态、删除确认，"
         "最后重启服务验证持久化。启动命令就是 python app.py，访问本机五千端口即可。"
         "我的汇报结束，请老师批评指正。")

prs.save(str(OUT / "实验一答辩演示.pptx"))
print("saved pptx")
