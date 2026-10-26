# -*- coding: utf-8 -*-
"""IOT 云开测追加前强制覆盖。

桌面各试验用 ``*_append_count``：0=覆盖队列，>=1=叠一套。
云任务 ``auto_append`` 且 **自动开跑** 时若不清零，上一轮（含远程中止未走完收尾）
残留计数会把本轮命令叠在旧队列后，表现为「跑完一次又从头追加再跑」。

「只追加」（``auto_append`` 且 ``auto_start=false``）用于运维连下多项未开跑命令，
须保留已有队列，交给 ``apply_append_mode`` 做同项/跨项判定；此时禁止整表清空。
"""
from __future__ import annotations

from typing import Any, Callable, Optional


def should_force_overwrite_for_iot_job(*, auto_start: bool) -> bool:
    """是否在追加前强制清空桌面队列。

    - ``auto_start=True``（默认云开测）：必须覆盖，防叠第二套。
    - ``auto_start=False``（只追加）：保留队列，允许跨项连下。
    """
    return bool(auto_start)


def force_overwrite_before_iot_append(
    *,
    reset_count: Optional[Callable[[], Any]] = None,
    log: Optional[Callable[[str], None]] = None,
) -> bool:
    """调用桌面清零回调；成功返回 True。"""
    if not callable(reset_count):
        if log:
            log("IOT 追加前无法强制覆盖：未绑定 reset_count")
        return False
    try:
        reset_count()
    except Exception as exc:
        if log:
            log(f"IOT 追加前强制覆盖失败: {exc}")
        return False
    if log:
        log("IOT 追加前已强制覆盖（清零追加计数，禁止叠队列）")
    return True
