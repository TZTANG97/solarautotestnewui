# -*- coding: utf-8 -*-
"""截取工控机上 Oxygen（德威创）窗口画面，供跳脱存证。"""

from __future__ import annotations

import os
import time
from typing import Optional, Tuple


def _find_oxygen_hwnd() -> Optional[int]:
    """按窗口标题模糊匹配 Oxygen / Dewesoft Oxygen。"""
    try:
        import win32gui
    except ImportError:
        return None

    candidates = []

    def _enum(hwnd, _extra):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if not title.strip():
            return
        low = title.casefold()
        if "oxygen" in low or "dewesoft" in low:
            # 排除明显不是主界面的附属窗
            if any(x in low for x in ("#32770", "tooltip", "ime")):
                return
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            except Exception:
                return
            area = max(0, right - left) * max(0, bottom - top)
            if area < 200 * 200:
                return
            score = 0
            if "oxygen" in low:
                score += 10
            if "dewesoft" in low:
                score += 5
            candidates.append((score, area, hwnd, title))

    try:
        win32gui.EnumWindows(_enum, None)
    except Exception:
        return None
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return int(candidates[0][2])


def capture_oxygen_window(save_path: str) -> Tuple[bool, str]:
    """
    截 Oxygen 主窗口到 save_path（png）。
    返回 (ok, message)；失败不抛异常。
    """
    path = (save_path or "").strip()
    if not path:
        return False, "保存路径为空"
    try:
        from PIL import ImageGrab
        import win32gui
    except ImportError as exc:
        return False, f"缺少截图依赖: {exc}"

    hwnd = _find_oxygen_hwnd()
    if not hwnd:
        return False, "未找到可见的 Oxygen/Dewesoft 窗口（请确认 Oxygen 已打开且未最小化）"

    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    except Exception as exc:
        return False, f"读取窗口位置失败: {exc}"

    # 纠正负坐标/最小化异常
    if right <= left or bottom <= top:
        return False, f"窗口尺寸无效 rect=({left},{top},{right},{bottom})"

    try:
        # 尽量提到前台再抓（失败仍尝试抓当前帧）
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.15)
        except Exception:
            pass
        img = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
    except TypeError:
        # 旧 Pillow 无 all_screens
        img = ImageGrab.grab(bbox=(left, top, right, bottom))
    except Exception as exc:
        return False, f"截图失败: {exc}"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        img.save(path, format="PNG")
    except Exception as exc:
        return False, f"写文件失败: {exc}"

    title = ""
    try:
        title = win32gui.GetWindowText(hwnd) or ""
    except Exception:
        pass
    return True, f"已保存 Oxygen 截图: {path}" + (f" ({title})" if title else "")


def build_trip_screenshot_path(save_path: str, *, stamp: Optional[str] = None) -> str:
    """与录波 CSV 同目录：{stem}_trip_{stamp}.png。"""
    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = (save_path or "").strip()
    if base:
        folder = os.path.dirname(os.path.abspath(base)) or os.path.join("command_save_files", "dewetron_data")
        stem = os.path.splitext(os.path.basename(base))[0] or "dewetron"
    else:
        folder = os.path.join("command_save_files", "dewetron_data")
        stem = "dewetron"
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{stem}_trip_{stamp}.png")
