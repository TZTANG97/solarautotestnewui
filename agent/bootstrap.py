# -*- coding: utf-8 -*-
"""
新电脑：生成本机 machineId → announce 上报发现 → 轮询 claim 领令牌 → 写 solar_agent.json。

对齐 IOT「添加设备」：先发现 pythonid，运维在台架管理确认添加后，本机才拿到令牌。

IOT 地址解析顺序：
  环境变量 SOLAR_IOT_BASE
  → config/solar_agent.json 已有 iot_base
  → config/iot_bootstrap.json（安装包可预置）
  → config/solar_agent.example.json
"""
from __future__ import annotations

import json
import logging
import os
import socket
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib import error, request
from urllib.parse import urlencode

from agent.config import _repo_root

logger = logging.getLogger("solar.agent.bootstrap")

CLAIM_POLL_SEC = 5.0
CLAIM_LOG_EVERY = 6  # 约 30s 打一次等待日志


def machine_id_path() -> Path:
    return _repo_root() / "config" / "solar_machine_id"


def config_path() -> Path:
    return _repo_root() / "config" / "solar_agent.json"


def ensure_machine_id() -> str:
    path = machine_id_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        mid = path.read_text(encoding="utf-8").strip()
        if len(mid) >= 8:
            return mid
    mid = uuid.uuid4().hex
    path.write_text(mid + "\n", encoding="utf-8")
    return mid


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def resolve_iot_base(existing: Optional[Dict[str, Any]] = None) -> str:
    existing = existing or {}
    candidates = [
        os.environ.get("SOLAR_IOT_BASE") or "",
        str(existing.get("iot_base") or ""),
        str(_read_json(_repo_root() / "config" / "iot_bootstrap.json").get("iot_base") or ""),
        str(_read_json(_repo_root() / "config" / "solar_agent.example.json").get("iot_base") or ""),
    ]
    for raw in candidates:
        text = str(raw or "").strip().rstrip("/")
        if text and "请填写" not in text:
            return text
    return ""


def resolve_register_key(existing: Optional[Dict[str, Any]] = None) -> str:
    existing = existing or {}
    boot = _read_json(_repo_root() / "config" / "iot_bootstrap.json")
    return (
        os.environ.get("SOLAR_SELF_REGISTER_KEY")
        or str(existing.get("register_key") or "")
        or str(boot.get("register_key") or "")
        or ""
    ).strip()


def config_has_token(data: Optional[Dict[str, Any]] = None) -> bool:
    data = data if data is not None else _read_json(config_path())
    token = str(data.get("agent_token") or "").strip()
    return bool(token) and not token.startswith("请填写")


def _http_json(
    method: str, url: str, body: Optional[dict] = None, timeout: float = 20.0
) -> Dict[str, Any]:
    raw = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Accept": "application/json"}
    if raw is not None:
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=raw, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail[:400]}") from e


def write_agent_config(
    *,
    iot_base: str,
    agent_token: str,
    pythonid: str = "",
    machine_id: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _read_json(path)
    data.update(
        {
            "iot_base": iot_base.rstrip("/"),
            "agent_token": agent_token,
            "pythonid": pythonid,
            "machine_id": machine_id,
            "poll_interval_sec": int(data.get("poll_interval_sec") or 15),
            "heartbeat_interval_sec": int(data.get("heartbeat_interval_sec") or 15),
            "dry_run": False,
            "execution_mode": "handoff",
            "mutex_path": data.get("mutex_path") or "",
            "agent_version": data.get("agent_version") or "0.1.0",
            "comment": "本机领取令牌后生成；勿提交 Git。换机勿拷贝此文件。",
        }
    )
    if extra:
        data.update(extra)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def announce(*, force: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
    """
    向 IOT 上报发现。返回 (ok, message, data)。
    data 可能含 pythonid / claimed / agentToken。
    """
    cfg = _read_json(config_path())
    if config_has_token(cfg) and not force:
        return True, "已有 Agent 令牌，跳过发现上报", {"claimed": True, "skipped": True}

    iot_base = resolve_iot_base(cfg)
    if not iot_base:
        return (
            False,
            "无法上报发现：未配置 IOT 地址。请在 config/iot_bootstrap.json 写入 "
            '{"iot_base":"http://IOT主机:端口/nss"} 或设置环境变量 SOLAR_IOT_BASE',
            {},
        )

    mid = ensure_machine_id()
    host = socket.gethostname()
    body = {
        "machineId": mid,
        "hostName": host,
        "agentVersion": str(cfg.get("agent_version") or "0.1.0"),
        "registerKey": resolve_register_key(cfg),
    }
    url = f"{iot_base.rstrip('/')}/api/solar-autotest/agent/announce"
    try:
        res = _http_json("POST", url, body)
    except Exception as exc:
        return False, f"发现上报失败（IOT={iot_base}）: {exc}", {}

    data = res.get("data") if isinstance(res, dict) else None
    if not isinstance(data, dict):
        return False, f"发现上报返回异常: {res}", {}

    pythonid = str(data.get("pythonid") or data.get("pythonId") or "").strip()
    claimed = bool(data.get("claimed"))
    token = str(data.get("agentToken") or data.get("agent_token") or "").strip()
    if token:
        write_agent_config(
            iot_base=iot_base,
            agent_token=token,
            pythonid=pythonid,
            machine_id=mid,
        )
        return True, f"已领取令牌 pythonid={pythonid}", data
    if claimed:
        return True, f"台架已添加 pythonid={pythonid}，等待领取令牌", data
    return True, f"已上报发现 pythonid={pythonid}，等待 IOT 台架管理「从发现添加」", data


def claim_once() -> Tuple[bool, str, Dict[str, Any]]:
    """尝试领取一次令牌。返回 (got_token, message, data)。"""
    cfg = _read_json(config_path())
    if config_has_token(cfg):
        return True, "已有令牌", {"claimed": True}

    iot_base = resolve_iot_base(cfg)
    if not iot_base:
        return False, "未配置 IOT 地址", {}

    mid = ensure_machine_id()
    qs = urlencode(
        {
            "machineId": mid,
            "registerKey": resolve_register_key(cfg),
        }
    )
    url = f"{iot_base.rstrip('/')}/api/solar-autotest/agent/claim?{qs}"
    try:
        res = _http_json("GET", url)
    except Exception as exc:
        return False, f"领取令牌失败: {exc}", {}

    data = res.get("data") if isinstance(res, dict) else None
    if not isinstance(data, dict):
        return False, f"领取返回异常: {res}", {}

    token = str(data.get("agentToken") or data.get("agent_token") or "").strip()
    pythonid = str(data.get("pythonid") or data.get("pythonId") or "").strip()
    if not token:
        return False, "尚未领取到令牌", data

    write_agent_config(
        iot_base=iot_base,
        agent_token=token,
        pythonid=pythonid,
        machine_id=mid,
    )
    return True, f"已领取令牌 pythonid={pythonid}", data


def wait_for_claim(*, max_wait_sec: float = 0) -> Tuple[bool, str]:
    """
    轮询 claim 直到拿到令牌。
    max_wait_sec<=0 表示一直等到进程退出（软件常驻场景用短时轮询后由下次启动继续）。
    启动阶段默认轮询一段时间，避免阻塞 UI 过久。
    """
    deadline = None if max_wait_sec <= 0 else (time.time() + max_wait_sec)
    n = 0
    while True:
        ok, msg, _data = claim_once()
        if ok and config_has_token():
            return True, msg
        n += 1
        if n == 1 or n % CLAIM_LOG_EVERY == 0:
            logger.info("%s", msg or "等待运维在 IOT 台架管理添加本机 pythonid…")
        if deadline is not None and time.time() >= deadline:
            return False, msg or "仍在等待运维添加台架"
        time.sleep(CLAIM_POLL_SEC)


def ensure_configured_and_start() -> Tuple[bool, str]:
    """供软件启动：发现上报 → 尝试领取 → 有令牌则拉起 Agent；否则后台继续等添加。"""
    from agent.process_control import start_agent, is_running

    if config_has_token():
        if is_running():
            return True, "已有令牌；Agent 已在运行"
        ok2, msg2 = start_agent()
        return ok2, msg2

    ok, msg, data = announce(force=False)
    if not ok:
        logger.warning("%s", msg)
        return False, msg

    if config_has_token():
        if is_running():
            return True, msg + "；Agent 已在运行"
        ok2, msg2 = start_agent()
        return ok2, f"{msg}；{msg2}"

    # 启动不长时间阻塞 UI：先短等一轮，再后台轮询
    got, claim_msg = wait_for_claim(max_wait_sec=8.0)
    if got:
        if is_running():
            return True, claim_msg + "；Agent 已在运行"
        ok2, msg2 = start_agent()
        return ok2, f"{claim_msg}；{msg2}"

    pythonid = str((data or {}).get("pythonid") or (data or {}).get("pythonId") or "")
    tip = (
        f"{msg}。请在 IOT「台架管理 → 从发现添加」选中 "
        f"{pythonid or '本机 pythonid'}；添加后本机将自动领取令牌。"
    )
    logger.warning("%s", tip)
    _start_claim_background()
    return False, tip


_claim_bg_started = False


def _start_claim_background() -> None:
    """后台领取令牌并启动 Agent（不阻塞 UI）。"""
    global _claim_bg_started
    if _claim_bg_started:
        return
    _claim_bg_started = True

    def _worker() -> None:
        global _claim_bg_started
        try:
            while not config_has_token():
                ok, msg, _ = claim_once()
                if ok and config_has_token():
                    logger.info("%s", msg)
                    break
                logger.debug("%s", msg)
                time.sleep(CLAIM_POLL_SEC)
            if config_has_token():
                from agent.process_control import start_agent, is_running

                if not is_running():
                    ok2, msg2 = start_agent()
                    logger.info("%s", msg2 if ok2 else msg2)
        except Exception as exc:
            logger.warning("后台领取令牌异常: %s", exc)
        finally:
            _claim_bg_started = False

    import threading

    threading.Thread(target=_worker, name="solar-claim", daemon=True).start()


# 兼容旧名
def self_register(*, force: bool = False) -> Tuple[bool, str]:
    ok, msg, _ = announce(force=force)
    if ok and not config_has_token():
        got, claim_msg = wait_for_claim(max_wait_sec=8.0)
        if got:
            return True, claim_msg
        _start_claim_background()
        return False, msg
    return ok, msg
