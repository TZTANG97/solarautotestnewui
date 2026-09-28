# -*- coding: utf-8 -*-
"""Infer instrument brand / catalog serial when *IDN? is missing."""
from __future__ import annotations

import re
from typing import Optional, Tuple

USB_VID_BRAND = {
    "0A69": "ITECH",
    "1698": "CHROMA",
    "0957": "Keysight",
    "2A8D": "Keysight",
}

KIND_ROLE = {
    "ac": "AC",
    "dc": "DC",
    "wt": "WT",
    "scope": "SCOPE",
    "dew": "DEW",
}

BRAND_DISPLAY = {
    "chroma": "CHROMA",
    "yokogawa": "YOKOGAWA",
    "itech": "ITECH",
    "keysight": "Keysight",
    "agilent": "Keysight",
    "dewetron": "DEWETRON",
    "dewesoft": "DEWETRON",
    "bluesight": "Bluesight",
}


def parse_scpi_idn(idn: str) -> Tuple[str, str, str]:
    text = (idn or "").strip()
    if not text or text.startswith("未响应"):
        return "", "", ""
    parts = [p.strip() for p in text.split(",")]
    brand = parts[0] if parts else ""
    model = parts[1] if len(parts) > 1 else ""
    serial = parts[2] if len(parts) > 2 else ""
    return brand[:64], model[:128], serial[:64]


def parse_usb_visa(resource: str) -> Tuple[str, str, str]:
    """USB0::0x0A69::0x084B::S50000002314::INSTR → (vid, pid, serial)."""
    m = re.search(
        r"USB\d*::0x([0-9A-Fa-f]+)::0x([0-9A-Fa-f]+)::([^:]+)",
        resource or "",
        re.I,
    )
    if not m:
        return "", "", ""
    return m.group(1).upper(), m.group(2).upper(), m.group(3).strip()


def is_resource_like_serial(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return True
    upper = text.upper()
    if upper.startswith(("USB", "TCPIP", "GPIB", "ASRL", "VXI", "PXI", "HISLIP")):
        return True
    if "::" in text:
        return True
    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?$", text):
        return True
    return False


def display_brand(brand: str) -> str:
    raw = (brand or "").strip()
    if not raw:
        return ""
    mapped = BRAND_DISPLAY.get(raw.lower())
    if mapped:
        return mapped
    if re.search(r"[A-Za-z]", raw):
        return raw[:64]
    return raw[:64]


def role_tag_for(kind: str, slot: str = "") -> str:
    kind_l = (kind or "").strip().lower()
    slot_l = (slot or "").strip().lower()
    if kind_l == "dc" and slot_l.startswith("dc"):
        return slot_l.upper()[:8]
    if slot_l in KIND_ROLE:
        return KIND_ROLE[slot_l]
    return KIND_ROLE.get(kind_l, "INST")


def sat_instrument_seq(
    *,
    kind: str,
    slot: str = "",
    host_name: str = "",
    machine_id: str = "",
    python_id: str = "",
) -> str:
    host = re.sub(r"[^A-Za-z0-9_-]+", "-", (host_name or "PC").strip()).strip("-_")[:24] or "PC"
    hx = re.sub(r"[^0-9a-fA-F]", "", (machine_id or "").lower())
    if len(hx) < 8:
        hx = re.sub(r"[^0-9a-fA-F]", "", python_id or "")[-16:]
    short8 = (hx[-8:] if len(hx) >= 8 else (hx + "00000000")[:8]).upper()
    return f"SAT-{role_tag_for(kind, slot)}-{host}-{short8}"[:64]


def infer_brand(*, kind: str, resource: str, brand: str = "", idn: str = "", model: str = "") -> str:
    idn_brand, _, _ = parse_scpi_idn(idn)
    shown = display_brand(brand or idn_brand)
    if shown:
        return shown
    blob = f"{model or ''} {idn or ''}".lower()
    if "chroma" in blob:
        return "CHROMA"
    if "itech" in blob:
        return "ITECH"
    kind_l = (kind or "").strip().lower()
    if kind_l == "dew":
        return "DEWETRON"
    vid, _pid, _sn = parse_usb_visa(resource)
    if vid and vid in USB_VID_BRAND:
        return USB_VID_BRAND[vid]
    res = (resource or "").strip()
    res_u = res.upper()
    if kind_l in ("ac", "dc"):
        if re.search(r":502(?:\D|$)", res) or res.endswith(":502"):
            return "ITECH"
        if "TCPIP" in res_u or "::INSTR" in res_u:
            return "CHROMA"
        if kind_l == "ac":
            return "CHROMA"
    if kind_l == "wt":
        return "YOKOGAWA"
    if kind_l == "scope":
        return "YOKOGAWA"
    return ""


def infer_serial(
    *,
    kind: str,
    resource: str,
    serial: str = "",
    idn: str = "",
    slot: str = "",
    host_name: str = "",
    machine_id: str = "",
    python_id: str = "",
) -> str:
    _b, _m, idn_serial = parse_scpi_idn(idn)
    cand = (serial or "").strip() or (idn_serial or "").strip()
    if not cand:
        _vid, _pid, usb_sn = parse_usb_visa(resource)
        cand = usb_sn
    if cand and not is_resource_like_serial(cand):
        return cand[:255]
    return sat_instrument_seq(
        kind=kind,
        slot=slot,
        host_name=host_name,
        machine_id=machine_id,
        python_id=python_id,
    )
