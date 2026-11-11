# -*- coding: utf-8 -*-
"""分开录轮次收口：标完成，并按已知 CSV 路径立刻上传。"""
from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Sequence


def round_file_label(
    round_index: int,
    file_list: Optional[Sequence[str]] = None,
    *,
    rounds: Optional[Sequence[Mapping[str, Any]]] = None,
    save_file_name: str = "",
) -> str:
    label = ""
    if file_list and 0 <= round_index < len(file_list):
        label = str(file_list[round_index] or "").strip()
    if not label and rounds and 0 <= round_index < len(rounds):
        label = str(rounds[round_index].get("filename") or "").strip()
    if not label:
        label = str(save_file_name or "").strip()
    return label


def finalize_recording_round(
    round_index: int,
    file_list: Optional[Sequence[str]] = None,
    *,
    note: str = "本轮完成",
    csv_path: str = "",
    rounds: Optional[Sequence[Mapping[str, Any]]] = None,
    set_round: Optional[Callable[..., None]] = None,
    config_dict: Optional[Mapping[str, Any]] = None,
    save_file_name: str = "",
    log: Optional[Callable[[str], None]] = None,
) -> str:
    """把本轮标成完成。有 csv_path 时直接上传，否则按文件名再找一次。"""
    try:
        idx = int(round_index)
    except (TypeError, ValueError):
        return ""
    if idx < 0:
        return ""

    def _mark(i: int, status: str, text: str) -> None:
        if set_round is None:
            return
        try:
            set_round(i, status, note=text)
        except TypeError:
            set_round(i, status, text)

    snapshot = list(rounds or [])
    for i, item in enumerate(snapshot):
        if i < idx and str(item.get("status") or "") == "进行中":
            _mark(i, "完成", "上一轮补标完成")
    current = ""
    if 0 <= idx < len(snapshot):
        current = str(snapshot[idx].get("status") or "")
    if current != "完成":
        _mark(idx, "完成", note)

    label = round_file_label(
        idx,
        file_list,
        rounds=snapshot,
        save_file_name=save_file_name,
    )
    try:
        from utils.iot_round_upload import schedule_round_csv_upload

        schedule_round_csv_upload(
            round_index=idx,
            file_label=label,
            config_dict=dict(config_dict) if isinstance(config_dict, Mapping) else None,
            csv_path=str(csv_path or ""),
            wait_s=5.0,
        )
    except Exception as exc:
        if log is not None:
            try:
                log(f"[round_upload] schedule failed: {exc}")
            except Exception:
                pass
    return label
