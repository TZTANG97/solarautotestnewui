# -*- coding: utf-8 -*-
"""工控机参数记忆：本地 JSON + Agent 上报 IOT prefs。"""
from __future__ import annotations

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_LOCK = threading.RLock()
_MAX = 480_000


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def prefs_path() -> Path:
    return _repo_root() / "config_files" / "iot_bench_prefs.json"


def empty_prefs() -> Dict[str, Any]:
    return {
        "useSavedInstruments": True,
        "useSavedTestParams": True,
        "instruments": [],
        "testParamsByType": {},
        "updatedAt": "",
        "source": "desktop",
    }


def loads_prefs(raw: Any) -> Dict[str, Any]:
    base = empty_prefs()
    if isinstance(raw, dict):
        data = raw
    elif isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return base
    else:
        return base
    if not isinstance(data, dict):
        return base
    out = empty_prefs()
    if "useSavedInstruments" in data:
        out["useSavedInstruments"] = bool(data.get("useSavedInstruments"))
    if "useSavedTestParams" in data:
        out["useSavedTestParams"] = bool(data.get("useSavedTestParams"))
    inst = data.get("instruments")
    if isinstance(inst, list):
        out["instruments"] = [x for x in inst if isinstance(x, dict)][:40]
    tmap = data.get("testParamsByType")
    if isinstance(tmap, dict):
        cleaned: Dict[str, Any] = {}
        for k, v in tmap.items():
            key = str(k or "").strip().lower()
            if not key or not isinstance(v, dict):
                continue
            widgets = v.get("widgets") if isinstance(v.get("widgets"), dict) else {}
            cleaned[key] = {
                "widgets": dict(widgets),
                "auto_append": bool(v["auto_append"]) if "auto_append" in v else True,
                "auto_start": bool(v["auto_start"]) if "auto_start" in v else True,
                "wait_finish": bool(v["wait_finish"]) if "wait_finish" in v else True,
                "savedAt": str(v.get("savedAt") or "")[:40],
            }
        out["testParamsByType"] = cleaned
    out["updatedAt"] = str(data.get("updatedAt") or "")[:40]
    out["source"] = str(data.get("source") or "desktop")[:32]
    return out


def load_local() -> Dict[str, Any]:
    path = prefs_path()
    with _LOCK:
        if not path.is_file():
            return empty_prefs()
        try:
            return loads_prefs(path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.debug("load iot_bench_prefs failed: %s", exc)
            return empty_prefs()


def save_local(prefs: Dict[str, Any]) -> Dict[str, Any]:
    body = loads_prefs(prefs)
    body["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body["source"] = body.get("source") or "desktop"
    text = json.dumps(body, ensure_ascii=False, indent=2)
    if len(text) > _MAX:
        body["instruments"] = (body.get("instruments") or [])[:20]
        keys = list((body.get("testParamsByType") or {}).keys())[:20]
        body["testParamsByType"] = {k: body["testParamsByType"][k] for k in keys}
        text = json.dumps(body, ensure_ascii=False, indent=2)
    path = prefs_path()
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return body


def merge_patch(current: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    out = loads_prefs(current)
    if not isinstance(patch, dict):
        return out
    if "useSavedInstruments" in patch:
        out["useSavedInstruments"] = bool(patch.get("useSavedInstruments"))
    if "useSavedTestParams" in patch:
        out["useSavedTestParams"] = bool(patch.get("useSavedTestParams"))
    if isinstance(patch.get("instruments"), list):
        out["instruments"] = [x for x in patch["instruments"] if isinstance(x, dict)][:40]
    tpatch = patch.get("testParamsByType")
    if isinstance(tpatch, dict):
        base_map = dict(out.get("testParamsByType") or {})
        for k, v in tpatch.items():
            key = str(k or "").strip().lower()
            if not key:
                continue
            if v is None:
                base_map.pop(key, None)
                continue
            if not isinstance(v, dict):
                continue
            widgets = v.get("widgets") if isinstance(v.get("widgets"), dict) else {}
            base_map[key] = {
                "widgets": dict(widgets),
                "auto_append": bool(v["auto_append"]) if "auto_append" in v else True,
                "auto_start": bool(v["auto_start"]) if "auto_start" in v else True,
                "wait_finish": bool(v["wait_finish"]) if "wait_finish" in v else True,
                "savedAt": str(v.get("savedAt") or datetime.now().isoformat(timespec="seconds"))[:40],
            }
        out["testParamsByType"] = base_map
    out["source"] = str(patch.get("source") or out.get("source") or "desktop")[:32]
    return out


def update_local(patch: Dict[str, Any]) -> Dict[str, Any]:
    with _LOCK:
        merged = merge_patch(load_local(), patch or {})
        return save_local(merged)


def set_use_saved_instruments(on: bool) -> Dict[str, Any]:
    return update_local({"useSavedInstruments": bool(on), "source": "desktop"})


def set_use_saved_test_params(on: bool) -> Dict[str, Any]:
    return update_local({"useSavedTestParams": bool(on), "source": "desktop"})


def save_instruments(instruments: List[Dict[str, Any]]) -> Dict[str, Any]:
    return update_local(
        {
            "instruments": [x for x in (instruments or []) if isinstance(x, dict)][:40],
            "source": "desktop",
        }
    )


def save_test_params(
    test_type: str,
    *,
    widgets: Dict[str, Any],
    auto_append: bool = True,
    auto_start: bool = True,
    wait_finish: bool = True,
) -> Dict[str, Any]:
    key = str(test_type or "").strip().lower() or "overload"
    return update_local(
        {
            "testParamsByType": {
                key: {
                    "widgets": dict(widgets or {}),
                    "auto_append": bool(auto_append),
                    "auto_start": bool(auto_start),
                    "wait_finish": bool(wait_finish),
                    "savedAt": datetime.now().isoformat(timespec="seconds"),
                }
            },
            "source": "desktop",
        }
    )


def remembered_test_widgets(test_type: str) -> Optional[Dict[str, Any]]:
    prefs = load_local()
    if not prefs.get("useSavedTestParams", True):
        return None
    key = str(test_type or "").strip().lower()
    entry = (prefs.get("testParamsByType") or {}).get(key)
    if not isinstance(entry, dict):
        return None
    widgets = entry.get("widgets")
    return dict(widgets) if isinstance(widgets, dict) else None


def should_merge_saved_test_params(job_params: Optional[Dict[str, Any]]) -> bool:
    """云端/桌面任一方关闭「使用上次」则不 merge。"""
    local = load_local()
    if not local.get("useSavedTestParams", True):
        return False
    if isinstance(job_params, dict) and "useSavedTestParams" in job_params:
        return bool(job_params.get("useSavedTestParams"))
    return True


def merge_widgets_with_memory(
    test_type: str,
    widgets: Optional[Dict[str, Any]],
    job_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    base = dict(widgets or {}) if isinstance(widgets, dict) else {}
    if not should_merge_saved_test_params(job_params):
        return base
    remembered = remembered_test_widgets(test_type)
    if not remembered:
        return base
    # 云端已填字段优先；空缺用本地记忆补
    out = dict(remembered)
    for k, v in base.items():
        if v is None or v == "":
            continue
        out[k] = v
    return out


def _try_agent_client():
    try:
        from agent.client import IotSolarClient
        from agent.config import default_config_path, load_config

        cfg_path = default_config_path()
        raw: Dict[str, Any] = {}
        if cfg_path.is_file():
            raw = json.loads(cfg_path.read_text(encoding="utf-8"))
        try:
            cfg_obj = load_config(str(cfg_path) if cfg_path.is_file() else None)
            base = str(getattr(cfg_obj, "iot_base", "") or "").strip()
            token = str(getattr(cfg_obj, "agent_token", "") or "").strip()
        except Exception:
            base = str(raw.get("iot_base") or "").strip()
            token = str(raw.get("agent_token") or "").strip()
        pythonid = str(raw.get("pythonid") or raw.get("python_id") or "").strip()
        if not base or not token:
            return None
        return IotSolarClient(base, token, pythonid=pythonid)
    except Exception as exc:
        logger.debug("agent client for prefs unavailable: %s", exc)
        return None


def push_to_cloud(patch: Optional[Dict[str, Any]] = None) -> bool:
    """双写：本地已更新后上报云端（失败静默）。"""
    client = _try_agent_client()
    if client is None:
        return False
    body = loads_prefs(patch) if patch else load_local()
    body["source"] = "desktop"
    try:
        if hasattr(client, "put_prefs"):
            client.put_prefs(body)
            return True
        client._request("PUT", "/api/solar-autotest/agent/prefs", body)  # noqa: SLF001
        return True
    except Exception as exc:
        logger.debug("push prefs failed: %s", exc)
        return False


def pull_from_cloud() -> Optional[Dict[str, Any]]:
    client = _try_agent_client()
    if client is None:
        return None
    try:
        if hasattr(client, "get_prefs"):
            res = client.get_prefs()
        else:
            res = client._request("GET", "/api/solar-autotest/agent/prefs")  # noqa: SLF001
        data = res.get("data") if isinstance(res, dict) else None
        if not isinstance(data, dict):
            return None
        merged = merge_patch(load_local(), data)
        # 云端更新时间更新时覆盖本地段
        remote_at = str(data.get("updatedAt") or "")
        local_at = str(load_local().get("updatedAt") or "")
        if remote_at and remote_at >= local_at:
            save_local(loads_prefs(data))
            return loads_prefs(data)
        return merged
    except Exception as exc:
        logger.debug("pull prefs failed: %s", exc)
        return None


def update_and_push(patch: Dict[str, Any]) -> Dict[str, Any]:
    body = update_local(patch)
    threading.Thread(target=push_to_cloud, args=(body,), daemon=True).start()
    return body
