# -*- coding: utf-8 -*-
"""
IOT 云任务 → 桌面 UI handoff。

Agent（execution_mode=handoff）把任务写入 iot_job_inbox/pending/，
本模块在主界面定时扫描：应用参数 → 调用过载 Append →（可选）开始试验 →
等试验结束再写回 results/。
"""
from __future__ import annotations

import json
import time
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

    # testType 别名 → (项目中文名, handler_key)
    _TYPE_MAP = {
        "overload": ("过载能力测试", "overload"),
        "overloads": ("过载能力测试", "overload"),
        "过载能力测试": ("过载能力测试", "overload"),
        "antibackflow": ("防逆流测试", "antibackflow"),
        "anti_backflow": ("防逆流测试", "antibackflow"),
        "防逆流测试": ("防逆流测试", "antibackflow"),
        "防逆流": ("防逆流测试", "antibackflow"),
    }

    def __init__(
        self,
        *,
        repo_root: Optional[Path] = None,
        resolve_overload_ui: Optional[Callable[[], Any]] = None,
        overload_append: Optional[Callable[[], None]] = None,
        resolve_antibackflow_ui: Optional[Callable[[], Any]] = None,
        antibackflow_append: Optional[Callable[[], None]] = None,
        start_test: Optional[Callable[[], None]] = None,
        get_run_status: Optional[Callable[[], str]] = None,
        get_run_progress: Optional[Callable[[], Dict[str, Any]]] = None,
        ensure_project: Optional[Callable[[str], None]] = None,
        log: Optional[Callable[[str], None]] = None,
        interval_ms: int = 3000,
        parent=None,
    ):
        super().__init__(parent)
        self.repo_root = Path(repo_root) if repo_root else _repo_root()
        self.resolve_overload_ui = resolve_overload_ui
        self.overload_append = overload_append
        self.resolve_antibackflow_ui = resolve_antibackflow_ui
        self.antibackflow_append = antibackflow_append
        self.start_test = start_test
        self.get_run_status = get_run_status
        self.get_run_progress = get_run_progress
        self.ensure_project = ensure_project
        self._log = log or (lambda m: print(f"[IOT-handoff] {m}", flush=True))
        self._busy = False
        self._awaiting: Optional[Dict[str, Any]] = None
        self._timer = QTimer(self)
        self._timer.setInterval(max(1000, int(interval_ms)))
        self._timer.timeout.connect(self.poll_once)
        self._last_progress_key = None

    def start(self) -> None:
        watched = " ; ".join(str(d / "pending") for d in self._inbox_dirs())
        self._log(f"已启动，监视 {watched}")
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def _inbox_dirs(self) -> list:
        """安装根 iot_job_inbox 优先；兼容旧 Agent 误写到 agent/iot_job_inbox。"""
        primary = self.repo_root / "iot_job_inbox"
        legacy = self.repo_root / "agent" / "iot_job_inbox"
        out = [primary]
        if legacy.resolve() != primary.resolve():
            out.append(legacy)
        return out

    def _write_roots_for(self, pending_path: Optional[Path]) -> list:
        """结案/进度写入安装根；若 pending 来自旧 agent/ 目录则双写，让旧 Agent wait_result 能收到。"""
        roots = [self.repo_root]
        if pending_path is not None:
            try:
                parts = set(Path(pending_path).resolve().parts)
            except OSError:
                parts = set(Path(pending_path).parts)
            if "agent" in parts and "iot_job_inbox" in parts:
                legacy_root = self.repo_root / "agent"
                if legacy_root.resolve() != self.repo_root.resolve():
                    roots.append(legacy_root)
        return roots

    def _write_result_all(self, pending_path: Optional[Path], job_id: int, result: Dict[str, Any]) -> None:
        from agent.job_inbox import write_result

        for root in self._write_roots_for(pending_path):
            write_result(root, job_id, result)

    def poll_once(self) -> None:
        if self._awaiting:
            self._check_awaiting_finish()
            return
        if self._busy:
            return
        for inbox in self._inbox_dirs():
            pending_dir = inbox / "pending"
            if not pending_dir.is_dir():
                continue
            files = sorted(pending_dir.glob("job_*.json"))
            if not files:
                continue
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
                already = False
                for root in self._write_roots_for(path):
                    if (root / "iot_job_inbox" / "results" / f"job_{job_id}.json").is_file():
                        already = True
                        break
                if already:
                    continue
                self._busy = True
                try:
                    self._handle_job(job, path)
                finally:
                    if not self._awaiting:
                        self._busy = False
                return


    def _read_run_status(self) -> str:
        if not self.get_run_status:
            return ""
        try:
            return str(self.get_run_status() or "").strip()
        except Exception as exc:
            self._log(f"读取试验状态失败: {exc}")
            return ""

    def _emit_progress(self, job_id: int, *, force: bool = False) -> None:
        from agent.job_inbox import write_progress

        percent = 15
        text = "试验进行中"
        step = "running"
        if self.get_run_progress:
            try:
                snap = self.get_run_progress() or {}
                if isinstance(snap, dict):
                    if snap.get("percent") is not None:
                        percent = int(snap.get("percent") or 0)
                    if snap.get("text"):
                        text = str(snap.get("text"))
                    if snap.get("step"):
                        step = str(snap.get("step"))
            except Exception as exc:
                self._log(f"读取进度失败: {exc}")
        key = (percent, text, step)
        if not force and key == self._last_progress_key:
            return
        self._last_progress_key = key
        pending = None
        if self._awaiting:
            pending = self._awaiting.get("pending_path")
        try:
            for root in self._write_roots_for(pending):
                write_progress(root, job_id, percent=percent, text=text, step=step)
        except Exception as exc:
            self._log(f"写进度失败: {exc}")

    def _resolve_handler(self, test_type: str):
        raw = str(test_type or "").strip()
        key = raw.lower() if raw.isascii() else raw
        mapped = self._TYPE_MAP.get(key) or self._TYPE_MAP.get(raw)
        if not mapped:
            return None
        project_name, handler_key = mapped
        if handler_key == "overload":
            return {
                "project_name": project_name,
                "resolve_ui": self.resolve_overload_ui,
                "append": self.overload_append,
                "label": "过载",
            }
        if handler_key == "antibackflow":
            return {
                "project_name": project_name,
                "resolve_ui": self.resolve_antibackflow_ui,
                "append": self.antibackflow_append,
                "label": "防逆流",
            }
        return None

    def _move_pending_done(self, pending_path: Path) -> None:
        try:
            done_dir = self.repo_root / "iot_job_inbox" / "done"
            done_dir.mkdir(parents=True, exist_ok=True)
            pending_path.replace(done_dir / pending_path.name)
        except OSError:
            pass

    def _attach_report_files(self, result: Dict[str, Any], job_id: int) -> None:
        """结案时把本机近期试验产出路径写入 result_summary.report_files，供 Agent 上传。"""
        try:
            from agent.reports import collect_report_files
        except Exception:
            return
        summary = result.get("result_summary")
        if not isinstance(summary, dict):
            summary = {}
            result["result_summary"] = summary
        from agent.job_inbox import write_result

        pending = None
        if self._awaiting:
            pending = self._awaiting.get("pending_path")
        for root in self._write_roots_for(pending):
            write_result(root, job_id, result)
        paths = collect_report_files(self.repo_root, job_id, result)
        listed = []
        for p in paths:
            try:
                listed.append(str(p.resolve()))
            except OSError:
                listed.append(str(p))
        if listed:
            summary["report_files"] = listed
            result["result_summary"] = summary
            for root in self._write_roots_for(pending):
                write_result(root, job_id, result)

    def _finish_job(
        self,
        *,
        job_id: int,
        pending_path: Optional[Path],
        result: Dict[str, Any],
        release_ui: bool = True,
    ) -> None:
        from agent.job_inbox import write_result
        from agent.ui_mutex import ui_release

        try:
            self._attach_report_files(result, job_id)
        except Exception:
            for root in self._write_roots_for(pending_path):
                write_result(root, job_id, result)
        self._log(f"任务 {job_id} 已写回 results status={result.get('status')}")
        if pending_path is not None:
            self._move_pending_done(pending_path)
        self._awaiting = None
        self._busy = False
        if release_ui:
            ui_release(repo_root=self.repo_root)

    def _check_awaiting_finish(self) -> None:
        aw = self._awaiting
        if not aw:
            return
        job_id = int(aw["job_id"])
        pending_path = aw.get("pending_path")
        now = time.time()
        elapsed = now - float(aw.get("started_at") or now)
        status = self._read_run_status()
        start_grace = float(aw.get("start_grace_sec") or 20)
        timeout = float(aw.get("timeout_sec") or 7200)

        if status == "进行中":
            if not aw.get("seen_running"):
                aw["seen_running"] = True
                self._log(f"任务 {job_id} 已进入进行中")
            self._emit_progress(job_id)
            return

        if status == "已结束":
            if not aw.get("seen_running") and elapsed < start_grace:
                # 可能仍是上一轮残留状态，再等片刻看是否进入「进行中」
                return
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "success",
                    "fail_reason": "",
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": True,
                        "waited_finish": True,
                        "run_status": status,
                        "elapsed_sec": round(elapsed, 1),
                        "missingWidgets": aw.get("missing") or [],
                        "note": "试验已正常结束并回传",
                    },
                    "report_meta": [],
                },
            )
            return

        if status in ("已中止", "失败"):
            if not aw.get("seen_running") and elapsed < start_grace:
                return
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "aborted" if status == "已中止" else "failed",
                    "fail_reason": f"试验状态={status}",
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": bool(aw.get("seen_running")),
                        "waited_finish": True,
                        "run_status": status,
                        "elapsed_sec": round(elapsed, 1),
                        "missingWidgets": aw.get("missing") or [],
                    },
                    "report_meta": [],
                },
            )
            return

        if not aw.get("seen_running") and elapsed >= start_grace:
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "failed",
                    "fail_reason": (
                        f"开始试验后 {int(start_grace)}s 内未进入「进行中」"
                        f"（当前状态={status or '空'}），可能启动被拦截"
                    ),
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": False,
                        "waited_finish": True,
                        "run_status": status,
                        "missingWidgets": aw.get("missing") or [],
                    },
                    "report_meta": [],
                },
            )
            return

        if elapsed >= timeout:
            self._finish_job(
                job_id=job_id,
                pending_path=pending_path,
                result={
                    "status": "failed",
                    "fail_reason": f"等待试验结束超时（{int(timeout)}s），当前状态={status or '空'}",
                    "result_summary": {
                        "handoff": True,
                        "appended": aw.get("appended"),
                        "started": bool(aw.get("seen_running")),
                        "waited_finish": True,
                        "run_status": status,
                        "missingWidgets": aw.get("missing") or [],
                    },
                    "report_meta": [],
                },
            )

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
            handler = self._resolve_handler(test_type)
            if not handler:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {
                        "status": "failed",
                        "fail_reason": f"UI handoff 暂不支持 testType={test_type}",
                    },
                )
                self._move_pending_done(pending_path)
                return

            if self.ensure_project:
                try:
                    self.ensure_project(handler["project_name"])
                except Exception as exc:
                    self._log(f"切换项目失败: {exc}")

            resolve_ui = handler.get("resolve_ui")
            ui_obj = resolve_ui() if resolve_ui else None
            if ui_obj is None:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {"status": "failed", "fail_reason": f"{handler['label']} UI 未就绪"},
                )
                self._move_pending_done(pending_path)
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
                    if k not in (
                        "e2e",
                        "auto_append",
                        "auto_start",
                        "wait_finish",
                        "wait_finish_timeout_sec",
                        "start_grace_sec",
                        "settings_csv",
                        "widgets",
                    )
                    and not str(k).startswith("_")
                }

            missing = apply_widget_values(real_ui, widgets)
            if missing:
                self._log(f"部分控件未写入: {missing[:12]}")

            auto_append = True
            if isinstance(params, dict) and "auto_append" in params:
                auto_append = bool(params.get("auto_append"))
            auto_start = False
            if isinstance(params, dict) and "auto_start" in params:
                auto_start = bool(params.get("auto_start"))
            wait_finish = True
            if isinstance(params, dict) and "wait_finish" in params:
                wait_finish = bool(params.get("wait_finish"))

            appended = False
            project_append = handler.get("append")
            if auto_append and project_append:
                project_append()
                appended = True
                self._log(f"已调用 {handler['label']} Append")

            if auto_start:
                if not self.start_test:
                    self._write_result_all(
                        pending_path,
                        job_id,
                        {
                            "status": "failed",
                            "fail_reason": "auto_start=true 但未绑定开始试验回调",
                            "result_summary": {"appended": appended},
                        },
                    )
                    self._move_pending_done(pending_path)
                    return
                self.start_test()
                self._log("已调用开始试验 RunProjectPush")

                if wait_finish:
                    timeout_sec = 7200.0
                    start_grace_sec = 20.0
                    if isinstance(params, dict):
                        if params.get("wait_finish_timeout_sec") is not None:
                            timeout_sec = float(params.get("wait_finish_timeout_sec"))
                        if params.get("start_grace_sec") is not None:
                            start_grace_sec = float(params.get("start_grace_sec"))
                    self._awaiting = {
                        "job_id": job_id,
                        "pending_path": pending_path,
                        "appended": appended,
                        "missing": missing,
                        "started_at": time.time(),
                        "seen_running": False,
                        "timeout_sec": timeout_sec,
                        "start_grace_sec": start_grace_sec,
                    }
                    self._last_progress_key = None
                    self._emit_progress(job_id, force=True)
                    self._log(
                        f"任务 {job_id} 等待试验结束（timeout={int(timeout_sec)}s，"
                        f"start_grace={int(start_grace_sec)}s）"
                    )
                    # 立刻检查一次（短试验 / 单测模拟）
                    self._check_awaiting_finish()
                    return

            self._write_result_all(
                pending_path,
                job_id,
                {
                    "status": "success",
                    "fail_reason": "",
                    "result_summary": {
                        "handoff": True,
                        "appended": appended,
                        "started": bool(auto_start),
                        "waited_finish": False,
                        "missingWidgets": missing,
                        "note": (
                            "已追加并启动试验（未等待结束，wait_finish=false）"
                            if auto_start
                            else "已应用参数并追加命令；params.auto_start=true 时可自动开始试验"
                        ),
                    },
                    "report_meta": [],
                },
            )
            self._log(f"任务 {job_id} 已写回 results")
            self._move_pending_done(pending_path)
        except Exception as exc:
            self._log(f"处理失败: {exc}\n{traceback.format_exc()}")
            self._awaiting = None
            try:
                self._write_result_all(
                    pending_path,
                    job_id,
                    {"status": "failed", "fail_reason": str(exc)[:500]},
                )
            except Exception:
                pass
        finally:
            if not self._awaiting:
                ui_release(repo_root=self.repo_root)


def start_iot_ui_handoff_from_main(
    *,
    resolve_overload_ui: Callable[[], Any],
    overload_append: Callable[[], None],
    resolve_antibackflow_ui: Optional[Callable[[], Any]] = None,
    antibackflow_append: Optional[Callable[[], None]] = None,
    start_test: Optional[Callable[[], None]] = None,
    get_run_status: Optional[Callable[[], str]] = None,
    get_run_progress: Optional[Callable[[], Dict[str, Any]]] = None,
    ensure_project: Optional[Callable[[str], None]] = None,
    log: Optional[Callable[[str], None]] = None,
    parent=None,
) -> IotUiHandoffService:
    svc = IotUiHandoffService(
        resolve_overload_ui=resolve_overload_ui,
        overload_append=overload_append,
        resolve_antibackflow_ui=resolve_antibackflow_ui,
        antibackflow_append=antibackflow_append,
        start_test=start_test,
        get_run_status=get_run_status,
        get_run_progress=get_run_progress,
        ensure_project=ensure_project,
        log=log,
        parent=parent,
    )
    # 稍晚启动，等主界面事件循环稳定
    QTimer.singleShot(2500, svc.start)
    return svc
