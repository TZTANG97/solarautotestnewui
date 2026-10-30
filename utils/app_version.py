# -*- coding: utf-8 -*-
"""界面上显示的软件版本。安装包读 VERSION 第一行；源码目录没有该文件。"""

from __future__ import annotations

import sys
from pathlib import Path

_UNPACKAGED = "源码未打包"


def read_app_version(search_roots=None) -> str:
    roots = list(search_roots) if search_roots is not None else _default_roots()
    seen = set()
    for root in roots:
        try:
            folder = Path(root).resolve()
        except Exception:
            continue
        if folder in seen:
            continue
        seen.add(folder)
        path = folder / "VERSION"
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        if lines and lines[0].strip():
            return lines[0].strip()
    return _UNPACKAGED


def _default_roots():
    roots = []
    argv0 = sys.argv[0] if sys.argv else ""
    if argv0:
        start = Path(argv0).resolve().parent
        roots.extend([start, start.parent])
    here = Path(__file__).resolve().parent
    roots.extend([here, here.parent, here.parent.parent])
    return roots
