# -*- coding: utf-8 -*-
"""
IOT 云任务 → 桌面 UI handoff。

Agent（execution_mode=handoff）把任务写入 iot_job_inbox/pending/，
本模块在主界面定时扫描：应用参数 → 调用过载 Append → 写回 results/。
"""
from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLineEdit,
    QPlainTextEdit,
    QRadioButton,
    QTextEdit,
    QWidget,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def apply_widget_values(root_widget, values: Dict[str, Any]) -> list:
    """按 objectName 写控件。返回未找到的键列表。"""
    missing = []
    if not values:
        return missing
    for name, val in values.items():
        w = None
        if hasattr(root_widget, "findChild"):
            try:
                w = root_widget.findChild(QWidget, str(name))
            except Exception:
                w = None
        if w is None and hasattr(root_widget, str(name)):
            w = getattr(root_widget, str(name), None)
        # LazyDialog / Ui 对象：属性即控件
        if w is None:
            missing.append(str(name))
            continue
        try:
            if isinstance(w, (QTextEdit, QPlainTextEdit)):
                w.setPlainText("" if val is None else str(val))
            elif isinstance(w, QLineEdit):
                w.setText("" if val is None else str(val))
            elif isinstance(w, QCheckBox):
                w.setChecked(bool(val) if not isinstance(val, str) else val.strip() in ("1", "true", "True", "yes"))
            elif isinstance(w, QRadioButton):
                w.setChecked(bool(val) if not isinstance(val, str) else val.strip() in ("1", "true", "True", "yes"))
            elif isinstance(w, QComboBox):
                if isinstance(val, int):
                    w.setCurrentIndex(val)
                else:
                    idx = w.findText(str(val))
                    if idx >= 0:
                        w.setCurrentIndex(idx)
                    else:
                        try:
                            w.setCurrentIndex(int(val))
                        except (TypeError, ValueError):
                            missing.append(str(name))
            else:
                # 尝试常见 API
                if hasattr(w, "setPlainText"):
                    w.setPlainText(str(val))
                elif hasattr(w, "setText"):
                    w.setText(str(val))
                elif hasattr(w, "setChecked"):
                    w.setChecked(bool(val))
                elif hasattr(w, "setCurrentIndex"):
                    w.setCurrentIndex(int(val))
                else:
                    missing.append(str(name))
        except Exception:
            missing.append(str(name))
    return missing


class IotUiHandoffService(QObject):
    """挂在主窗口上的定时扫描服务。"""

    def __init__(
        self,
        *,
        repo_root: Optional[Path] = None,
        resolve_overload_ui: Optional[Callable[[], Any]] = None,
        overload_append: Optional[Callable[[], None]] = None,
        log: Optional[Callable[[str], None]] = None,
        interval_ms: int = 3000,
        parent=None,
    ):
        super().__init__(parent)
        self.repo_root = Path(repo_root) if repo_root else _repo_root()
        self.resolve_overload_ui = resolve_overload_ui
        self.overload_append = overload_append
        self._log = log or (lambda m: print(f"[IOT-handoff] {m}", flush=True))
        self._busy = False
        self._timer = QTimer(self)
        self._timer.setInterval(max(1000, int(interval_ms)))
        self._timer.timeout.connect(self.poll_once)

    def start(self) -> None:
        self._log(f"已启动，监视 {self.repo_root / 'iot_job_inbox' / 'pending'}")
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def poll_once(self) -> None:
        if self._busy:
            return
        pending_dir = self.repo_root / "iot_job_inbox" / "pending"
        if not pending_dir.is_dir():
            return
        files = sorted(pending_dir.glob("job_*.json"))
        if not files:
            return
        # 跳过已有结果的
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                self._log(f"读取失败 {path.name}: {exc}")
                continue
            job = payload.get("job") or payload
            job_id = int(job.get("id") or 0)
            if job_id <= 0:
                continue
            result_file = self.repo_root / "iot_job_inbox" / "results" / f"job_{job_id}.json"
            if result_file.is_file():
                continue
            self._busy = True
            try:
                self._handle_job(job, path)
            finally:
                self._busy = False
            break  # 一次只处理一个

    def _handle_job(self, job: dict, pending_path: Path) -> None:
        from agent.job_inbox import write_result
        from agent.ui_mutex import ui_release, ui_try_acquire

        job_id = int(job.get("id") or 0)
        test_type = str(job.get("testType") or "").strip().lower()
        self._log(f"处理任务 id={job_id} type={test_type}")

        if not ui_try_acquire(meta=f"handoff:{job_id}", repo_root=self.repo_root):
            self._log("无法占本机 UI 锁（可能 Agent 仍占用），本轮跳过")
            return

        try:
            if test_type not in ("overload", "过载能力测试", "overloads"):
                write_result(
                    self.repo_root,
                    job_id,
                    {
                        "status": "failed",
                        "fail_reason": f"UI handoff 暂不支持 testType={test_type}",
                    },
                )
                return

            ui_obj = self.resolve_overload_ui() if self.resolve_overload_ui else None
            if ui_obj is None:
                write_result(
                    self.repo_root,
                    job_id,
                    {"status": "failed", "fail_reason": "过载 UI 未就绪"},
                )
                return

            # 强制 LazyDialog 创建
            real_ui = ui_obj
            if hasattr(ui_obj, "ui"):
                try:
                    real_ui = ui_obj.ui
                except Exception:
                    real_ui = ui_obj
            if hasattr(ui_obj, "ensure"):
                try:
                    ui_obj.ensure()
                    real_ui = getattr(ui_obj, "_real_ui", None) or real_ui
                except Exception:
                    pass

            params = job.get("params") or {}
            widgets = params.get("widgets") if isinstance(params, dict) else None
            if not isinstance(widgets, dict):
                widgets = params if isinstance(params, dict) else {}
                # 去掉非控件元数据
                widgets = {
                    k: v
                    for k, v in widgets.items()
                    if k not in ("e2e", "auto_append", "auto_start", "settings_csv", "widgets")
                    and not str(k).startswith("_")
                }

            missing = apply_widget_values(real_ui, widgets)
            if missing:
                self._log(f"部分控件未写入: {missing[:12]}")

            auto_append = True
            if isinstance(params, dict) and "auto_append" in params:
                auto_append = bool(params.get("auto_append"))

            appended = False
            if auto_append and self.overload_append:
                self.overload_append()
                appended = True
                self._log("已调用 thaioverloadsAppend")

            write_result(
                self.repo_root,
                job_id,
                {
                    "status": "success",
                    "fail_reason": "",
                    "result_summary": {
                        "handoff": True,
                        "appended": appended,
                        "missingWidgets": missing,
                        "note": "已应用参数并追加命令；完整启停试验可后续扩展 auto_start",
                    },
                    "report_meta": [],
                },
            )
            self._log(f"任务 {job_id} 已写回 results")
            # 可选：处理完移动 pending
            try:
                done_dir = self.repo_root / "iot_job_inbox" / "done"
                done_dir.mkdir(parents=True, exist_ok=True)
                pending_path.replace(done_dir / pending_path.name)
            except OSError:
                pass
        except Exception as exc:
            self._log(f"处理失败: {exc}\n{traceback.format_exc()}")
            try:
                write_result(
                    self.repo_root,
                    job_id,
                    {"status": "failed", "fail_reason": str(exc)[:500]},
                )
            except Exception:
                pass
        finally:
            ui_release(repo_root=self.repo_root)


def start_iot_ui_handoff_from_main(
    *,
    resolve_overload_ui: Callable[[], Any],
    overload_append: Callable[[], None],
    log: Optional[Callable[[str], None]] = None,
    parent=None,
) -> IotUiHandoffService:
    svc = IotUiHandoffService(
        resolve_overload_ui=resolve_overload_ui,
        overload_append=overload_append,
        log=log,
        parent=parent,
    )
    # 稍晚启动，等主界面事件循环稳定
    QTimer.singleShot(2500, svc.start)
    return svc
