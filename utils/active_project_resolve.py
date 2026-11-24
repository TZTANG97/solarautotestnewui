# -*- coding: utf-8 -*-
"""开跑/德威创 prepare 用的试验名解析（comboBox_PS 为空时的兜底）。"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, Sequence


def lookup_project_name_from_token(
    token: Any,
    *,
    resolve_handler: Optional[Callable[[str], Any]] = None,
) -> str:
    """把 IOT test_type / 中文名解析成桌面分项名。"""
    name = str(token or "").strip()
    if not name:
        return ""
    if resolve_handler is not None:
        try:
            handler = resolve_handler(name)
        except Exception:
            handler = None
        if isinstance(handler, dict) and handler.get("project_name"):
            return str(handler.get("project_name")).strip()
    return name


def is_plausible_desktop_project_name(name: str) -> bool:
    """尚未进 Dialog 表时，仍可接受的桌面中文试验名。"""
    text = str(name or "").strip()
    if not text:
        return False
    if text.startswith("solar_"):
        return False
    if "/" in text or "\\" in text:
        return False
    # 纯英文 key / UUID 等不当试验名
    if " " not in text and text.isascii() and "_" in text:
        return False
    return True


def pick_active_project_name(
    candidates: Sequence[Any],
    *,
    resolve_handler: Optional[Callable[[str], Any]] = None,
    is_known: Optional[Callable[[str], bool]] = None,
    registered_projects: Optional[Iterable[str]] = None,
    prefer_dew: Optional[Callable[[str], bool]] = None,
    preferred: Any = None,
) -> str:
    """从候选里挑出一个试验名。优先已知 Dialog；否则用 IOT 解出的中文名。"""
    seen = set()
    fallback = ""
    known_fn = is_known or (lambda _n: False)
    for raw in candidates:
        name = lookup_project_name_from_token(raw, resolve_handler=resolve_handler)
        if not name or name in seen:
            continue
        seen.add(name)
        if known_fn(name):
            return name
        if not fallback and is_plausible_desktop_project_name(name):
            fallback = name

    names = [str(n or "").strip() for n in (registered_projects or ()) if str(n or "").strip()]
    if len(names) == 1:
        return names[0]
    if prefer_dew is not None:
        for name in names:
            try:
                if prefer_dew(name):
                    return name
            except Exception:
                continue

    if fallback:
        return fallback
    return lookup_project_name_from_token(preferred, resolve_handler=resolve_handler)


def collect_handoff_project_candidates(svc: Any) -> list:
    """从 IOT handoff 的 _job_ctx / _awaiting 收集试验名候选。"""
    out = []
    if svc is None:
        return out
    for attr in ("_job_ctx", "_awaiting"):
        src = getattr(svc, attr, None)
        if not isinstance(src, dict):
            continue
        handler = src.get("handler") or {}
        if isinstance(handler, dict):
            out.append(handler.get("project_name") or handler.get("label"))
        out.append(src.get("test_type"))
    return out
