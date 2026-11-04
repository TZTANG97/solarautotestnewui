# -*- coding: utf-8 -*-
"""IOT 云开测追加前强制覆盖。

桌面各试验用 ``*_append_count``：0=覆盖队列，>=1=叠一套。
云任务 ``auto_append`` 且 **自动开跑**、本机未在跑时若不清零，上一轮（含远程中止未走完收尾）
残留计数会把本轮命令叠在旧队列后，表现为「跑完一次又从头追加再跑」。

「只追加」（``auto_append`` 且 ``auto_start=false``）用于运维连下多项未开跑命令，
须保留已有队列，交给 ``apply_append_mode`` 做同项/跨项判定；此时禁止整表清空。

本机已在「运行/暂停」，或桌面已经追加、队列里还有命令时，不得清队列。
IOT 再追加应接在现有命令后面。队列已空时，自动开跑仍覆盖，避免残留计数叠第二套。
"""
from __future__ import annotations

from typing import Any, Callable, Optional

_EXPERIMENT_START_SOURCES = frozenset(
    {"experiment_start", "exper_start", "blockly_start"}
)


def _job_source(params: Any) -> str:
    if not isinstance(params, dict):
        return ""
    return str(params.get("source") or "").strip().lower()


def coerce_auto_start(params: Any) -> bool:
    """云任务没带 ``auto_start`` 时与网页默认勾选一致，按自动开始。

    显式 ``false`` 仍是只追加、不开跑。
    实验管理 ``source=experiment_start`` 一律开跑：本地开测写入的
    ``auto_start=false`` 若被带回云任务，会导致跳过开跑并秒成功。
    """
    if isinstance(params, dict):
        if _job_source(params) in _EXPERIMENT_START_SOURCES:
            return True
        if "auto_start" in params:
            return bool(params.get("auto_start"))
    return True


def coerce_auto_append(params: Any) -> bool:
    """实验管理开测必须追加；其它任务尊重显式 ``auto_append``，默认 True。"""
    if isinstance(params, dict):
        if _job_source(params) in _EXPERIMENT_START_SOURCES:
            return True
        if "auto_append" in params:
            return bool(params.get("auto_append"))
    return True


def should_force_overwrite_for_iot_job(
    *,
    auto_start: bool,
    desktop_running: bool = False,
    queue_nonempty: bool = False,
) -> bool:
    """是否在追加前强制清空桌面队列。

    - 只追加（``auto_start=False``）：保留队列。
    - 本机已在跑，或桌面已经追加、队列非空：保留队列，让 ``apply_append_mode`` 跨项/同项。
    - 队列已空且自动开跑：覆盖，清掉上一轮残留计数。
    """
    if desktop_running or queue_nonempty:
        return False
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
