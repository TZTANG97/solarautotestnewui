# -*- coding: utf-8 -*-
"""Append week39 daily SolarAutoTest bench work (2026-09/20~09/24).

Idempotent: skips a day if marker already present in column C.
Only appends items not already covered by the existing daily text.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(r"c:\Users\13852\Desktop\每周周报_唐子钧.xlsx")
BAK = (
    Path(__file__).resolve().parents[1]
    / "code_example"
    / "media"
    / "每周周报_唐子钧_week39追加前_20260924.xlsx"
)

MARKER = "【追加·光伏自动化台架】"

# rows 5..9 = 周日..周四（在既有 IOT/线上内容后追加台架实测）
APPENDS = {
    5: (  # Sun 09/20
        "IOT/光伏自动化",
        "\n".join(
            [
                MARKER,
                "1. 台架：确认工控机德威创 SCPI + Agent 为本周 10min 过压等开测主路径，核对导出字段与 RATE 档位。",
            ]
        ),
    ),
    6: (  # Mon 09/21
        "IOT/光伏自动化",
        "\n".join(
            [
                MARKER,
                "1. 台架：配合全队列 handoff，核对 WT/德威创桌面会话与网页下发一致，避免假已连接开测失败。",
            ]
        ),
    ),
    7: (  # Tue 09/22
        "IOT/光伏自动化",
        "\n".join(
            [
                MARKER,
                "1. SoftPanel/IV：Voc/FF 自动填充改回手动；UI 字号锁定 scale=1.0。",
                "2. 设备页：DC2–4/WT/德威创布局与输入框挤压修复；更新安装界面现代化。",
                "3. 保存路径：WT/德威创默认 %LOCALAPPDATA%\\SolarAutoTest\\… 并自动建目录；德威创面板增加保存路径浏览；修复 config.ini %LOCALAPPDATA% 插值崩溃。",
                "4. 德威创：导出树补 F_fund；刷新率加 200/500/1000ms；关闭断流自动抓跳脱值（10min 过压误报）。",
                "5. 启动自动连：USB 直流按 status.json/槽位记忆恢复；OSS 多轮发版至 20260922.1759。",
            ]
        ),
    ),
    8: (  # Wed 09/23
        "IOT/光伏自动化",
        "\n".join(
            [
                MARKER,
                "1. 10min 过压×德威创（工况机）：START 改到启机/并网等待之后；Time[s] 首点归零；200ms 绝对节拍并按设备 RATE 回报对齐。",
                "2. 关机设置：尊重「开启/关闭」——追加中间轮保持输出，最后一轮再关断，修复误强制 OUTP OFF 导致关机再启机。",
                "3. OSS 发版：20260923.1435（录波时机/时基）、20260923.1446（关机保持）。",
            ]
        ),
    ),
    9: (  # Thu 09/24
        "IOT/光伏自动化",
        "\n".join(
            [
                MARKER,
                "1. 工况机：10min 过压德威创开测问题复盘（并网前开录 / 时基 / 追加关机）与发版验证收口。",
                "2. 周报：按既有格式将本周台架实际工作追加写入 week39。",
            ]
        ),
    ),
}


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"missing: {SRC}")
    BAK.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, BAK)
    print("backup", BAK)

    wb = openpyxl.load_workbook(SRC)
    ws = next((s for s in wb.worksheets if "week39" in s.title), None)
    if ws is None:
        raise SystemExit("week39 sheet not found")

    ws["E2"] = "日期：2026/09/20  week 39（周日至周四，截止09/24）"

    wrap = Alignment(wrap_text=True, vertical="top")
    center = Alignment(wrap_text=True, vertical="center", horizontal="center")

    for row, (proj_tag, block) in APPENDS.items():
        old_c = str(ws.cell(row, 3).value or "").rstrip()
        if MARKER in old_c:
            print(f"row {row}: already appended, skip")
            continue

        old_proj = str(ws.cell(row, 2).value or "").strip()
        if not old_proj:
            ws.cell(row, 2).value = proj_tag
        elif "光伏" not in old_proj:
            ws.cell(row, 2).value = f"{old_proj}/光伏"

        new_c = old_c + ("\n" if old_c else "") + block
        cell = ws.cell(row, 3)
        cell.value = new_c
        cell.alignment = wrap
        ws.cell(row, 2).alignment = center
        for col in (4, 6):
            if not ws.cell(row, col).value:
                ws.cell(row, col).value = "完成"
            ws.cell(row, col).alignment = center
        ws.row_dimensions[row].height = max(
            float(ws.row_dimensions[row].height or 60),
            14 * (new_c.count("\n") + 3),
        )
        print(f"row {row}: appended {block.count(chr(10)) + 1} lines")

    wb.save(SRC)
    print("saved", SRC)


if __name__ == "__main__":
    main()
