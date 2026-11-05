# -*- coding: utf-8 -*-
"""台架本地开测 → IOT 登记实验/任务。

Web 开测走 handoff（云端已建实验）；本地点「开始」原先不登记，
导致 IOT 实验管理无记录。本模块在 RunProjectPush / 结束时补登记。
云端 handoff 等待中（_awaiting）则跳过，避免重复建局。
"""
from __future__ import annotations

import json
import logging
import sys
import threading
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_state: Dict[str, Any] = {"job_id": None, "exper_id": None}


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _scpi_mod():
    """取正在跑的主程序模块。

    ``python SCPITestWave.py`` 时运行态在 ``__main__``；若再 ``import SCPITestWave``
    会加载第二份空壳，读不到 ``_iot_ui_handoff_svc``，云单会被秒成功并另建 local_ui。
    """
    preferred = None
    for name in ("__main__", "SCPITestWave"):
        mod = sys.modules.get(name)
        if mod is None:
            continue
        if getattr(mod, "_iot_ui_handoff_svc", None) is not None:
            return mod
        if preferred is None and (
            getattr(mod, "ui", None) is not None
            or hasattr(mod, "strArrayTest")
            or hasattr(mod, "RunProjectPush")
        ):
            preferred = mod
    if preferred is not None:
        return preferred
    try:
        import SCPITestWave as sw  # noqa: WPS433 — 仅测试/非桌面入口兜底

        return sw
    except Exception:
        return None


def handoff_has_awaiting_job() -> bool:
    """云端 handoff 正在处理或已占用当前试验局时返回 True。

    start_test() 调用时 _awaiting 尚未写入，但 _job_ctx 已在；
    两者任一存在都说明本局由云端任务登记，本地勿再创建实验。
    """
    try:
        sw = _scpi_mod()
        if sw is None:
            return False
        svc = getattr(sw, "_iot_ui_handoff_svc", None)
        if svc is None:
            return False
        if getattr(svc, "_job_ctx", None):
            return True
        aw = getattr(svc, "_awaiting", None)
        if not aw:
            return False
        try:
            return int(aw.get("job_id") or 0) > 0
        except (TypeError, ValueError):
            return True
    except Exception:
        return False


def current_local_job_id() -> Optional[int]:
    with _lock:
        jid = _state.get("job_id")
    try:
        return int(jid) if jid else None
    except (TypeError, ValueError):
        return None


def _job_id_from_status_json() -> Optional[int]:
    """内存态丢失时，从 status.json.project.jobId 找回本地任务。"""
    try:
        path = _repo_root() / "status.json"
        if not path.is_file():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        proj = raw.get("project") if isinstance(raw, dict) else None
        if not isinstance(proj, dict):
            return None
        jid = int(proj.get("jobId") or 0)
        return jid if jid > 0 else None
    except Exception:
        return None


def _persist_local_job_ids(job_id: int, exper_id: Optional[int] = None) -> None:
    """把本地登记的 job/exper 写入 status.json，供 Agent 心跳与结案兜底。"""
    try:
        path = _repo_root() / "status.json"
        from utils.status_json_devices import status_json_lock, status_when_binding_new_job

        with status_json_lock(str(path)):
            try:
                data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
            except Exception:
                data = {}
            if not isinstance(data, dict):
                data = {}
            proj = data.get("project")
            if not isinstance(proj, dict):
                proj = {}
            proj = dict(proj)
            proj["status"] = status_when_binding_new_job(str(proj.get("status") or ""))
            proj["jobId"] = int(job_id)
            if exper_id:
                proj["experId"] = int(exper_id)
            data["project"] = proj
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        logger.debug("写入 status.json jobId 失败", exc_info=True)


def _build_client():
    from agent.client import IotSolarClient
    from agent.config import load_config

    cfg = load_config()
    if not cfg.agent_token or str(cfg.agent_token).startswith("请填写"):
        raise RuntimeError("无有效 agent_token，无法向 IOT 登记本地试验")
    pythonid = ""
    try:
        raw_path = _repo_root() / "config" / "solar_agent.json"
        if raw_path.is_file():
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            pythonid = str(raw.get("pythonid") or raw.get("pythonId") or "").strip()
    except Exception:
        pythonid = ""
    return IotSolarClient(cfg.iot_base, cfg.agent_token, pythonid=pythonid)


def _ui_log(msg: str) -> None:
    """后台线程只打日志，避免跨线程碰 Qt 控件。"""
    logger.info(msg)
    print(msg, flush=True)


def _do_start(
    test_name: str,
    widgets: Optional[Dict[str, Any]] = None,
    run_commands: Optional[list] = None,
    blockly_code: str = "",
    blockly_xml: str = "",
) -> None:
    try:
        client = _build_client()
        data = client.local_run_start(
            test_type=test_name,
            title=test_name,
            widgets=widgets,
            run_commands=run_commands,
            blockly_code=blockly_code,
            blockly_xml=blockly_xml,
        )
        job_id = int(data.get("jobId") or data.get("id") or 0)
        exper_id = int(data.get("experimentId") or data.get("experid") or 0)
        if job_id <= 0:
            raise RuntimeError(f"IOT 未返回 jobId: {data!r}")
        with _lock:
            _state["job_id"] = job_id
            _state["exper_id"] = exper_id or None
        _persist_local_job_ids(job_id, exper_id or None)
        msg = (
            f"[IOT] 本地开测已登记实验 #{exper_id} / 任务 #{job_id}"
            if exper_id
            else f"[IOT] 本地开测已登记任务 #{job_id}"
        )
        logger.info(msg)
        _ui_log(msg)
    except Exception as exc:
        logger.info("本地开测 IOT 登记失败（试验仍继续）: %s", exc, exc_info=True)
        _ui_log(f"[IOT] 本地开测登记失败（试验仍继续）: {exc}")


def _do_done(job_id: int, aborted: bool) -> None:
    try:
        client = _build_client()
        status = "aborted" if aborted else "success"
        reason = "台架本地中止" if aborted else ""
        client.done(job_id, status=status, fail_reason=reason)
        logger.info("[IOT] 本地任务 #%s 已结案 status=%s", job_id, status)
        _ui_log(f"[IOT] 本地任务 #{job_id} 已结案（{status}）")
    except Exception as exc:
        logger.info("本地结案上报失败: %s", exc, exc_info=True)
        _ui_log(f"[IOT] 本地结案上报失败: {exc}")
    finally:
        with _lock:
            if _state.get("job_id") == job_id:
                _state["job_id"] = None
                _state["exper_id"] = None


_QUEUE_OPEN = frozenset({"等待", "进行中", "暂停", "运行", "测试中"})


def clear_status_job_binding() -> None:
    """去掉 status.json 上的任务号，避免心跳继续把新进度写到上一单。

    本机未在跑时顺带丢掉已结束/已中止的 queue 段，避免新云任务详情挂上上一局。
    """
    with _lock:
        _state["job_id"] = None
        _state["exper_id"] = None
    try:
        path = _repo_root() / "status.json"
        if not path.is_file():
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return
        proj = data.get("project")
        if not isinstance(proj, dict):
            return
        proj.pop("jobId", None)
        proj.pop("job_id", None)
        proj.pop("experId", None)
        # 空闲换绑：清终态队列；仍在跑则只解绑 jobId
        if not desktop_run_in_progress():
            queue = proj.get("queue")
            if isinstance(queue, list):
                kept = [
                    it
                    for it in queue
                    if isinstance(it, dict)
                    and str(it.get("status") or "").strip() in _QUEUE_OPEN
                ]
                if kept != queue:
                    proj["queue"] = kept
        data["project"] = proj
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        logger.debug("清除 status.json 任务号失败", exc_info=True)


def _local_run_flag() -> str:
    try:
        sw = _scpi_mod()
        if sw is None:
            return ""
        return str(getattr(sw, "strTestStatusFlag", "") or "").strip()
    except Exception:
        return ""


def desktop_run_in_progress() -> bool:
    """本机命令队列仍在跑（含暂停）时，禁止新开/强结上一单。"""
    return _local_run_flag() in ("运行", "暂停")


_PROGRESS_RUNNING = ("进行中", "暂停", "人工等待")


def bench_is_running(progress_status: str = "") -> bool:
    """执行标志或进度条任一显示在跑，都算台架占用。

    刚点开始时进度可能已是「进行中」，``strTestStatusFlag`` 还没写成「运行」。
    只看其中一边会在这个窗口里改绑任务号并再点一次开始。
    """
    if desktop_run_in_progress():
        return True
    return str(progress_status or "").strip() in _PROGRESS_RUNNING


def desktop_queue_nonempty() -> bool:
    """桌面已经追加过、命令还在队列里（含尚未点开始）。"""
    try:
        sw = _scpi_mod()
        if sw is None:
            return False
        return bool(getattr(sw, "strArrayTest", None))
    except Exception:
        return False


def _status_json_project() -> Dict[str, Any]:
    try:
        path = _repo_root() / "status.json"
        if not path.is_file():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        proj = raw.get("project") if isinstance(raw, dict) else None
        return dict(proj) if isinstance(proj, dict) else {}
    except Exception:
        return {}


def release_previous_cloud_job_for_new_round() -> Optional[int]:
    """桌面不在跑、且不是云端这次交接本身时，结案仍挂着的上一云任务。

    本机仍在「运行/暂停」或 status.json 仍是进行中时，绝不强结成功——
    否则中途追加再点开始会把还在跑的上一单（如静态QU）误标成成功。
    """
    try:
        sw = _scpi_mod()
        svc = getattr(sw, "_iot_ui_handoff_svc", None) if sw is not None else None
    except Exception:
        svc = None
    if desktop_run_in_progress():
        return None
    proj = _status_json_project()
    local_status = str(proj.get("status") or "").strip()
    if local_status in ("进行中", "暂停", "运行"):
        logger.info(
            "跳过结案上一云任务：status.json 仍为 %s（本机队列未真正结束）",
            local_status,
        )
        return None
    if svc is not None and getattr(svc, "_job_ctx", None):
        return None
    job_id = None
    if svc is not None and hasattr(svc, "finish_awaiting_as_new_round"):
        try:
            job_id = svc.finish_awaiting_as_new_round()
        except Exception:
            logger.info("结案上一云任务失败", exc_info=True)
            job_id = None
    if not job_id:
        job_id = _job_id_from_status_json()
        if job_id:
            aborted = local_status in ("已中止", "失败", "中止")
            try:
                from agent.job_inbox import write_result

                write_result(
                    _repo_root(),
                    int(job_id),
                    {
                        "status": "aborted" if aborted else "success",
                        "fail_reason": "台架本地中止" if aborted else "",
                        "result_summary": {
                            "note": (
                                "本机已另行开测，上一云任务按中止结案"
                                if aborted
                                else "本机已另行开测，上一云任务按完成结案"
                            ),
                        },
                    },
                )
            except Exception:
                logger.debug("写上一云任务结果失败", exc_info=True)
            threading.Thread(
                target=_do_done,
                args=(int(job_id), bool(aborted)),
                daemon=True,
                name="iot-close-previous-job",
            ).start()
    clear_status_job_binding()
    return int(job_id) if job_id else None


def handoff_start_in_progress() -> bool:
    """云端交接正在调用开始试验。此时不要再登记一条本地任务。"""
    try:
        sw = _scpi_mod()
        if sw is None:
            return False
        svc = getattr(sw, "_iot_ui_handoff_svc", None)
        if svc is None:
            return False
        ctx = getattr(svc, "_job_ctx", None)
        return isinstance(ctx, dict) and int(ctx.get("job_id") or 0) > 0
    except Exception:
        return False


def _handoff_keep_job_id() -> int:
    """云端正在交接/等待结束的任务号；开跑时不能把它当「上一单」摘掉。"""
    try:
        sw = _scpi_mod()
        if sw is None:
            return 0
        svc = getattr(sw, "_iot_ui_handoff_svc", None)
        if svc is None:
            return 0
        fn = getattr(svc, "_current_handoff_job_id", None)
        if callable(fn):
            return int(fn() or 0)
        for src in (getattr(svc, "_awaiting", None), getattr(svc, "_job_ctx", None)):
            if isinstance(src, dict):
                jid = int(src.get("job_id") or 0)
                if jid > 0:
                    return jid
    except Exception:
        return 0
    return 0


def detach_previous_job_for_fresh_start(*, keep_job_id: int = 0) -> Optional[int]:
    """新开一局之前摘掉上一单号，并清掉它留下的远程停机。

    软件重新打开后，status.json 往往还挂着途哲这台的上一单。
    点开始会先把进度写成「进行中」。若这时心跳仍读到旧任务号，
    而云端那一单已经是 aborted，就会写成远程停机，把刚开始的闪变停掉。

    注意：IOT 云任务开跑时 status/awaiting 已是本单 jobId（如 106）。
    若把本单记进 superseded，随后网页中止 106 会被「忽略上一单停机」。
    """
    if desktop_run_in_progress():
        return None
    try:
        keep = int(keep_job_id or 0)
    except (TypeError, ValueError):
        keep = 0
    if keep <= 0:
        keep = _handoff_keep_job_id()
    old = current_local_job_id() or _job_id_from_status_json()
    from agent.job_inbox import (
        ack_stop_request,
        forget_superseded_job,
        is_superseded_job,
        list_stop_requests,
        remember_superseded_job,
    )

    root = _repo_root()
    try:
        old_i = int(old) if old else 0
    except (TypeError, ValueError):
        old_i = 0
    if old_i > 0 and old_i != keep:
        remember_superseded_job(root, old_i)
    elif old_i > 0 and old_i == keep:
        # 本单被误记为上一单时摘掉，保证 IOT 中止生效
        forget_superseded_job(root, old_i)
    for req in list_stop_requests(root):
        try:
            jid = int(req.get("job_id") or 0)
        except (TypeError, ValueError):
            jid = 0
        if jid <= 0:
            continue
        if keep > 0 and jid == keep:
            # 保留当前任务的停机单，交给 handoff 执行
            continue
        if is_superseded_job(root, jid):
            ack_stop_request(root, jid)
            continue
        remember_superseded_job(root, jid)
        ack_stop_request(root, jid)
    if keep <= 0 or (old_i > 0 and old_i != keep):
        clear_status_job_binding()
    if old_i > 0 and old_i != keep:
        _ui_log(f"[IOT] 新开试验前已摘掉上一单 #{old_i}，它的远程停机不再作用到这一局")
    elif old_i > 0 and old_i == keep:
        _ui_log(f"[IOT] 保持当前云任务 #{keep}，不将其标为上一单")
    return old_i if old_i > 0 else None


def notify_local_run_started(
    test_name: str,
    widgets: Optional[Dict[str, Any]] = None,
    *,
    run_commands: Optional[list] = None,
    blockly_code: str = "",
    blockly_xml: str = "",
) -> None:
    """UI 线程调用：后台登记；handoff 占用时跳过。

    widgets / run_commands / blockly_* 应来自本机当前局实际 Dialog 与 strArrayTest，
    一并上报供 IOT 实验 Blockly 与步骤快照使用。
    """
    if handoff_start_in_progress():
        logger.info("[iot_local_run] handoff 正在开测，跳过本地登记")
        return
    # 云端正在等本局结束：本局归属该云任务。若此时再 local_run_start，
    # 会把云单按「本机已另行开测」秒成功，并再新建一条 local_ui（job100/101 双单）。
    if handoff_has_awaiting_job():
        jid = None
        try:
            sw = _scpi_mod()
            aw = getattr(getattr(sw, "_iot_ui_handoff_svc", None), "_awaiting", None) or {}
            jid = int(aw.get("job_id") or 0) or None
        except Exception:
            jid = current_local_job_id() or _job_id_from_status_json()
        logger.info(
            "[iot_local_run] handoff 等待结案中，跳过本地登记（沿用云任务 #%s）",
            jid or "?",
        )
        _ui_log(
            f"[IOT] 云端任务执行中"
            f"{f' #{jid}' if jid else ''}，不另建本机任务"
        )
        return
    if not desktop_run_in_progress():
        # 进度已经写成进行中时，RunProject 里已经摘过上一单。
        # 这里再摘会把刚绑定的任务号清掉，心跳又读到终态。
        try:
            from utils.status_json_devices import project_status_is_live_local_run

            live = project_status_is_live_local_run(
                getattr(__import__("SCPITestWave"), "_run_progress_state", None),
                _local_run_flag(),
            )
        except Exception:
            live = False
        if not live:
            try:
                detach_previous_job_for_fresh_start()
            except Exception:
                logger.debug("新开试验前摘掉上一单失败", exc_info=True)
    # 中途追加后再点开始：命令已在同一 RunProject 队列里继续跑，
    # 绝不能再 local_run_start，否则服务端会把还在跑的上一单结掉。
    if desktop_run_in_progress():
        jid = current_local_job_id() or _job_id_from_status_json()
        logger.info(
            "[iot_local_run] 本机仍在执行中，跳过新开任务（保持 job #%s）",
            jid or "?",
        )
        _ui_log(
            f"[IOT] 试验仍在执行中，追加项并入当前任务"
            f"{f' #{jid}' if jid else ''}，不新开一单"
        )
        return
    # 只剩上一单的等待结案：先结掉，这次开始才是新任务
    try:
        release_previous_cloud_job_for_new_round()
    except Exception:
        logger.debug("开测前结案上一云任务跳过", exc_info=True)
    name = (test_name or "").strip() or "本地实验"
    try:
        from utils.iot_run_upload import enrich_widgets_for_upload

        w = enrich_widgets_for_upload(widgets if isinstance(widgets, dict) else None)
    except Exception:
        w = dict(widgets) if isinstance(widgets, dict) else None
    cmds = list(run_commands) if isinstance(run_commands, list) else None
    code = (blockly_code or "").strip()
    xml = (blockly_xml or "").strip()
    threading.Thread(
        target=_do_start,
        args=(name, w, cmds, code, xml),
        daemon=True,
        name="iot-local-run-start",
    ).start()


def adopt_cloud_job(job_id: int, exper_id: Optional[int] = None) -> None:
    """云端任务开跑：丢掉上一单本地号，立刻把 status.json 写成这一单。

    否则心跳仍读到上一单（例如 67），当前单 69 的远程中止和结案会对不上。
    """
    try:
        jid = int(job_id)
    except (TypeError, ValueError):
        return
    if jid <= 0:
        return
    with _lock:
        prev = _state.get("job_id")
        try:
            prev_id = int(prev) if prev else 0
        except (TypeError, ValueError):
            prev_id = 0
        if prev_id and prev_id != jid:
            _state["job_id"] = None
            _state["exper_id"] = None
    try:
        from agent.job_inbox import forget_superseded_job

        forget_superseded_job(_repo_root(), jid)
    except Exception:
        logger.debug("adopt 时摘掉误标上一单失败", exc_info=True)
    _persist_local_job_ids(jid, exper_id)


def notify_local_run_finished(*, aborted: bool = False) -> None:
    """试验正常结束或中止时结案；无登记则静默。"""
    if handoff_has_awaiting_job():
        logger.info("[iot_local_run] handoff 等待结案，跳过本地 done，改为立刻查终态")
        try:
            sw = _scpi_mod()
            svc = getattr(sw, "_iot_ui_handoff_svc", None) if sw is not None else None
            notify = getattr(svc, "notify_desktop_run_finished", None)
            if callable(notify):
                notify()
        except Exception:
            logger.debug("通知 handoff 结案失败", exc_info=True)
        return
    with _lock:
        jid = _state.get("job_id")
    if not jid:
        # 进程重启或登记线程竞态时，内存可能空，但 status.json 仍有 jobId
        jid = _job_id_from_status_json()
        if jid:
            with _lock:
                _state["job_id"] = jid
    if not jid:
        return
    try:
        job_id = int(jid)
    except (TypeError, ValueError):
        return
    if job_id <= 0:
        return
    threading.Thread(
        target=_do_done,
        args=(job_id, bool(aborted)),
        daemon=True,
        name="iot-local-run-done",
    ).start()
