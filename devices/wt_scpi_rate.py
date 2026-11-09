# -*- coding: utf-8 -*-
"""WT SCPI update-rate helpers.

Yokogawa WT panel numeric display refreshes at ~250 ms even when
``:RATE`` is 50/100 ms. Communication ``:NUMERIC:NORMAL:VALUE?`` follows
``:RATE``, not the panel. Historical ~180 ms floors usually came from:
serial (ASRL) round-trips, never verifying ``:RATE?``, or confusing panel
refresh with the communication data rate.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

# Discrete rates commonly accepted by WT3000 / WT1800 / WT5000 families.
WT_RATE_MS_CHOICES = (50, 100, 200, 250, 500, 1000, 2000, 5000, 10000, 20000)


def parse_rate_ms(rate_text) -> int:
    """Parse UI / SCPI rate text into milliseconds (default 100)."""
    if rate_text is None:
        return 100
    text = str(rate_text).strip()
    if not text:
        return 100
    text = re.sub(r"^:RATE\s*", "", text, flags=re.IGNORECASE).strip().strip('"')
    lower = text.lower().replace(" ", "")
    if lower.endswith("ms"):
        try:
            return max(1, int(round(float(lower[:-2]))))
        except ValueError:
            return 100
    if lower.endswith("s") and not lower.endswith("ms"):
        try:
            return max(1, int(round(float(lower[:-1]) * 1000)))
        except ValueError:
            return 100
    try:
        value = float(text)
    except ValueError:
        match = re.search(r"([\d.]+)", text)
        if not match:
            return 100
        value = float(match.group(1))
    # Instrument often replies in seconds (0.05 / 5.0E-2).
    if 0 < value < 1.5:
        return max(1, int(round(value * 1000)))
    return max(1, int(round(value)))


def snap_rate_ms(rate_ms: int, choices: Tuple[int, ...] = WT_RATE_MS_CHOICES) -> int:
    """Snap to the nearest supported instrument rate."""
    target = int(rate_ms)
    return min(choices, key=lambda item: abs(item - target))


def rate_command(rate_ms: int) -> str:
    """Build ``:RATE`` write command (milliseconds unit)."""
    from utils.wt_setup_catalog_overrides import get_rate_scpi_prefix, get_rate_scpi_template

    snapped = snap_rate_ms(rate_ms)
    if snapped >= 1000 and snapped % 1000 == 0:
        ms_part = f"{snapped // 1000}S"
    else:
        ms_part = f"{snapped}MS"

    template = get_rate_scpi_template()
    if template:
        return template.format(ms=ms_part, snapped=snapped)

    prefix = get_rate_scpi_prefix()
    return f"{prefix} {ms_part}"


def rates_match_ms(expected_ms: int, actual_ms: int, tol_ms: int = 5) -> bool:
    return abs(int(expected_ms) - int(actual_ms)) <= int(tol_ms)


def is_serial_resource(resource_name: Optional[str]) -> bool:
    name = str(resource_name or "").upper()
    return "ASRL" in name or name.startswith("COM")


def serial_too_slow_for_rate(resource_name: Optional[str], rate_ms: int) -> bool:
    """True when serial link is unlikely to sustain the requested rate."""
    return is_serial_resource(resource_name) and int(rate_ms) < 200
