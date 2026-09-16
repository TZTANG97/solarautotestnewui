# -*- coding: utf-8 -*-
"""软件急停：按关电源规则关输出并中止试验（可单测）。"""
from __future__ import annotations

from typing import Callable, Optional

ESTOP_LOG_ZH = "[急停] 软件急停已执行（直流先关→交流）"
ESTOP_FAIL_REASON_ZH = "软件急停"
ESTOP_CONFIRM_ZH = "确认软件急停？将立即按关电源规则关闭输出并中止试验"


def estop_software(
    *,
    force_off: Callable[[], None],
    end_project: Callable[[], None],
    notify_handoff: Optional[Callable[[], None]] = None,
    log: Optional[Callable[[str], None]] = None,
) -> None:
    """先关输出，再中止试验；可选通知 IOT handoff 结案。

    调用顺序固定：force_off → end_project → notify_handoff → log。
    """
    force_off()
    end_project()
    if notify_handoff is not None:
        try:
            notify_handoff()
        except Exception:
            pass
    if log is not None:
        try:
            log(ESTOP_LOG_ZH)
        except Exception:
            pass
