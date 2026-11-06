# -*- coding: utf-8 -*-
"""交叉测试：多试验追加 → 换页不覆盖 → 队列分段可顺序跑完。"""
from __future__ import annotations

from utils.append_mode import (
    apply_append_mode,
    begin_append_attempt,
    commit_append_if_success,
    resolve_append_mode,
    should_refresh_progress_on_project_switch,
)
from utils.test_queue_markers import is_queue_end_row, parse_queue_segments


def _append(g: dict, name: str, cmds: list, *, local_count: int) -> None:
    flag, change, label = apply_append_mode(g, project_name=name, local_count=local_count)
    print(f"  append {name}: flag={flag} change={change} label={label}")
    if flag == "0":
        g["strArrayTest"] = []
    g["strArrayTest"].extend(cmds)
    prev = begin_append_attempt(g)
    g["strSettingTestFlag"] = "1"
    assert commit_append_if_success(g, name, prev), name
    assert is_queue_end_row(g["strArrayTest"][-1]), name


def main() -> None:
    g = {
        "strArrayTest": [],
        "project_now": "",
        "strAddTestFlag": "0",
        "project_change": "0",
        "strSettingTestFlag": "0",
    }

    print("1) 谐波电流 覆盖追加")
    _append(
        g,
        "谐波电流",
        [["AC", "write", "HARM_START"], ["AC", "query", "*IDN?", "", "", "", "", "", "", 10]],
        local_count=0,
    )
    assert g["project_now"] == "谐波电流"

    print("2) 模拟打开「过欠压」对话框（禁止改写 project_now）")
    # 旧 bug：project_now = 当前下拉
    poisoned = resolve_append_mode(
        project_name="过欠压_过欠频",
        local_count=0,
        queue=g["strArrayTest"],
        project_now="过欠压_过欠频",
    )
    assert poisoned[2] == "覆盖"
    kept = resolve_append_mode(
        project_name="过欠压_过欠频",
        local_count=0,
        queue=g["strArrayTest"],
        project_now=g["project_now"],
    )
    assert kept == ("1", "1", "跨项追加"), kept

    print("3) 过欠压_过欠频 跨项追加")
    before = list(g["strArrayTest"])
    _append(
        g,
        "过欠压_过欠频",
        [["AC", "write", "OVUF_START"], ["AC", "write", "VOLT 253"]],
        local_count=0,
    )
    assert any(r[2] == "HARM_START" for r in g["strArrayTest"])
    assert any(r[2] == "OVUF_START" for r in g["strArrayTest"])
    assert len(g["strArrayTest"]) > len(before)

    print("4) 电压闪变 再跨一项")
    _append(
        g,
        "电压闪变",
        [["AC", "write", "FLICK_START"]],
        local_count=0,
    )

    segs = parse_queue_segments(g["strArrayTest"])
    names = [s["name"] for s in segs]
    print("  segments:", names)
    assert names == ["谐波电流", "过欠压_过欠频", "电压闪变"], names

    print("5) 换下拉到未追加项：进度应 keep_queue")
    assert (
        should_refresh_progress_on_project_switch(
            current_count=0, queue=g["strArrayTest"], running=False
        )
        == "keep_queue"
    )

    print("6) 模拟 RunProject 顺序：按 QUEUE/end_test 分段推进")
    order = []
    for i, row in enumerate(g["strArrayTest"]):
        if is_queue_end_row(row):
            order.append(("END", row[2], i))
        elif row[0] == "AC" and row[1] == "write":
            order.append(("CMD", row[2], i))
    cmd_names = [x[1] for x in order if x[0] == "CMD"]
    assert cmd_names == ["HARM_START", "OVUF_START", "VOLT 253", "FLICK_START"], cmd_names
    end_names = [x[1] for x in order if x[0] == "END"]
    assert end_names == ["谐波电流", "过欠压_过欠频", "电压闪变"], end_names
    # 每段 END 都在该段命令之后
    first_cmd = {
        "谐波电流": "HARM_START",
        "过欠压_过欠频": "OVUF_START",
        "电压闪变": "FLICK_START",
    }
    for name, cmd in first_cmd.items():
        cmd_i = next(i for t, n, i in order if t == "CMD" and n == cmd)
        end_i = next(i for t, n, i in order if t == "END" and n == name)
        assert cmd_i < end_i, (name, cmd_i, end_i)

    print("CROSS_OK", len(g["strArrayTest"]), "rows,", len(segs), "projects")


if __name__ == "__main__":
    main()
