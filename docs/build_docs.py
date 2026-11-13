"""生成实验一交付文档：实验报告.docx、需求验收表.docx"""
import os
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = Path(__file__).resolve().parent
SHOT = OUT / "screenshots"

CN_BODY = "宋体"
CN_HEAD = "黑体"
EN_FONT = "Times New Roman"


def set_run_font(run, cn=CN_BODY, size=12, bold=False, color=None):
    run.font.name = EN_FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cn)
    rfonts.set(qn("w:ascii"), EN_FONT)
    rfonts.set(qn("w:hAnsi"), EN_FONT)
    run.font.color.rgb = color or RGBColor(0, 0, 0)


def patch_style(style, cn, size, bold=False, line=1.5, before=0, after=4,
                align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_chars=0):
    style.font.name = EN_FONT
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), cn)
    rfonts.set(qn("w:ascii"), EN_FONT)
    rfonts.set(qn("w:hAnsi"), EN_FONT)
    pf = style.paragraph_format
    pf.line_spacing = line
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.alignment = align
    if indent_chars:
        pf.first_line_indent = Pt(size * indent_chars)


def setup_section(doc, landscape=False):
    for s in doc.sections:
        if landscape:
            s.orientation = WD_ORIENT.LANDSCAPE
            s.page_width, s.page_height = Cm(29.7), Cm(21.0)
        else:
            s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.top_margin = s.bottom_margin = Cm(2.5)
        s.left_margin = s.right_margin = Cm(2.5)


def add_page_number(doc):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = "PAGE"
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        run._r.append(fld_begin)
        run._r.append(instr)
        run._r.append(fld_end)
        set_run_font(run, size=10.5)


def body(doc, text, indent=True):
    p = doc.add_paragraph(style="Normal")
    run = p.add_run(text)
    set_run_font(run, CN_BODY, 12)
    if not indent:
        p.paragraph_format.first_line_indent = Pt(0)
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    run = p.add_run(text)
    set_run_font(run, CN_HEAD, 14 if level == 1 else 12, bold=True)
    p.paragraph_format.keep_with_next = True
    return p


def caption(doc, text):
    p = doc.add_paragraph(style="Caption")
    run = p.add_run(text)
    set_run_font(run, CN_BODY, 10.5)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1
    return p


def shade(cell, color="F2F2F2"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "808080")
        borders.append(el)
    tblPr.append(borders)


def add_table(doc, headers, rows, widths, aligns=None, font_size=10.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    hdr = table.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        cell.width = Cm(widths[i])
        shade(cell)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(text), CN_BODY, font_size, bold=True)
    for row in rows:
        cells = table.add_row()
        trPr = cells._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        cant.set(qn("w:val"), "true")
        trPr.append(cant)
        for i, text in enumerate(row):
            cell = cells.cells[i]
            cell.width = Cm(widths[i])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = (aligns[i] if aligns else WD_ALIGN_PARAGRAPH.LEFT)
            p.paragraph_format.line_spacing = 1
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            set_run_font(p.add_run(text), CN_BODY, font_size)
    return table


# ==================================================================== 实验报告
def build_report():
    doc = Document()
    setup_section(doc)
    patch_style(doc.styles["Normal"], CN_BODY, 12, line=1.5, after=4, indent_chars=2)
    patch_style(doc.styles["Heading 1"], CN_HEAD, 14, bold=True, line=1.5, before=10, after=5,
                align=WD_ALIGN_PARAGRAPH.LEFT, indent_chars=0)
    patch_style(doc.styles["Heading 2"], CN_HEAD, 12, bold=True, line=1.5, before=8, after=4,
                align=WD_ALIGN_PARAGRAPH.LEFT, indent_chars=0)
    patch_style(doc.styles["Caption"], CN_BODY, 10.5, line=1, before=4, after=4,
                align=WD_ALIGN_PARAGRAPH.CENTER, indent_chars=0)
    add_page_number(doc)

    # 标题
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    set_run_font(p.add_run("《软件工程》实验一实验报告"), CN_HEAD, 18, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    set_run_font(p.add_run("StudyTask 个人学习任务管理系统"), CN_BODY, 12)

    add_table(doc,
              ["班级", "学号", "姓名"],
              [["　　　　　　", "　　　　　　", "　　　　　　"]],
              [4.6, 4.6, 4.6],
              aligns=[WD_ALIGN_PARAGRAPH.CENTER] * 3, font_size=10.5)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    set_run_font(p.add_run("提交日期：2026-11-10　　指导教师：林卫中、赵丽萍"), CN_BODY, 10.5)

    heading(doc, "一、实验目标与需求范围")
    body(doc, "本实验按教师提供的需求规格说明书（指导书附录 A）完成一个可本地运行的单用户学习任务管理 Web 系统，"
              "用于记录课程作业、实验与考试准备事项。实验要验证的核心问题是：AI 能否按照需求开发出可验收的软件，"
              "以及哪些错误必须由人发现。")
    body(doc, "实现范围限定为任务增删改查、任务状态、组合筛选、逾期提示与基础统计（P1-F01 至 P1-F07）。"
              "不实现账号注册、多用户权限、邮件与短信推送、第三方日历同步、移动端应用和云部署。"
              "验收依据为 2.5 节 T1 至 T10 十条最低验收用例，以及附录 A 中 FR-01 至 FR-10 的功能性需求。")

    heading(doc, "二、实现方案")
    body(doc, "开发环境为 Windows 11、Python 3.13.16、venv 虚拟环境、Flask 3.1.3、SQLite（标准库 sqlite3）与 pytest 9.2.0，"
              "前端使用原生 HTML 与 CSS，未引入前端框架。系统采用三层结构：路由层 app.py 只负责接收表单、渲染页面与跳转；"
              "业务层 services.py 集中字段校验、筛选、逾期判定与统计；数据层 db.py 管理连接与建表。"
              "规则从页面代码中剥离后，测试可以直接针对业务函数，修改规则也不必改动路由。")
    body(doc, "数据设计为单表 tasks，字段包括任务名称（1 至 100 字）、所属课程（1 至 60 字）、任务描述（不超过 1000 字）、"
              "截止日期（YYYY-MM-DD）、优先级（高、中、低，默认中）、状态（待完成、进行中、已完成，默认待完成），"
              "以及自动记录的创建时间与更新时间；课程、状态、优先级建立索引。数据库文件为 instance/studytask.db，首次启动自动建表。")
    body(doc, "关键规则实现如下。校验在写入前完成，名称或课程为空、截止日期非法时返回错误提示且不写库，页面保留已填内容。"
              "逾期与即将到期只对未完成任务生效：截止日期早于今天标记“已逾期”，今天起 3 天内标记“即将到期”，"
              "已完成任务不显示任何到期提醒。筛选按课程、状态、优先级组合，空条件表示不限。"
              "统计按全库计算总数、完成数与完成率，总数为 0 时完成率显示 0%。"
              "删除采用服务端二次确认页：先进入确认页，提交后才执行删除，取消则原任务保留，使确认流程可被截图与自动化测试验证。")

    heading(doc, "三、实施过程")
    body(doc, "工作按“读需求、搭骨架、写规则、写测试、部署验收”推进。AI 承担了项目结构、数据表、路由与模板、"
              "校验与统计函数以及 pytest 用例的初稿；本人承担范围裁剪（拒绝登录、邮件提醒等范围外功能）、"
              "规则核对（对照 FR-07 修正已完成任务仍显示逾期的问题）、确认流程改造（否决前端弹窗，改为服务端确认页）"
              "以及启动方式的真实性验证。")
    body(doc, "版本管理方面，仓库已初始化 Git 并完成首次提交（commit 0bc285e，标签 baseline-v1），"
              ".gitignore 已排除虚拟环境、数据库文件与缓存；推送到 GitHub 的命令见 README 与 SUBMIT.md。"
              "关键提示词、AI 产出与人工判断记录在仓库根目录的 AI_DEV_LOG.md 中，共记录 9 条代表性协作事件。")

    heading(doc, "四、测试结果")
    body(doc, "自动化测试共 18 条，覆盖 T1 至 T10 以及非法日期、超长字段、非法状态值、404 页面、零任务统计等边界情况，"
              "执行命令 python -m pytest -v 的结果为 18 passed。表 1 为验收用例结论摘要，完整记录见同目录《需求验收表》。", indent=False)

    caption(doc, "表 1　T1 至 T10 验收用例结论摘要")
    add_table(doc,
              ["用例", "需求编号", "测试要点", "结论"],
              [["T1", "FR-01", "新建课程“数据结构”、明日截止、高优先级任务", "通过"],
               ["T2", "FR-01", "名称为空提交，提示错误且不产生脏数据", "通过"],
               ["T3", "FR-03", "修改任务描述与优先级，刷新后保留", "通过"],
               ["T4", "FR-05", "待完成→进行中→已完成逐次更新并持久保存", "通过"],
               ["T5", "FR-06", "按课程、状态、优先级及组合条件筛选", "通过"],
               ["T6", "FR-07", "昨日到期未完成任务显示“已逾期”", "通过"],
               ["T7", "FR-07", "明日到期未完成任务显示“即将到期”", "通过"],
               ["T8", "FR-08", "创建 5 项完成 2 项，总数 5、完成数 2、完成率 40%", "通过"],
               ["T9", "FR-04", "删除前取消不删除，确认后删除", "通过"],
               ["T10", "FR-09", "停止并重启服务后，已保存数据仍可查询", "通过"]],
              [1.6, 2.6, 9.6, 2.2],
              aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER,
                      WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER], font_size=10.5)

    body(doc, "另外做了一次真实运行验证。通过浏览器表单录入 5 条任务，其中 1 条昨日到期未完成，页面显示“已逾期”；"
              "2 条 3 天内到期，显示“即将到期”；完成后统计为总数 5、已完成 2、完成率 40%。"
              "停止服务进程并重新启动后，列表、筛选与统计结果均保持不变，满足 FR-09 的持久化要求。")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run1 = p.add_run()
    run1.add_picture(str(SHOT / "01-list.png"), width=Cm(6.6))
    p.add_run("　")
    run2 = p.add_run()
    run2.add_picture(str(SHOT / "02-validation.png"), width=Cm(6.6))
    caption(doc, "图 1　任务列表（含统计与到期提醒）与表单校验提示")

    heading(doc, "五、问题与反思")
    body(doc, "第一个问题是日期真实性校验缺失。AI 生成的校验只判断截止日期是否为空，未验证日期是否存在，"
              "输入 2026-02-30 仍可保存成功。用该输入实测发现后，要求追加日期解析校验，"
              "修复后非法日期返回 400，数据库无新增记录。")
    body(doc, "第二个问题是已完成任务被误标逾期。首版逾期判定只比较日期，已完成的过期任务仍显示“已逾期”，与 FR-07 相冲突。"
              "将状态判断加入到期标记逻辑后，只对未完成任务提示，并补充 T7b 用例锁定该行为，防止回归。")
    body(doc, "第三个问题是测试断言用了不可区分的数据。筛选用例最初用单字母任务名 A、B、C，"
              "其中字母 C 命中了页面 HTML 文本，导致用例误报失败。排查确认这不是功能缺陷，"
              "改用中文可区分任务名后 18 条用例全部通过。这说明断言必须使用能唯一区分的数据，否则测试会失去判断力。")
    body(doc, "反思来看，AI 擅长把规范快速转成结构完整的代码，但对规则细节与“是否真的跑起来”缺乏判断力。"
              "本次三个缺陷都不是语法错误，而是需求细节、规则边界与验证方式的问题，只能靠人对照 SRS 逐条核对、"
              "用可复现的测试与真实运行记录来发现。AI 输出始终是待验证的产物，验收责任仍在开发者一方。")

    heading(doc, "六、附录：运行说明")
    body(doc, "在项目目录下创建虚拟环境并安装依赖（pip install -r requirements.txt），执行 python app.py 后"
              "浏览器访问 http://127.0.0.1:5000 即可使用；自动化测试执行 python -m pytest -v。"
              "源代码、README、AI_DEV_LOG.md 与测试用例均在同一仓库，按 README 可在新环境从零启动。", indent=False)

    doc.save(str(OUT / "实验一实验报告.docx"))
    print("saved report")


# ================================================================ 需求验收表
def build_acceptance():
    doc = Document()
    setup_section(doc, landscape=True)
    patch_style(doc.styles["Normal"], CN_BODY, 12, line=1.5, after=4, indent_chars=0)
    patch_style(doc.styles["Heading 1"], CN_HEAD, 14, bold=True, line=1.5, before=10, after=5,
                align=WD_ALIGN_PARAGRAPH.LEFT, indent_chars=0)
    add_page_number(doc)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    set_run_font(p.add_run("StudyTask 需求验收表（实验一 T1 至 T10）"), CN_HEAD, 18, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    set_run_font(p.add_run("测试环境：Windows 11 / Python 3.13.16 / Flask 3.1.3 / SQLite；"
                           "测试日期：2026-11-10；执行人：　　　　"), CN_BODY, 10.5)

    rows = [
        ["T1", "FR-01", "填写课程“数据结构”、截止日期为明天、优先级“高”后提交", "列表显示新增任务，字段与输入一致",
         "提交后跳转详情页，列表出现该任务，课程、日期、优先级均正确", "截图 01；test_t1", "通过"],
        ["T2", "FR-01", "任务名称留空，其余字段正常填写后提交", "提示错误，不产生脏数据",
         "页面返回 400，字段下方提示“任务名称不能为空”，数据库无新增记录", "截图 02；test_t2", "通过"],
        ["T3", "FR-03", "进入编辑页，修改任务描述与优先级后保存", "修改成功且刷新后保留",
         "详情页显示新描述与新的优先级标记，重新打开页面仍为修改后的值", "test_t3", "通过"],
        ["T4", "FR-05", "依次点击标记为进行中、标记为已完成", "状态逐次正确更新并持久保存",
         "列表与详情页状态依次变为“进行中”“已完成”，重新查询仍为已完成", "test_t4、test_t4b", "通过"],
        ["T5", "FR-06", "分别按课程、状态、优先级以及三者组合筛选", "结果只包含匹配任务",
         "单条件与组合条件均只返回匹配记录，清除筛选后恢复全量列表", "截图 05；test_t5", "通过"],
        ["T6", "FR-07", "新增截止日期为昨天、状态未完成的任务", "显示逾期标识",
         "列表该行显示红色“已逾期”标记", "test_t6", "通过"],
        ["T7", "FR-07", "新增截止日期为明天、状态未完成的任务", "显示即将到期标识",
         "列表该行显示“即将到期”标记；已完成任务不显示提醒", "test_t7、test_t7b", "通过"],
        ["T8", "FR-08", "创建 5 项任务，其中完成 2 项", "总数 5、完成数 2、完成率 40%",
         "首页统计卡片显示 5、2、40%", "截图 01；test_t8", "通过"],
        ["T9", "FR-04", "点击删除进入确认页，分别执行取消与确认", "取消不删除，确认后删除",
         "取消返回详情页，任务仍在；确认后列表不再显示该任务，详情页返回 404", "截图 04；test_t9", "通过"],
        ["T10", "FR-09", "录入数据后关闭服务进程并重新启动，再查询", "已保存数据仍可查询",
         "重启后列表、筛选与统计结果不变，数据来自 instance/studytask.db", "真实重启验证；test_t10", "通过"],
    ]
    add_table(doc,
              ["用例", "需求编号", "输入与测试步骤", "预期结果", "实际结果", "证据", "结论"],
              rows,
              [1.5, 2.2, 7.4, 4.6, 8.2, 3.6, 1.5],
              aligns=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT,
                      WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT,
                      WD_ALIGN_PARAGRAPH.CENTER], font_size=9)

    body(doc, "补充自动化测试（同一仓库 tests/test_app.py）：18 条用例全部通过，"
              "包含非法日期 2026-02-30、名称超长 101 字、描述超长 1001 字、非法状态值、"
              "不存在的任务与页面（404）、零任务时完成率为 0% 等边界场景。执行命令 python -m pytest -v。", indent=False)
    body(doc, "结论：T1 至 T10 全部通过，FR-01 至 FR-10 已覆盖，无严重功能缺陷；"
              "已知限制包括仅支持单用户本地使用、使用 Flask 开发服务器、未提供数据导出入口。", indent=False)

    doc.save(str(OUT / "需求验收表.docx"))
    print("saved acceptance")


if __name__ == "__main__":
    os.makedirs(SHOT, exist_ok=True)
    build_report()
    build_acceptance()
