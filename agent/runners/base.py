# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Protocol


ProgressCb = Callable[[int, str, str], None]


class JobRunner(Protocol):
    def run(self, job: Dict[str, Any], on_progress: ProgressCb) -> Dict[str, Any]:
        """
        执行任务。返回 dict:
          status: success|failed|aborted
          fail_reason: str
          result_summary: dict
          report_meta: list
        """
        ...


@dataclass
class RunResult:
    status: str
    fail_reason: str = ""
    result_summary: Optional[Dict[str, Any]] = None
    report_meta: Optional[list] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "fail_reason": self.fail_reason,
            "result_summary": self.result_summary or {},
            "report_meta": self.report_meta or [],
        }
