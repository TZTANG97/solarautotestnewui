# -*- coding: utf-8 -*-
"""
新电脑：machineId → announce 分配 pythonid → WebSocket 上线（进「添加设备」）
→ 运维在添加设备选 pythonid 保存 → claim 令牌 → 写配置并跑任务。

IOT 地址优先安装包正式地址（iot_bootstrap.json），避免升级后仍指向 127.0.0.1。
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
CLAIM_LOG_EVERY = 6
# 视为「联调地址」，升级后应被安装包正式 iot_bootstrap 覆盖
_LOCAL_IOT_MARKERS = ("127.0.0.1", "localhost", "0.0.0.0", "请填写")


def machine_id_path() -> Path:
    return _repo_root() / "config" / "solar_machine_id"


def config_path() -> Path:
    return _repo_root() / "config" / "solar_agent.json"


def _windows_machine_guid() -> str:
    """本机稳定机器码（重装目录不变则同一台机），避免随机 uuid 导致反复「重新添加」。"""
    try:
        import winreg  # type: ignore

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        try:
            val, _ = winreg.QueryValueEx(key, "MachineGuid")
        finally:
            winreg.CloseKey(key)
        hx = "".join(c for c in str(val) if c.isalnum()).lower()
        return hx if len(hx) >= 8 else ""
    except Exception:
        return ""


def ensure_machine_id() -> str:
    path = machine_id_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        mid = path.read_text(encoding="utf-8").strip()
        if len(mid) >= 8:
            return mid
    # 已有文件优先；新机用 Windows MachineGuid，保证同机同码
    mid = _windows_machine_guid() or uuid.uuid4().hex
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


def _is_local_iot(url: str) -> bool:
    text = (url or "").strip().lower()
    if not text:
        return True
    return any(m in text for m in _LOCAL_IOT_MARKERS)


def resolve_iot_base(existing: Optional[Dict[str, Any]] = None) -> str:
    """
    优先：环境变量 → 安装包 iot_bootstrap（正式地址）→ 本机 solar_agent
    （若 solar_agent 仍是 127.0.0.1 则忽略，避免升级后连错）。
    """
    existing = existing or {}
    env = (os.environ.get("SOLAR_IOT_BASE") or "").strip().rstrip("/")
    boot = str(_read_json(_repo_root() / "config" / "iot_bootstrap.json").get("iot_base") or "").strip().rstrip("/")
    agent = str(existing.get("iot_base") or "").strip().rstrip("/")
    example = str(
        _read_json(_repo_root() / "config" / "solar_agent.example.json").get("iot_base") or ""
    ).strip().rstrip("/")

    if env and not _is_local_iot(env):
        return env
    if boot and not _is_local_iot(boot):
        return boot
    if agent and not _is_local_iot(agent):
        return agent
    if env:
        return env
    if boot:
        return boot
    if agent:
        return agent
    if example and "请填写" not in example:
        return example
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
    agent_token: Optional[str] = None,
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
            "pythonid": pythonid or data.get("pythonid") or "",
            "machine_id": machine_id or data.get("machine_id") or "",
            "poll_interval_sec": int(data.get("poll_interval_sec") or 15),
            "heartbeat_interval_sec": int(data.get("heartbeat_interval_sec") or 15),
            "dry_run": False,
            "execution_mode": "handoff",
            "mutex_path": data.get("mutex_path") or "",
            "agent_version": data.get("agent_version") or "0.1.0",
            "comment": "正式环境；勿提交 Git。换机勿拷贝。令牌由添加设备后自动领取。",
        }
    )
    if agent_token is not None:
        data["agent_token"] = agent_token
    elif "agent_token" not in data:
        data["agent_token"] = ""
    if extra:
        data.update(extra)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def announce(*, force: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
    cfg = _read_json(config_path())
    iot_base = resolve_iot_base(cfg)
    if not iot_base:
        return (
            False,
            "未配置 IOT 地址。请检查 config/iot_bootstrap.json 的 iot_base",
            {},
        )

    mid = ensure_machine_id()
    host = socket.gethostname()
    # 已有令牌仍刷新发现/WS 用的 pythonid（不强制重新领令牌）
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
    token = str(data.get("agentToken") or data.get("agent_token") or "").strip()
    old_base = str(cfg.get("iot_base") or "")
    # 从本机联调切到正式环境时，丢掉旧本地令牌，走添加设备后重新 claim
    keep_token = ""
    if token:
        keep_token = token
    elif config_has_token(cfg) and not _is_local_iot(old_base) and not _is_local_iot(iot_base):
        keep_token = str(cfg.get("agent_token") or "")
    write_agent_config(
        iot_base=iot_base,
        agent_token=keep_token,
        pythonid=pythonid,
        machine_id=mid,
    )
    if keep_token and token:
        return True, f"已领取令牌 pythonid={pythonid}", data
    if keep_token and not token:
        return True, f"已上线 pythonid={pythonid}（沿用令牌）", data
    if bool(data.get("claimed")):
        return True, f"台架已添加 pythonid={pythonid}，可领取令牌", data
    return True, f"已上报 pythonid={pythonid}，请在「设备管理→添加设备」中选择并添加", data


def claim_once() -> Tuple[bool, str, Dict[str, Any]]:
    cfg = _read_json(config_path())
    if config_has_token(cfg) and not _is_local_iot(str(cfg.get("iot_base") or "")):
        # 令牌有效且地址非本地
        pass
    iot_base = resolve_iot_base(cfg)
    if not iot_base:
        return False, "未配置 IOT 地址", {}

    mid = ensure_machine_id()
    qs = urlencode({"machineId": mid, "registerKey": resolve_register_key(cfg)})
    url = f"{iot_base.rstrip('/')}/api/solar-autotest/agent/claim?{qs}"
    try:
        res = _http_json("GET", url)
    except Exception as exc:
        return False, f"领取令牌失败: {exc}", {}

    data = res.get("data") if isinstance(res, dict) else None
    if not isinstance(data, dict):
        return False, f"领取返回异常: {res}", {}

    token = str(data.get("agentToken") or data.get("agent_token") or "").strip()
    pythonid = str(data.get("pythonid") or data.get("pythonId") or cfg.get("pythonid") or "").strip()
    if not token:
        return False, "尚未领取到令牌（请先在添加设备中完成登记）", data

    write_agent_config(iot_base=iot_base, agent_token=token, pythonid=pythonid, machine_id=mid)
    return True, f"已领取令牌 pythonid={pythonid}", data


def wait_for_claim(*, max_wait_sec: float = 0) -> Tuple[bool, str]:
    deadline = None if max_wait_sec <= 0 else (time.time() + max_wait_sec)
    n = 0
    while True:
        ok, msg, _ = claim_once()
        if ok and config_has_token():
            return True, msg
        n += 1
        if n == 1 or n % CLAIM_LOG_EVERY == 0:
            logger.info("%s", msg or "等待在「添加设备」中登记本机 pythonid…")
        if deadline is not None and time.time() >= deadline:
            return False, msg or "仍在等待添加设备"
        time.sleep(CLAIM_POLL_SEC)


def start_ws_presence_from_config() -> Tuple[bool, str]:
    from agent.ws_gateway import start_presence

    cfg = _read_json(config_path())
    iot_base = resolve_iot_base(cfg)
    pythonid = str(cfg.get("pythonid") or "").strip()
    mid = str(cfg.get("machine_id") or ensure_machine_id()).strip()
    if not iot_base or not pythonid:
        return False, "缺少 iot_base 或 pythonid，无法 WebSocket 上线"
    ok = start_presence(
        iot_base=iot_base,
        pythonid=pythonid,
        machine_id=mid,
        host_name=socket.gethostname(),
    )
    return (True, f"已 WebSocket 上线 pythonid={pythonid}") if ok else (False, "WebSocket 上线失败")


def ensure_configured_and_start() -> Tuple[bool, str]:
    """软件启动：announce → WS 上线（进添加设备）→ 有令牌则拉 Agent；否则后台 claim。"""
    from agent.process_control import start_agent, is_running

    ok, msg, data = announce(force=False)
    if not ok:
        logger.warning("%s", msg)
        return False, msg

    ws_ok, ws_msg = start_ws_presence_from_config()
    if not ws_ok:
        logger.warning("%s", ws_msg)

    if config_has_token() and not _is_local_iot(resolve_iot_base()):
        # 纠正本机旧 127.0.0.1：若已有令牌但地址已切正式，仍要能跑 Agent
        if is_running():
            return True, f"{msg}；{ws_msg}；Agent 已在运行"
        ok2, msg2 = start_agent(allow_without_token=False)
        return ok2, f"{msg}；{ws_msg}；{msg2}"

    # 无令牌：启动 Agent 进入 presence/claim 模式
    if not is_running():
        ok2, msg2 = start_agent(allow_without_token=True)
    else:
        ok2, msg2 = True, "Agent 已在运行"

    got, claim_msg = wait_for_claim(max_wait_sec=6.0)
    if got:
        return True, f"{msg}；{ws_msg}；{claim_msg}"

    pythonid = str((data or {}).get("pythonid") or (data or {}).get("pythonId") or "")
    tip = (
        f"{msg}。请打开 IOT「设备管理→添加设备」，选择 pythonid={pythonid or '本机'}，"
        f"验证后添加；本机将自动领取令牌。（{ws_msg}；{msg2}）"
    )
    logger.warning("%s", tip)
    _start_claim_background()
    return True, tip  # WS 已上线算成功，便于首页显示


_claim_bg_started = False


def _start_claim_background() -> None:
    global _claim_bg_started
    if _claim_bg_started:
        return
    _claim_bg_started = True

    def _worker() -> None:
        global _claim_bg_started
        try:
            while True:
                base = resolve_iot_base(_read_json(config_path()))
                if config_has_token() and not _is_local_iot(base):
                    # 若配置里仍是旧本地地址，强制写成正式 base
                    cfg = _read_json(config_path())
                    if _is_local_iot(str(cfg.get("iot_base") or "")):
                        write_agent_config(
                            iot_base=base,
                            agent_token=str(cfg.get("agent_token") or ""),
                            pythonid=str(cfg.get("pythonid") or ""),
                            machine_id=str(cfg.get("machine_id") or ensure_machine_id()),
                        )
                    break
                ok, msg, _ = claim_once()
                if ok:
                    logger.info("%s", msg)
                    base2 = resolve_iot_base(_read_json(config_path()))
                    if config_has_token() and not _is_local_iot(base2):
                        break
                time.sleep(CLAIM_POLL_SEC)
            if config_has_token():
                from agent.process_control import is_running, start_agent, stop_agent

                if is_running():
                    stop_agent()
                    time.sleep(1.0)
                ok2, msg2 = start_agent(allow_without_token=False)
                logger.info("%s", msg2)
                start_ws_presence_from_config()
        except Exception as exc:
            logger.warning("后台领取令牌异常: %s", exc)
        finally:
            _claim_bg_started = False

    import threading

    threading.Thread(target=_worker, name="solar-claim", daemon=True).start()


def self_register(*, force: bool = False) -> Tuple[bool, str]:
    ok, msg, _ = announce(force=force)
    return ok, msg
