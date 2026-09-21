# -*- coding: utf-8 -*-
"""云端下发仪器操作时，禁止桌面弹出模态框（否则主界面会一直卡住）。"""
from __future__ import annotations

_depth = 0


def remote_connect_silent() -> bool:
    return _depth > 0


class silent_remote_connect:
    def __enter__(self):
        global _depth
        _depth += 1
        return self

    def __exit__(self, exc_type, exc, tb):
        global _depth
        _depth = max(0, _depth - 1)
        return False
