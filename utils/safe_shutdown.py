# -*- coding: utf-8 -*-
"""统一生成强制安全关机命令。

关机序列只写 ``OUTP OFF``，顺序固定为 DC →（蓝点缓降等待）→ AC。
时间字段沿用项目现有约定：数值单位为 0.1 秒。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


BLUESIGHT_DC_OFF_SETTLE_01S = 50
DEFAULT_INTER_COMMAND_WAIT_01S = 5


def _empty_row() -> list[Any]:
    return ["" for _ in range(10)]


def _write_row(device: str) -> list[Any]:
    row = _empty_row()
    row[0] = device
    row[1] = "write"
    row[2] = "OUTP OFF"
    return row


def _wait_row(wait_01s: int, wait_slot: int) -> list[Any]:
    if not 0 <= wait_slot < 10:
        raise ValueError("wait_slot must be between 0 and 9")
    row = _empty_row()
    row[0] = "AC"
    row[1] = "query"
    row[2] = "*IDN?"
    row[wait_slot] = int(wait_01s)
    return row


def _format_attr_name(pattern: str, channel: int) -> str:
    if "%" in pattern:
        return pattern % channel
    if "{" in pattern:
        return pattern.format(channel, ch=channel, channel=channel)
    return pattern


def _is_checked(widget: Any) -> bool:
    if widget is None:
        return False
    try:
        return bool(widget.isChecked())
    except Exception:
        return False


def s1_and_step_dc(ui: Any, step_cb_name: str, channel: int) -> bool:
    """仅当对应 S1 与目标步骤 DC 复选框同时勾选时返回 True。"""
    s1_name = "checkBox_S1_DC%d" % int(channel)
    step_name = _format_attr_name(step_cb_name, int(channel))
    return _is_checked(getattr(ui, s1_name, None)) and _is_checked(
        getattr(ui, step_name, None)
    )


def enabled_shutdown_dc_channels(
    ui: Any,
    *,
    s1_fmt: str = "checkBox_S1_DC%d",
    end_fmt: str = "checkBox_S_End_DC%d",
    channels: Iterable[int] = range(1, 5),
) -> list[int]:
    """按严格 S1∧End 规则返回可关断的 1 基 DC 通道号。"""
    enabled: list[int] = []
    for channel in channels:
        channel_i = int(channel)
        s1_name = _format_attr_name(s1_fmt, channel_i)
        end_name = _format_attr_name(end_fmt, channel_i)
        if _is_checked(getattr(ui, s1_name, None)) and _is_checked(
            getattr(ui, end_name, None)
        ):
            enabled.append(channel_i)
    return enabled


def force_end_combos_off(
    ui: Any,
    combo_names: Iterable[str],
    *,
    log: Any = None,
    tag: str = "",
) -> list[str]:
    """把关机组合框强制设为“关闭”，返回发生改写的控件名。"""
    changed: list[str] = []
    for combo_name in combo_names:
        combo = getattr(ui, combo_name, None)
        if combo is None:
            continue
        try:
            if combo.currentText() != "开启":
                continue
            combo.setCurrentText("关闭")
        except Exception:
            continue
        changed.append(combo_name)
        if log is not None:
            message = "%s关机步骤已强制改为关闭输出: %s" % (
                ("[%s] " % tag) if tag else "",
                combo_name,
            )
            try:
                if callable(log):
                    log(message)
                else:
                    log.append(message)
            except Exception:
                pass
    return changed


def _factor_for_channel(
    per_dc_factor: Mapping[Any, Any] | None, channel: int
) -> str:
    if not per_dc_factor:
        return ""
    zero_based = int(channel) - 1
    for key in (str(zero_based), zero_based):
        if key in per_dc_factor:
            return str(per_dc_factor.get(key) or "").strip()
    return ""


def build_forced_shutdown_rows(
    *,
    dc_channels: Iterable[int],
    per_dc_factor: Mapping[Any, Any] | None = None,
    settle_01s: int = BLUESIGHT_DC_OFF_SETTLE_01S,
    inter_wait_01s: int = DEFAULT_INTER_COMMAND_WAIT_01S,
    wait_slot: int = 8,
) -> list[list[Any]]:
    """构造 DC OFF → 蓝点缓降等待 → AC OFF 的固定安全序列。

    ``dc_channels`` 使用 1 基编号，``per_dc_factor`` 延续主程序的
    0 基字符串键（``"0"`` 对应 DC1）。蓝点等待不会低于 50 tick。
    """
    channels = sorted({int(channel) for channel in dc_channels})
    if any(channel < 1 for channel in channels):
        raise ValueError("DC channels must be one-based positive integers")

    rows: list[list[Any]] = []
    has_bluesight = False
    inter_wait = max(0, int(inter_wait_01s))

    for channel in channels:
        rows.append(_write_row("DC%d" % channel))
        if _factor_for_channel(per_dc_factor, channel).casefold() == "bluesight":
            has_bluesight = True
        if inter_wait:
            rows.append(_wait_row(inter_wait, wait_slot))

    if has_bluesight:
        rows.append(
            _wait_row(
                max(BLUESIGHT_DC_OFF_SETTLE_01S, int(settle_01s)),
                wait_slot,
            )
        )

    rows.append(_write_row("AC"))
    if inter_wait:
        rows.append(_wait_row(inter_wait, wait_slot))
    return rows


def append_ui_forced_shutdown_step(
    commands: list[list[Any]],
    steps: list[list[list[Any]]],
    ui: Any,
    *,
    per_dc_factor: Mapping[Any, Any] | None = None,
    settle_01s: int = BLUESIGHT_DC_OFF_SETTLE_01S,
    inter_wait_01s: int = DEFAULT_INTER_COMMAND_WAIT_01S,
    log: Any = None,
    tag: str = "",
) -> list[int]:
    """UI 关机步：强制关输出，并按 DC→缓降等待→AC 追加命令。

    返回启用的 1 基 DC 通道列表（可能为空，仍会关 AC）。
    """
    force_end_combos_off(
        ui,
        (
            "comboBox_S_End_AC",
            "comboBox_S_End_DC1",
            "comboBox_S_End_DC2",
            "comboBox_S_End_DC3",
            "comboBox_S_End_DC4",
        ),
        log=log,
        tag=tag,
    )
    dc_channels = enabled_shutdown_dc_channels(ui)
    step_rows = build_forced_shutdown_rows(
        dc_channels=dc_channels,
        per_dc_factor=per_dc_factor,
        settle_01s=settle_01s,
        inter_wait_01s=inter_wait_01s,
    )
    commands.extend(step_rows)
    steps.append(list(step_rows))
    return dc_channels
