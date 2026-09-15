# -*- coding: utf-8 -*-
"""本机互斥：云任务 vs 本地 UI 手动试验。"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional


class LocalMutex:
    """
    基于文件的简单互斥（同机多进程约定）。
    - Agent 执行云任务前 acquire(owner=\"agent\")
    - 桌面 UI 手动开测前可 acquire(owner=\"ui\")（后续接入）
    - 对方已占用则失败
    """

    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> Optional[dict]:
        if not self.path.is_file():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def is_held_by_other(self, owner: str) -> Optional[str]:
        data = self._read()
        if not data:
            return None
        held = str(data.get("owner") or "")
        if held and held != owner:
            return held
        return None

    def acquire(self, owner: str, meta: str = "") -> bool:
        other = self.is_held_by_other(owner)
        if other:
            return False
        payload = {
            "owner": owner,
            "pid": os.getpid(),
            "meta": meta or "",
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return True

    def release(self, owner: str) -> None:
        data = self._read()
        if not data:
            return
        if str(data.get("owner") or "") != owner:
            return
        try:
            self.path.unlink(missing_ok=True)
        except TypeError:
            # py3.7 无 missing_ok；本项目 >=3.14
            if self.path.is_file():
                self.path.unlink()
        except OSError:
            pass
