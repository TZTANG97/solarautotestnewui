# -*- coding: utf-8 -*-
"""回写桌面《光伏自动化项目进度表》I 列：按总览序号标记 IOT Web 接入。"""
from __future__ import annotations

import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment

SRC = Path(r"c:\Users\13852\Desktop\光伏自动化项目进度表-20260920.xlsx")
OUT = Path(r"c:\Users\13852\Desktop\光伏自动化项目进度表-20260923.xlsx")
BACKUP = Path(r"c:\Users\13852\Desktop\光伏自动化项目进度表-20260920.bak.xlsx")

TODAY = "2026-09-23"

WEB_DONE = {
    1: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：实验管理新建→填参→开始；"
        "积木与表单双向同步；Agent 填表追加"
    ),
    2: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 谐波设置与桌面 "
        "Dialog_thaixiebodianliu 对齐（谐波1~11次卡片/采集时长/录波方式/关机）；"
        "谐波卡片 DC·功率% 不再混入启机页"
    ),
    3: (
        f"已接入（开测表单+细Blockly+handoff） 2026-09-18：实验管理新建→填参→开始；"
        "积木与表单双向同步；Agent 填表追加"
    ),
    4: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaizhiliufenliang 对齐（100%/66%/33%/可选功率点、采集与录波、关机）；"
        "默认功率与录波方式（连续录）与桌面一致"
    ),
    5: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaifixedPF 对齐（采集/录波 + 测量步骤1~5 功率点、关机）；"
        "步骤功率默认 100/75/50/30/20，录波默认连续录"
    ),
    6: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaichonglian 对齐（重联1~5 电压/频率/采集、关机交流+直流1~4）；"
        "S5~S7 默认启用与桌面一致"
    ),
    7: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaistaticmppttest 对齐（蓝电/SoftPanel、DC1~4 Vnom 段、功率%、"
        "MPPT时长、蓝电 IV 默认）；隐藏 {{dcPrefix}} 模板垃圾字段"
    ),
    8: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaiguoqianya_pin 对齐（过/欠压/过/欠频扫描、相位页、时长单位默认秒、关机）；"
        "扫描启用默认与桌面一致"
    ),
    9: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaiguoqianpin_immun 对齐（频率扫描1~9、更新率、关机直流标签）；"
        "时长单位默认秒"
    ),
    10: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaiguopinjiangzai FrequencyLadder 对齐（频率台阶 list/电压/驻留）；"
        "旧 S3~S17 隐藏；关机交流/直流标签对齐"
    ),
    11: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaiqianpinshengzai FrequencyLadder 对齐（欠频台阶 list）；"
        "旧 S3~S17 隐藏；关机交流/直流标签对齐"
    ),
    12: (
        f"已接入（开测表单+细Blockly+handoff） {TODAY}：Web 与桌面 "
        "Dialog_thaivoltprotect10min 对齐（过压保护 L1~L3/采集10分钟、"
        "保护后恢复、启机电压默认230、关机）"
    ),
}

DONE_COUNT = len(WEB_DONE)
DONE_NAMES = (
    "电压闪变、谐波电流、过载、直流分量、固定PF=1、重连、静态MPPT、"
    "过欠压_过欠频、巴西过欠频稳定性、过频降载、欠频升载、10min过压保护"
)
NEXT_SEQ = 13
NEXT_NAME = "频率适应性"


def _set(cell, value):
    cell.value = value
    cell.alignment = Alignment(wrap_text=True, vertical="center")


def _bump_summary(text: str) -> str:
    t = str(text)
    t = re.sub(r"已接入\s*\d+/30", f"已接入 {DONE_COUNT}/30", t)
    t = re.sub(r"表内已接入\s*\d+/30", f"表内已接入 {DONE_COUNT}/30", t)
    t = re.sub(r"\d+\s*表内Web已接入", f"{DONE_COUNT} 表内Web已接入", t)
    t = re.sub(
        r"电压闪变[、,，]?过载|电压闪变、谐波电流、过载(?:、直流分量)?",
        DONE_NAMES,
        t,
    )
    t = t.replace("2026-09-20", TODAY)
    return t


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"missing {SRC}")
    if not BACKUP.is_file():
        BACKUP.write_bytes(SRC.read_bytes())
        print(f"backup -> {BACKUP}")

    wb = openpyxl.load_workbook(SRC)
    ws = wb[wb.sheetnames[0]]

    for row in ws.iter_rows(min_row=1, max_row=6, max_col=12):
        for cell in row:
            v = str(cell.value or "")
            if "Web" in v or "已接入" in v or "2/30" in v or "3/30" in v or "4/30" in v:
                cell.value = _bump_summary(v)

    header_row = None
    for r in range(1, 10):
        if ws.cell(r, 1).value == "序号":
            header_row = r
            break
    if header_row is None:
        raise SystemExit("header 序号 not found")

    col_i = 9
    for r in range(header_row + 1, header_row + 35):
        seq = ws.cell(r, 1).value
        if seq not in WEB_DONE:
            continue
        _set(ws.cell(r, col_i), WEB_DONE[seq])
        ws.cell(r, 11).value = TODAY
        ev = str(ws.cell(r, 12).value or "")
        note = f"｜{TODAY} IOT Web 参数已与桌面细核（见 I 列）。下一 Web 接入：{NEXT_NAME}（总览序{NEXT_SEQ}）。"
        if "IOT Web 参数已与桌面细核" not in ev or f"序{NEXT_SEQ}" not in ev:
            # 去掉旧的「下一 Web」句再追加
            ev2 = re.sub(r"｜?下一 Web 接入：[^｜]*", "", ev)
            if "IOT Web 参数已与桌面细核" in ev2:
                ev2 = re.sub(
                    r"｜?\d{4}-\d{2}-\d{2} IOT Web 参数已与桌面细核（见 I 列）。?",
                    "",
                    ev2,
                )
            ws.cell(r, 12).value = (ev2.rstrip("｜") + note).lstrip("｜")
            ws.cell(r, 12).alignment = Alignment(wrap_text=True, vertical="center")

    wb.save(OUT)
    try:
        wb.save(SRC)
        print(f"updated {SRC}")
    except PermissionError:
        print(f"原文件占用，已写 {OUT}")
    print(f"also saved {OUT} done={DONE_COUNT}/30 next={NEXT_SEQ} {NEXT_NAME}")


if __name__ == "__main__":
    main()
