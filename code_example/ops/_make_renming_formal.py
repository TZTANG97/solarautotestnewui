# -*- coding: utf-8 -*-
"""Rebuild 任命函.docx with formal Chinese document layout."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

SRC = Path(
    r"e:\腾讯电脑管家软件搬家\xwechat_files\wxid_j9jgj60bl99o21_4a84\msg\file\2026-10\任命函.docx"
)
DST = SRC.with_name("任命函_正式版.docx")
DST_OVERWRITE = SRC  # try replace original if not locked
DST_BAK = SRC.with_name("任命函_原稿备份.docx")
DST_COPY = Path(r"E:\solarautotestnewui\docs") / "任命函_正式版.docx"


def set_run_font(run, *, name_cn="仿宋", name_en="Times New Roman", size_pt=16, bold=False):
    run.bold = bold
    run.font.size = Pt(size_pt)
    run.font.name = name_en
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:ascii"), name_en)
    rFonts.set(qn("w:hAnsi"), name_en)
    rFonts.set(qn("w:eastAsia"), name_cn)
    rFonts.set(qn("w:cs"), name_en)


def add_para(
    doc,
    text,
    *,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    name_cn="仿宋",
    size_pt=16,
    bold=False,
    first_indent_chars=0,
    space_before=0,
    space_after=0,
    line_pt=28,
):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(line_pt)
    if first_indent_chars:
        # 2 Chinese characters ≈ 2 * font size
        pf.first_line_indent = Pt(size_pt * first_indent_chars)
    run = p.add_run(text)
    set_run_font(run, name_cn=name_cn, size_pt=size_pt, bold=bold)
    return p


def main():
    # Backup original once
    if SRC.exists() and not DST_BAK.exists():
        DST_BAK.write_bytes(SRC.read_bytes())

    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    # Formal Chinese letter margins
    section.top_margin = Cm(3.7)
    section.bottom_margin = Cm(3.5)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)

    # Default style
    styles = doc.styles["Normal"]
    styles.font.name = "Times New Roman"
    styles.font.size = Pt(16)
    styles.element.rPr.rFonts.set(qn("w:eastAsia"), "仿宋")

    # Title
    add_para(
        doc,
        "任 命 函",
        align=WD_ALIGN_PARAGRAPH.CENTER,
        name_cn="黑体",
        size_pt=22,
        bold=False,
        space_before=0,
        space_after=18,
        line_pt=36,
    )

    # Recipient
    add_para(
        doc,
        "致：公司全体员工及相关部门",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        space_after=6,
    )

    # Subject / decision line
    add_para(
        doc,
        "关于授权周常州同志担任苏州途哲科技有限公司实验室经理的任命决定",
        align=WD_ALIGN_PARAGRAPH.LEFT,
        space_before=6,
        space_after=12,
    )

    # Body
    add_para(
        doc,
        (
            "为适应公司业务发展需要，进一步完善实验室管理体系，保障实验室检测/校准工作的"
            "独立、公正、科学、准确，经公司管理层研究决定：任命周常州同志为苏州途哲科技"
            "有限公司实验室经理，全面负责实验室的日常运营与质量管理工作。本任命自"
            "2026年3月1日起生效。"
        ),
        first_indent_chars=2,
        space_after=6,
    )

    add_para(
        doc,
        "主要职责与权限如下：",
        first_indent_chars=2,
        space_before=6,
        space_after=6,
    )

    duties = [
        (
            "体系运行与维护：全面负责实验室CNAS（ISO/IEC 17025）质量管理体系的建立、"
            "实施、保持和改进，确保体系持续有效运行。"
        ),
        (
            "公正性与保密性：作为实验室公正性及保密性的第一责任人，确保实验室活动不受"
            "任何来自内外部的不正当商业、财务和其他方面的压力和影响，严守客户秘密及"
            "技术机密。"
        ),
        (
            "资源配置与保障：负责实验室人员、设备、设施及环境等资源的统筹配置，确保"
            "满足检测/校准方法及体系运行的要求。"
        ),
        (
            "技术运作与质量控制：组织并监督实验室日常检测/校准活动的开展，审批检测"
            "方案，确保结果的有效性和准确性；组织参加能力验证及实验室间比对。"
        ),
        (
            "人员管理与授权：负责实验室人员的岗位设置、培训、考核及能力监控，对关键"
            "岗位人员（如授权签字人、检测员等）进行资格确认与授权。"
        ),
        (
            "内外部审核与评审：组织实验室内部审核和管理评审，负责对接CNAS等外部评审"
            "机构的评审工作，并组织落实不符合项的整改闭环。"
        ),
        (
            "客户沟通与投诉处理：负责与客户就技术及质量问题进行沟通，组织处理客户投诉，"
            "提升客户满意度。"
        ),
    ]
    for i, text in enumerate(duties, 1):
        p = add_para(doc, f"{i}. {text}", first_indent_chars=0, space_after=3)
        # hanging indent for numbered items
        p.paragraph_format.left_indent = Pt(16)
        p.paragraph_format.first_line_indent = Pt(-16)

    add_para(
        doc,
        "权限授予：",
        first_indent_chars=2,
        space_before=10,
        space_after=3,
    )
    add_para(
        doc,
        (
            "公司授权周常州同志在实验室管理事务中，代表公司行使上述相关职权，包括但"
            "不限于：实验室人员调配建议权、设备采购审批权（限额内）、检测报告/证书的"
            "审核批准权（如符合授权签字人条件则另行授权），以及体系文件在权限范围内的"
            "审批发布权。"
        ),
        first_indent_chars=2,
        space_after=6,
    )

    add_para(
        doc,
        (
            "请公司各部门及相关人员积极配合其工作，共同推动公司实验室质量管理水平"
            "迈上新台阶。"
        ),
        first_indent_chars=2,
        space_before=6,
        space_after=6,
    )

    add_para(
        doc,
        "特此任命。",
        first_indent_chars=2,
        space_before=6,
        space_after=24,
    )

    # Signature block (right side)
    for text in (
        "苏州途哲科技有限公司",
        "总经理（或法定代表人）签字：_______________",
        "日期：　　　年　　月　　日",
    ):
        add_para(
            doc,
            text,
            align=WD_ALIGN_PARAGRAPH.RIGHT,
            space_before=0,
            space_after=4,
            line_pt=28,
        )

    doc.save(DST)
    DST_COPY.parent.mkdir(parents=True, exist_ok=True)
    doc.save(DST_COPY)
    try:
        doc.save(DST_OVERWRITE)
        print("Replaced original:", DST_OVERWRITE)
    except PermissionError:
        print("Original file is open/locked; left unchanged:", DST_OVERWRITE)
    print("Backup:", DST_BAK if DST_BAK.exists() else "(none)")
    print("Saved:", DST)
    print("Copy:", DST_COPY)


if __name__ == "__main__":
    main()
