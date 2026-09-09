# -*- coding: utf-8 -*-
"""将 SCPITestWave.py 各 Send 的手写 AC 启机块替换为 append_ac_startup_from_ui。

跳过：thaidianyashanbianSend（闪变，技能约定只读）。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "SCPITestWave.py"

SKIP_FUNCS = {
    "thaidianyashanbianSend",  # 闪变：只读参考
}

UI_RE = re.compile(
    r"S1ACEACHStatus\s*=\s*(\w+)\.comboBox_S1_AC_2\.currentText\(\)"
)


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def replace_startup_block(body: str, ui_var: str) -> tuple[str, int]:
    """替换第一个 step1 的 if 单相 / elif 三相 启机块。"""
    lines = body.splitlines(keepends=True)
    start = None
    indent = None
    for i, line in enumerate(lines):
        if re.match(r'[ \t]*if S1ACEACHStatus == "单相":\s*$', line):
            start = i
            indent = _line_indent(line)
            break
    if start is None:
        return body, 0

    # 找同缩进的 elif 三相
    elif_i = None
    for i in range(start + 1, len(lines)):
        ind = _line_indent(lines[i])
        if lines[i].strip() == "":
            continue
        if ind < indent:
            return body, 0
        if ind == indent and re.match(
            r'[ \t]*elif S1ACEACHStatus == "三相":\s*$', lines[i]
        ):
            elif_i = i
            break
        if ind == indent and not lines[i].lstrip().startswith(("#", "elif", "else")):
            # 同级其他语句，结构异常
            return body, 0
    if elif_i is None:
        return body, 0

    # elif 块结束：下一个同级或更小缩进的非空行
    end = None
    for i in range(elif_i + 1, len(lines)):
        if lines[i].strip() == "":
            # 空行可能仍在块内；看下一非空
            continue
        ind = _line_indent(lines[i])
        if ind <= indent:
            end = i
            break
    if end is None:
        end = len(lines)

    # 安全：被替换块内应含 PHAS / VOLT
    block_text = "".join(lines[start:end])
    if "INST:PHAS" not in block_text or "VOLT" not in block_text:
        return body, 0

    replacement = (
        f'{" " * indent}# 共用 AC 启机（爱科同压: EDIT ALL + 一次 VOLT/FREQ）\n'
        f'{" " * indent}append_ac_startup_from_ui({ui_var}, strArrayTest, strArrayTestStepSingle)\n'
    )
    # 若 end 前有空行，保留一块后的结构
    new_lines = lines[:start] + [replacement] + lines[end:]
    new_body = "".join(new_lines)

    # 若 S1ACEACHStatus 仅剩赋值且无其它引用，删赋值
    if new_body.count("S1ACEACHStatus") == 1:
        new_body = re.sub(
            r"[ \t]*S1ACEACHStatus\s*=\s*\w+\.comboBox_S1_AC_2\.currentText\(\)\n",
            "",
            new_body,
            count=1,
        )
    return new_body, 1


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    parts = re.split(r"(?=^def )", text, flags=re.M)
    changed = []
    out = []
    for part in parts:
        mdef = re.match(r"^def (\w+)\(", part)
        if not mdef:
            out.append(part)
            continue
        name = mdef.group(1)
        if name in SKIP_FUNCS:
            out.append(part)
            continue
        if "Send" not in name:
            out.append(part)
            continue
        if 'if S1ACEACHStatus == "单相":' not in part:
            out.append(part)
            continue
        um = UI_RE.search(part)
        if not um:
            print(f"SKIP {name}: 找不到 UI 变量")
            out.append(part)
            continue
        # Cos Brazil 等可能有多处单相/三相；只替换含 step1 启机的第一处
        # （后续矩阵改压另议）
        new_part, n = replace_startup_block(part, um.group(1))
        if n == 0:
            print(f"SKIP {name}: 未匹配到启机块")
            out.append(part)
            continue
        # 若还有第二处 if S1ACEACHStatus == 单相（矩阵），再试一轮（限 3 次）
        rounds = 1
        while 'if S1ACEACHStatus == "单相":' in new_part and rounds < 3:
            # 矩阵块也可能错误用 EACH；仅当块内含 EDIT EACH 或 PHAS THREE 启机风格时替换
            # 对 Cos Brazil step 中途改压：若仍是完整单相/三相设定，也统一
            new_part2, n2 = replace_startup_block(new_part, um.group(1))
            if n2 == 0:
                break
            new_part = new_part2
            n += n2
            rounds += 1
        changed.append(f"{name} x{n} -> {um.group(1)}")
        out.append(new_part)

    if not changed:
        print("无改动")
        return 1

    TARGET.write_text("".join(out), encoding="utf-8")
    print(f"已改 {len(changed)} 个函数:")
    for c in changed:
        print(" ", c)

    text2 = TARGET.read_text(encoding="utf-8")
    send_each = []
    for m in re.finditer(r"^def (\w+Send)\(", text2, re.M):
        start = m.start()
        nxt = re.search(r"^def ", text2[m.end() :], re.M)
        end = m.end() + (nxt.start() if nxt else len(text2) - m.end())
        body = text2[start:end]
        if "INST:EDIT EACH" in body:
            send_each.append(m.group(1))
    print("Send 内仍含 INST:EDIT EACH:", send_each or "无")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
