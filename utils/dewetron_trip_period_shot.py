# -*- coding: utf-8 -*-
"""跳脱时间段波形截图：只画跳脱前后一段实时数据，不截整段试验。"""

from __future__ import annotations

import os
import time
from typing import List, Optional, Sequence, Tuple

from utils.dewetron_trip_monitor import find_current_indices


Sample = Tuple[float, Sequence[float]]  # (elapsed_s, numeric values)


def slice_trip_period(
    samples: Sequence[Sample],
    *,
    pre_s: float = 2.0,
    post_s: float = 1.0,
) -> List[Sample]:
    """截取最后一点为跳脱点时，往前 pre_s、往后 post_s（缓冲内）的时间段。"""
    if not samples:
        return []
    t_trip = float(samples[-1][0])
    t0 = t_trip - float(pre_s)
    t1 = t_trip + float(post_s)
    return [s for s in samples if t0 <= float(s[0]) <= t1]


def render_trip_period_png(
    samples: Sequence[Sample],
    channel_names: Sequence[str],
    save_path: str,
    *,
    title: str = "",
    trip_time_s: Optional[float] = None,
) -> Tuple[bool, str]:
    """
    把时间段内电流（及电压若有）画成 PNG。
    不依赖 matplotlib，用 Pillow + 折线即可验证。
    """
    path = (save_path or "").strip()
    if not path:
        return False, "保存路径为空"
    if len(samples) < 2:
        return False, f"时间段样本不足: {len(samples)}"

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        return False, f"缺少 Pillow: {exc}"

    names = [str(n) for n in (channel_names or [])]
    phase_idx, total_idx = find_current_indices(names)
    u_idx = [
        i
        for i, n in enumerate(names)
        if n.split("@", 1)[0].upper().startswith("U")
        and any(ch in n.split("@", 1)[0].upper() for ch in ("U1", "U2", "U3", "U_TRMS", "URMS"))
    ]
    # 更宽松：U1_tRMS / U2 / U3
    if not u_idx:
        u_idx = [
            i
            for i, n in enumerate(names)
            if "U1" in n.upper() or "U2" in n.upper() or "U3" in n.upper()
        ][:3]

    times = [float(s[0]) for s in samples]
    t_min, t_max = min(times), max(times)
    if t_max <= t_min:
        t_max = t_min + 1e-3
    trip_t = float(trip_time_s) if trip_time_s is not None else times[-1]

    def series(indices: Sequence[int]) -> List[List[float]]:
        out = []
        for idx in indices:
            ys = []
            for _t, vals in samples:
                try:
                    ys.append(float(vals[idx]) if idx < len(vals) else float("nan"))
                except (TypeError, ValueError, IndexError):
                    ys.append(float("nan"))
            out.append(ys)
        return out

    i_indices = list(phase_idx) if phase_idx else ([total_idx] if total_idx is not None else [])
    i_series = series(i_indices)
    u_series = series(u_idx[:3])

    width, height = 1200, 700
    margin_l, margin_r, margin_t, margin_b = 70, 30, 50, 50
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    mid_y = margin_t + plot_h // 2

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    def x_of(t: float) -> int:
        return margin_l + int((t - t_min) / (t_max - t_min) * plot_w)

    def y_of(v: float, vmin: float, vmax: float, top: int, bottom: int) -> int:
        if vmax <= vmin:
            vmax = vmin + 1.0
        ratio = (v - vmin) / (vmax - vmin)
        ratio = max(0.0, min(1.0, ratio))
        return int(bottom - ratio * (bottom - top))

    def draw_panel(series_list: List[List[float]], top: int, bottom: int, colors: Sequence[str], label: str):
        flat = [v for ser in series_list for v in ser if v == v]
        if not flat:
            draw.text((margin_l, top + 8), f"{label}: (no data)", fill=(120, 120, 120), font=font)
            return
        vmin, vmax = min(flat), max(flat)
        if abs(vmax - vmin) < 1e-9:
            vmax = vmin + 1.0
        # grid
        draw.rectangle([margin_l, top, width - margin_r, bottom], outline=(200, 200, 200))
        for ser, color in zip(series_list, colors):
            pts = []
            for t, v in zip(times, ser):
                if v != v:
                    continue
                pts.append((x_of(t), y_of(v, vmin, vmax, top, bottom)))
            if len(pts) >= 2:
                draw.line(pts, fill=color, width=2)
        draw.text((margin_l + 4, top + 4), f"{label}  [{vmin:.2f}, {vmax:.2f}]", fill=(40, 40, 40), font=font)

    colors_i = [(220, 20, 60), (30, 144, 255), (34, 139, 34)]
    colors_u = [(255, 140, 0), (138, 43, 226), (0, 128, 128)]
    draw_panel(u_series, margin_t, mid_y - 8, colors_u, "U")
    draw_panel(i_series, mid_y + 8, height - margin_b, colors_i, "I")

    # 跳脱竖线
    tx = x_of(trip_t)
    draw.line([(tx, margin_t), (tx, height - margin_b)], fill=(0, 160, 160), width=2)
    draw.text((tx + 4, margin_t + 4), f"trip @ {trip_t:.3f}s", fill=(0, 120, 120), font=font)

    hdr = title or "Dewetron trip period"
    draw.text((margin_l, 12), f"{hdr}  window={t_min:.3f}~{t_max:.3f}s  n={len(samples)}", fill=(0, 0, 0), font=font)

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        img.save(path, format="PNG")
    except Exception as exc:
        return False, f"写文件失败: {exc}"
    return True, f"已保存跳脱时间段截图: {path} ({len(samples)} pts, {t_min:.3f}~{t_max:.3f}s)"


def build_trip_period_path(save_path: str, *, stamp: Optional[str] = None) -> str:
    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = (save_path or "").strip()
    if base:
        folder = os.path.dirname(os.path.abspath(base)) or os.path.join("command_save_files", "dewetron_data")
        stem = os.path.splitext(os.path.basename(base))[0] or "dewetron"
    else:
        folder = os.path.join("command_save_files", "dewetron_data")
        stem = "dewetron"
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{stem}_trip_period_{stamp}.png")


def build_trip_oxygen_path(save_path: str, *, stamp: Optional[str] = None) -> str:
    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = (save_path or "").strip()
    if base:
        folder = os.path.dirname(os.path.abspath(base)) or os.path.join("command_save_files", "dewetron_data")
        stem = os.path.splitext(os.path.basename(base))[0] or "dewetron"
    else:
        folder = os.path.join("command_save_files", "dewetron_data")
        stem = "dewetron"
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{stem}_trip_oxygen_{stamp}.png")
