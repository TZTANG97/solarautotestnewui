# -*- coding: utf-8 -*-
"""各品牌 AC/DC 保护上限（OVP/OCP/OPP）读回。

对齐 config/iot_output_limits.json 的 volt_max / curr_max / pow_max。
未识别品牌、未连机、或寄存器/命令未确认时返回 {_unread: True, detail: 中文原因}。
禁止代设保护值，只读比对。
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

_LIMIT_KEYS = ("volt_max", "curr_max", "pow_max")

# Chroma AC（61800 等）：可编程电压/电流限与保护查询候选（依次尝试）
_CHROMA_AC_SCPI: Dict[str, Tuple[str, ...]] = {
    "volt_max": (
        "SOUR:VOLT:PROT:HIGH?",
        "SOUR:VOLT:PROT?",
        "VOLT:PROT:HIGH?",
        "VOLT:PROT?",
        "SOUR:VOLT:LIM?",
        "VOLT:LIM?",
    ),
    "curr_max": (
        "SOUR:CURR:PROT:HIGH?",
        "SOUR:CURR:PROT?",
        "CURR:PROT:HIGH?",
        "CURR:PROT?",
        "SOUR:CURR:LIM?",
        "CURR:LIM?",
    ),
    "pow_max": (
        "SOUR:POW:PROT:HIGH?",
        "SOUR:POW:PROT?",
        "POW:PROT:HIGH?",
        "POW:PROT?",
        "SOUR:POW:LIM?",
        "POW:LIM?",
    ),
}

# Chroma DC（62000P 等）
_CHROMA_DC_SCPI: Dict[str, Tuple[str, ...]] = {
    "volt_max": (
        "SOUR:VOLT:PROT:HIGH?",
        "SOUR:VOLT:PROT?",
        "VOLT:PROT:HIGH?",
        "VOLT:PROT?",
    ),
    "curr_max": (
        "SOUR:CURR:PROT:HIGH?",
        "SOUR:CURR:PROT?",
        "CURR:PROT:HIGH?",
        "CURR:PROT?",
    ),
    "pow_max": (
        "SOUR:POW:PROT:HIGH?",
        "SOUR:POW:PROT?",
        "POW:PROT:HIGH?",
        "POW:PROT?",
    ),
}


def _unread(detail: str) -> Dict[str, Any]:
    return {"_unread": True, "detail": str(detail or "未能读回")}


def normalize_brand(brand: Any) -> str:
    b = str(brand or "").strip().lower()
    if b in ("chroma_ip", "chroma-ip", "chromaip"):
        return "chroma"
    if b in ("itech", "i tech", "爱科"):
        return "itech"
    if b in ("bluesight", "蓝点", "guochan", "国产"):
        return "bluesight"
    if b in ("chroma", "致茂"):
        return "chroma"
    return b


def _parse_float(raw: Any) -> Optional[float]:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    if not s:
        return None
    # 取首个数值（兼容 "220.0,0" / "NO ERROR" 以外的成功应答）
    m = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _clear_scpi_errors(handle: Any) -> None:
    if handle is None or not hasattr(handle, "query"):
        return
    for _ in range(8):
        try:
            ans = str(handle.query("SYST:ERR?") or "").strip()
        except Exception:
            return
        if not ans:
            return
        low = ans.lower()
        if low.startswith("0") or "no error" in low:
            return


def _query_scpi_first(
    handle: Any,
    commands: Sequence[str],
    *,
    log_prefix: str = "",
) -> Tuple[Optional[float], str]:
    """依次 query，返回 (值, 用过的命令或失败说明)。"""
    if handle is None or not hasattr(handle, "query"):
        return None, "无 SCPI 句柄"
    last_err = ""
    for cmd in commands:
        _clear_scpi_errors(handle)
        try:
            raw = handle.query(cmd)
        except Exception as exc:
            last_err = "%s 失败: %s" % (cmd, exc)
            logger.info("%s%s", log_prefix, last_err)
            continue
        val = _parse_float(raw)
        if val is None:
            last_err = "%s 应答无法解析: %r" % (cmd, raw)
            logger.info("%s%s", log_prefix, last_err)
            _clear_scpi_errors(handle)
            continue
        # 过滤明显错误码应答
        text = str(raw or "").strip().lower()
        if "error" in text and "no error" not in text:
            last_err = "%s 设备报错: %r" % (cmd, raw)
            logger.info("%s%s", log_prefix, last_err)
            _clear_scpi_errors(handle)
            continue
        logger.info("%s%s = %s (raw=%r)", log_prefix, cmd, val, raw)
        _clear_scpi_errors(handle)
        return val, cmd
    return None, last_err or "候选命令均失败"


def read_chroma_scpi_limits(
    handle: Any,
    scpi_map: Dict[str, Tuple[str, ...]],
    *,
    log_prefix: str = "[上限读回] ",
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    tried: List[str] = []
    for key in _LIMIT_KEYS:
        cmds = scpi_map.get(key) or ()
        if not cmds:
            continue
        val, used = _query_scpi_first(handle, cmds, log_prefix=log_prefix)
        if val is None:
            tried.append("%s:%s" % (key, used))
            continue
        out[key] = val
        tried.append("%s@%s" % (key, used))
    if not out:
        return _unread("Chroma 保护查询均未成功（%s）" % "；".join(tried[:3]))
    out["_source"] = "chroma_scpi"
    out["_detail"] = "；".join(tried)
    return out


def _read_modbus_scaled(
    client: Any,
    *,
    regs: Dict[str, Optional[int]],
    scale: float,
    device_id: int = 1,
    brand_label: str,
) -> Dict[str, Any]:
    """按寄存器表读保护；地址为 None 的项跳过；全部未配置则未读回。"""
    configured = {k: v for k, v in regs.items() if v is not None}
    if not configured:
        return _unread(
            "%s 保护上限寄存器尚未按厂家手册确认，禁止瞎读" % brand_label
        )
    if client is None:
        return _unread("%s 无 Modbus 客户端" % brand_label)

    out: Dict[str, Any] = {}
    errors: List[str] = []

    def _read_words(addr: int, count: int = 1) -> Optional[List[int]]:
        if hasattr(client, "read_holding_registers"):
            try:
                rr = client.read_holding_registers(
                    addr, count=count, device_id=device_id
                )
            except TypeError:
                try:
                    rr = client.read_holding_registers(
                        addr, count=count, slave=device_id
                    )
                except TypeError:
                    rr = client.read_holding_registers(addr, count)
            if rr is None or getattr(rr, "isError", lambda: False)():
                return None
            regs_list = getattr(rr, "registers", None)
            return list(regs_list) if regs_list else None
        rh = getattr(client, "read_holding_register", None)
        if callable(rh):
            raw = rh(addr, quantity=count, unit=device_id)
            if raw is None:
                return None
            if isinstance(raw, (list, tuple)) and raw and isinstance(raw[0], int):
                return list(raw)
            if isinstance(raw, int):
                return [raw]
        return None

    for key, addr in configured.items():
        try:
            words = _read_words(int(addr), 1)
        except Exception as exc:
            errors.append("%s@0x%04X:%s" % (key, int(addr), exc))
            continue
        if not words:
            errors.append("%s@0x%04X:空应答" % (key, int(addr)))
            continue
        raw_u = int(words[0]) & 0xFFFF
        val = float(raw_u) * float(scale)
        out[key] = val
        logger.info(
            "[上限读回] %s %s REG 0x%04X = %s (raw=%s scale=%s)",
            brand_label,
            key,
            int(addr),
            val,
            raw_u,
            scale,
        )

    if not out:
        detail = "%s 保护寄存器读失败" % brand_label
        if errors:
            detail = "%s（%s）" % (detail, "；".join(errors[:3]))
        return _unread(detail)
    out["_source"] = "modbus_prot"
    if errors:
        out["_detail"] = "；".join(errors)
    return out


def itech_ac_prot_regs() -> Dict[str, Optional[int]]:
    """爱科 AC 保护保持寄存器。

    仓库内尚无经台架核对的 OVP/OCP/OPP 地址；确认后填入下方常量即可启用读回。
    单位由 itech_prot_scale() 缩放。
    """
    from scpi_to_modbustcp import ItechTranslator

    return {
        "volt_max": getattr(ItechTranslator, "REG_PROT_VOLT", None),
        "curr_max": getattr(ItechTranslator, "REG_PROT_CURR", None),
        "pow_max": getattr(ItechTranslator, "REG_PROT_POW", None),
    }


def itech_prot_scale() -> float:
    from scpi_to_modbustcp import ItechTranslator

    return float(getattr(ItechTranslator, "PROT_SCALE", 0.01) or 0.01)


def bluesight_prot_regs() -> Dict[str, Optional[int]]:
    from scpi_to_modbustcp import BluesightTranslator

    return {
        "volt_max": getattr(BluesightTranslator, "REG_PROT_VOLT", None),
        "curr_max": getattr(BluesightTranslator, "REG_PROT_CURR", None),
        "pow_max": getattr(BluesightTranslator, "REG_PROT_POW", None),
    }


def bluesight_prot_scale() -> float:
    from scpi_to_modbustcp import BluesightTranslator

    return float(getattr(BluesightTranslator, "PROT_SCALE", 0.01) or 0.01)


def infer_ac_brand(controller: Any, brand_hint: Any = None) -> str:
    hint = normalize_brand(brand_hint)
    if hint:
        return hint
    if getattr(controller, "_itech", None) is not None:
        return "itech"
    idn = str(getattr(controller, "_idn", "") or "")
    if "CHROMA" in idn.upper():
        return "chroma"
    brand_attr = normalize_brand(getattr(controller, "brand", None))
    if brand_attr:
        return brand_attr
    # SCPI 句柄默认按 Chroma 族尝试
    if getattr(controller, "handle", None) is not None and getattr(
        controller, "client", None
    ) is None:
        return "chroma"
    if getattr(controller, "client", None) is not None:
        return "itech"
    return ""


def infer_dc_brand(controller: Any, brand_hint: Any = None) -> str:
    hint = normalize_brand(brand_hint)
    if hint:
        return hint
    brand_attr = normalize_brand(getattr(controller, "brand", None))
    if brand_attr:
        return brand_attr
    if getattr(controller, "client", None) is not None:
        return "bluesight"
    return "chroma"


def read_ac_output_limits(controller: Any, brand: Any = None) -> Dict[str, Any]:
    if controller is None:
        return _unread("交流电源未连接")
    if not getattr(controller, "connected", False) and getattr(
        controller, "handle", None
    ) is None:
        return _unread("交流电源未连接")

    b = infer_ac_brand(controller, brand)
    if b == "itech":
        client = getattr(controller, "client", None)
        itech = getattr(controller, "_itech", None)
        if client is None and itech is not None:
            client = getattr(itech, "AC_client", None)
        return _read_modbus_scaled(
            client,
            regs=itech_ac_prot_regs(),
            scale=itech_prot_scale(),
            brand_label="爱科交流",
        )
    if b in ("chroma", ""):
        handle = getattr(controller, "handle", None)
        if handle is None:
            return _unread("交流电源无 SCPI 句柄")
        return read_chroma_scpi_limits(
            handle, _CHROMA_AC_SCPI, log_prefix="[上限读回][AC] "
        )
    return _unread("交流电源品牌未识别或不支持读回: %s" % (b or "空"))


def read_dc_output_limits(controller: Any, brand: Any = None) -> Dict[str, Any]:
    if controller is None:
        return _unread("直流电源未连接")
    if not getattr(controller, "connected", False) and getattr(
        controller, "handle", None
    ) is None and getattr(controller, "client", None) is None:
        return _unread("直流电源未连接")

    b = infer_dc_brand(controller, brand)
    if b == "itech":
        client = getattr(controller, "client", None)
        # 爱科 DC 与蓝点同走 Modbus 客户端；寄存器表独立（待手册确认）
        return _read_modbus_scaled(
            client,
            regs=itech_ac_prot_regs(),  # 同族占位；确认后可拆 DC 专用表
            scale=itech_prot_scale(),
            brand_label="爱科直流",
        )
    if b == "bluesight":
        client = getattr(controller, "client", None)
        return _read_modbus_scaled(
            client,
            regs=bluesight_prot_regs(),
            scale=bluesight_prot_scale(),
            brand_label="蓝点直流",
        )
    if b in ("chroma", ""):
        handle = getattr(controller, "handle", None)
        if handle is None:
            return _unread("直流电源无 SCPI 句柄")
        return read_chroma_scpi_limits(
            handle, _CHROMA_DC_SCPI, log_prefix="[上限读回][DC] "
        )
    return _unread("直流电源品牌未识别或不支持读回: %s" % (b or "空"))
