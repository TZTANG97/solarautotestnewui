# -*- coding: utf-8 -*-
"""Yokogawa WT SCPI numeric collector (parallel to DewetronDataCollector).

Uses ``:RATE`` + ``:NUMERIC:NORMAL:VALUE?`` so sample spacing follows the
instrument data-update rate (50/100 ms), not the ~250 ms panel refresh.
"""
from __future__ import annotations

import csv
import os
import re
import threading
import time
from typing import Dict, List, Optional, Sequence, Tuple

from devices.wt_scpi_rate import (
    is_serial_resource,
    parse_rate_ms,
    rate_command,
    rates_match_ms,
    serial_too_slow_for_rate,
    snap_rate_ms,
)

# Common three-phase power items (element 1/2/3 + sigma). Models may reject
# unknown tokens; prepare() keeps only items accepted by ITEM? round-trip.
DEFAULT_WT_ITEMS = (
    "URMS,1",
    "URMS,2",
    "URMS,3",
    "IRMS,1",
    "IRMS,2",
    "IRMS,3",
    "P,1",
    "P,2",
    "P,3",
    "P,SIGMA",
    "Q,SIGMA",
    "LAMBDA,SIGMA",
    "FU,1",
)


class WtScpiCollector:
    """Background NUMERIC poller for WT3000 / WT1800 / WT1806E / WT5000."""

    def __init__(self, controller, logger=None):
        self._ctrl = controller
        self._log = logger
        self._stop_event = threading.Event()
        self._thread = None
        self.is_gather = threading.Event()
        self._rate_ms = 100
        self._items: List[str] = []
        self._header: List[str] = []
        self._rows: List[Tuple[float, List[float]]] = []
        self._rows_lock = threading.Lock()
        self._gather_start = 0.0
        self._save_path = ""
        self._warnings: List[str] = []
        self._last_error = ""

    # --- public API -----------------------------------------------------

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._collect_loop, name="WtScpiCollector", daemon=True
        )
        self._thread.start()

    def stop(self):
        self.stop_gathering()
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None

    def prepare(
        self,
        items: Optional[Sequence[str]] = None,
        rate_text: str = "100ms",
        save_path: str = "",
    ) -> Tuple[bool, List[str], List[str]]:
        """Configure RATE + NUMERIC items. Returns (ok, items, warnings)."""
        self._warnings = []
        self._last_error = ""
        self._save_path = save_path or ""
        self._rate_ms = snap_rate_ms(parse_rate_ms(rate_text))
        wanted = list(items) if items else list(DEFAULT_WT_ITEMS)

        handle = getattr(self._ctrl, "handle", None)
        if handle is None or not getattr(self._ctrl, "connected", False):
            self._last_error = "WT SCPI 未连接"
            return False, [], [self._last_error]

        resource = getattr(self._ctrl, "resource", "") or getattr(
            handle, "resource_name", ""
        )
        if serial_too_slow_for_rate(resource, self._rate_ms):
            msg = (
                f"当前为串口链路 ({resource})，难以稳定跑到 {self._rate_ms}ms；"
                "请改用以太网 TCPIP::IP::10001::SOCKET，否则间隔会贴近 ~180–250ms"
            )
            self._warnings.append(msg)
            self._info(msg)

        if not self._setup_rate():
            return False, [], self._warnings + [self._last_error or "RATE 设置失败"]

        accepted = self._setup_numeric_items(wanted)
        if not accepted:
            return False, [], self._warnings + [self._last_error or "NUMERIC 配置失败"]

        self._items = accepted
        self._header = ["Time [s]"] + accepted
        self._info(
            f"WT SCPI prepare OK: rate={self._rate_ms}ms, items={len(accepted)}"
        )
        return True, list(accepted), list(self._warnings)

    def start_gathering(self) -> bool:
        if not self._items:
            self._last_error = "未 prepare"
            return False
        if not getattr(self._ctrl, "connected", False):
            self._last_error = "WT SCPI 未连接"
            return False
        with self._rows_lock:
            self._rows = []
        self._gather_start = time.time()
        self.is_gather.set()
        self._info("WT SCPI gathering started")
        return True

    def stop_gathering(self) -> bool:
        was = self.is_gather.is_set()
        self.is_gather.clear()
        if was:
            self._info(f"WT SCPI gathering stopped, rows={self.total_rows()}")
        return was

    def total_rows(self) -> int:
        with self._rows_lock:
            return len(self._rows)

    def get_rows(self) -> List[Tuple[float, List[float]]]:
        with self._rows_lock:
            return list(self._rows)

    def latest_row(self) -> Optional[Tuple[float, List[float]]]:
        with self._rows_lock:
            if not self._rows:
                return None
            return self._rows[-1]

    def latest_item_map(self) -> Dict[str, float]:
        """最新一行按 NUMERIC item 名映射（如 URMS,1）。"""
        row = self.latest_row()
        if not row:
            return {}
        _t, values = row
        items = list(self._items or [])
        out: Dict[str, float] = {}
        for i, token in enumerate(items):
            if i >= len(values):
                break
            v = values[i]
            if v != v:  # NaN
                continue
            out[str(token).strip().upper()] = float(v)
        return out

    def latest_cloud_measures(self) -> Optional[Dict[str, float]]:
        """映射为云端曲线字段 u_rms / i_rms / p / freq。"""
        m = self.latest_item_map()
        if not m:
            return None

        def _avg(prefix: str) -> Optional[float]:
            vals = []
            for k, v in m.items():
                if k.startswith(prefix + ",") and not k.endswith(",SIGMA"):
                    vals.append(v)
            if not vals:
                return None
            return sum(vals) / len(vals)

        u = _avg("URMS")
        if u is None and "URMS,1" in m:
            u = m["URMS,1"]
        i = _avg("IRMS")
        if i is None and "IRMS,1" in m:
            i = m["IRMS,1"]
        p = m.get("P,SIGMA")
        if p is None:
            p_vals = [v for k, v in m.items() if k.startswith("P,") and k != "P,SIGMA"]
            if p_vals:
                p = sum(p_vals)
        freq = m.get("FU,1") or m.get("FREQ,1") or m.get("F,1")
        out: Dict[str, float] = {}
        if u is not None:
            out["u_rms"] = round(float(u), 4)
        if i is not None:
            out["i_rms"] = round(float(i), 4)
        if p is not None:
            out["p"] = round(float(p), 4)
        if freq is not None:
            out["freq"] = round(float(freq), 4)
        return out or None

    def sample_interval_stats(self) -> dict:
        """Measure spacing between PC receive timestamps of stored rows."""
        with self._rows_lock:
            times = [t for t, _ in self._rows]
        if len(times) < 2:
            return {"n": len(times), "median_ms": None, "mean_ms": None, "p95_ms": None}
        deltas = [(times[i] - times[i - 1]) * 1000.0 for i in range(1, len(times))]
        deltas.sort()
        n = len(deltas)
        mean = sum(deltas) / n
        median = deltas[n // 2]
        p95 = deltas[min(n - 1, int(n * 0.95))]
        return {
            "n": len(times),
            "median_ms": round(median, 2),
            "mean_ms": round(mean, 2),
            "p95_ms": round(p95, 2),
            "min_ms": round(deltas[0], 2),
            "max_ms": round(deltas[-1], 2),
            "target_ms": self._rate_ms,
        }

    def export_to_csv(self, csv_path: Optional[str] = None) -> Optional[str]:
        path = csv_path or self._save_path
        if not path:
            return None
        rows = self.get_rows()
        if not rows:
            return None
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(self._header or (["Time [s]"] + self._items))
            for t_s, values in rows:
                writer.writerow(
                    [f"{t_s:.4f}"] + [f"{v:.7f}" if v == v else "" for v in values]
                )
        self._info(f"WT SCPI CSV exported: {path} ({len(rows)} rows)")
        return path

    def last_error(self) -> str:
        return self._last_error

    def warnings(self) -> List[str]:
        return list(self._warnings)

    # --- SCPI helpers ---------------------------------------------------

    def _info(self, message: str):
        print(f"[WtScpiCollector] {message}")
        if self._log is not None:
            try:
                self._log.info(message)
            except Exception:
                pass

    def _write(self, command: str) -> bool:
        handle = getattr(self._ctrl, "handle", None)
        if handle is None:
            self._last_error = "handle 为空"
            return False
        try:
            handle.write(command)
            return True
        except Exception as exc:
            self._last_error = f"write {command!r} failed: {exc}"
            self._info(self._last_error)
            return False

    def _query(self, command: str) -> Optional[str]:
        handle = getattr(self._ctrl, "handle", None)
        if handle is None:
            self._last_error = "handle 为空"
            return None
        try:
            return str(handle.query(command)).strip()
        except Exception as exc:
            self._last_error = f"query {command!r} failed: {exc}"
            self._info(self._last_error)
            return None

    def _setup_rate(self) -> bool:
        cmd = rate_command(self._rate_ms)
        if not self._write(cmd):
            return False
        # Give the instrument a beat to apply the update period.
        time.sleep(0.05)
        reply = self._query(":RATE?")
        if reply is None:
            return False
        actual = parse_rate_ms(reply)
        self._info(f"RATE set={self._rate_ms}ms reply={reply!r} parsed={actual}ms")
        if not rates_match_ms(self._rate_ms, actual, tol_ms=10):
            # Some models snap 200→250; accept snapped value but warn.
            snapped = snap_rate_ms(actual)
            msg = (
                f"RATE 回读为 {actual}ms（目标 {self._rate_ms}ms），"
                f"将按 {snapped}ms 采集"
            )
            self._warnings.append(msg)
            self._rate_ms = snapped
            if not rates_match_ms(self._rate_ms, actual, tol_ms=10):
                self._last_error = msg
                return False
        return True

    def _setup_numeric_items(self, wanted: Sequence[str]) -> List[str]:
        """Program ITEM1..N; drop items the instrument rejects."""
        if not self._write(":NUMERIC:FORMAT ASCII"):
            return []
        # Clear / set count — NUMBER ALL is model-dependent; set explicit count.
        if not self._write(f":NUMERIC:NORMAL:NUMBER {len(wanted)}"):
            return []

        accepted: List[str] = []
        for index, item in enumerate(wanted, start=1):
            token = str(item).strip()
            if not token:
                continue
            if not self._write(f":NUMERIC:NORMAL:ITEM{index} {token}"):
                continue
            check = self._query(f":NUMERIC:NORMAL:ITEM{index}?")
            if check is None:
                continue
            # Reply often echoes "URMS,1" or ":NUMERIC:NORMAL:ITEM1 URMS,1"
            if token.replace(" ", "").upper() in check.replace(" ", "").upper():
                accepted.append(token)
            else:
                self._warnings.append(f"ITEM{index} 未接受 {token!r} (reply={check!r})")

        if not accepted:
            self._last_error = "没有任何 NUMERIC ITEM 被仪器接受"
            return []

        if not self._write(f":NUMERIC:NORMAL:NUMBER {len(accepted)}"):
            return []
        # Re-write compacted list in case we skipped rejected slots.
        for index, item in enumerate(accepted, start=1):
            if not self._write(f":NUMERIC:NORMAL:ITEM{index} {item}"):
                return []
        return accepted

    # --- gather loop ----------------------------------------------------

    def _collect_loop(self):
        while not self._stop_event.is_set():
            if not self.is_gather.is_set():
                time.sleep(0.05)
                continue
            interval_s = max(self._rate_ms, 1) / 1000.0
            t0 = time.time()
            raw = self._query(":NUMERIC:NORMAL:VALUE?")
            if raw:
                values = self._parse_values(raw)
                if values is not None:
                    elapsed = time.time() - self._gather_start
                    with self._rows_lock:
                        self._rows.append((elapsed, values))
            slept = interval_s - (time.time() - t0)
            time.sleep(max(slept, 0.001))

    def _parse_values(self, raw: str) -> Optional[List[float]]:
        text = raw
        if text.upper().startswith(":NUMERIC"):
            match = re.search(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", text)
            if match is None:
                return None
            text = text[match.start():]
        parts = [p.strip() for p in text.replace(";", ",").split(",") if p.strip()]
        if not parts:
            return None
        out: List[float] = []
        for part in parts:
            try:
                out.append(float(part))
            except ValueError:
                out.append(float("nan"))
        need = len(self._items)
        if need and len(out) > need:
            out = out[:need]
        while need and len(out) < need:
            out.append(float("nan"))
        return out
