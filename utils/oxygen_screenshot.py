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
    返回 (ok, message)；空白图不保存。失败不抛异常。
    """
    path = (save_path or "").strip()
    if not path:
        return False, "保存路径为空"
    try:
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

    if right <= left or bottom <= top:
        return False, f"窗口尺寸无效 rect=({left},{top},{right},{bottom})"

    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception:
        pass

    from utils.screen_capture import is_blank_image, save_usable_image

    img = _grab_printwindow(hwnd)
    if img is None or is_blank_image(img):
        grabbed = _grab_screen_rect(left, top, right, bottom)
        if grabbed is not None and (img is None or not is_blank_image(grabbed)):
            img = grabbed
    if img is None:
        return False, "截图失败: 没有拿到窗口画面"

    ok, msg = save_usable_image(img, path)
    if not ok:
        return False, (
            "Oxygen 画面是显卡绘制的，抓到的是空白图，未保存。"
            "请让 Oxygen 停在闪变结果页并且不要最小化后再试。"
        )
    title = ""
    try:
        title = win32gui.GetWindowText(hwnd) or ""
    except Exception:
        pass
    if title:
        msg += f" ({title})"
    return True, msg


def capture_flicker_result(beside: str = "") -> Tuple[bool, str]:
    """闪变结束时把 Oxygen 结果页存到录波旁边。空白图不保存。"""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    base = (beside or "").strip()
    if base:
        folder = base if os.path.isdir(base) else (os.path.dirname(os.path.abspath(base)) or "")
    else:
        folder = ""
    if not folder:
        from utils.wt_save_path import ensure_dewetron_save_dir

        folder = ensure_dewetron_save_dir()
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"flicker_oxygen_{stamp}.png")
    return capture_oxygen_window(path)


def _grab_screen_rect(left: int, top: int, right: int, bottom: int):
    try:
        from PIL import ImageGrab
    except ImportError:
        return None
    try:
        return ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
    except TypeError:
        try:
            return ImageGrab.grab(bbox=(left, top, right, bottom))
        except Exception:
            return None
    except Exception:
        return None


def _grab_printwindow(hwnd: int):
    """PrintWindow(PW_RENDERFULLCONTENT)。64 位句柄必须按指针传，否则会抓到空图。"""
    try:
        import ctypes
        from ctypes import wintypes

        from PIL import Image
    except ImportError:
        return None

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetWindowDC.argtypes = [wintypes.HWND]
    user32.GetWindowDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, ctypes.c_uint]
    user32.PrintWindow.restype = wintypes.BOOL
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi32.SelectObject.restype = wintypes.HGDIOBJ
    gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi32.DeleteObject.restype = wintypes.BOOL
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteDC.restype = wintypes.BOOL
    gdi32.GetDIBits.argtypes = [
        wintypes.HDC,
        wintypes.HBITMAP,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_uint,
    ]
    gdi32.GetDIBits.restype = ctypes.c_int

    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    width = int(rect.right - rect.left)
    height = int(rect.bottom - rect.top)
    if width < 50 or height < 50:
        return None

    hwnd_dc = user32.GetWindowDC(hwnd)
    if not hwnd_dc:
        return None
    mem_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, width, height)
    old = gdi32.SelectObject(mem_dc, bitmap) if mem_dc and bitmap else None
    img = None
    try:
        if not mem_dc or not bitmap:
            return None
        # 2 = PW_RENDERFULLCONTENT，能抓到普通 GDI 抓不到的窗口内容
        if not user32.PrintWindow(hwnd, mem_dc, 2):
            return None

        class _BitmapInfoHeader(ctypes.Structure):
            _fields_ = [
                ("biSize", ctypes.c_uint32),
                ("biWidth", ctypes.c_int32),
                ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16),
                ("biBitCount", ctypes.c_uint16),
                ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32),
                ("biXPelsPerMeter", ctypes.c_int32),
                ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32),
                ("biClrImportant", ctypes.c_uint32),
            ]

        header = _BitmapInfoHeader()
        header.biSize = ctypes.sizeof(_BitmapInfoHeader)
        header.biWidth = width
        header.biHeight = -height
        header.biPlanes = 1
        header.biBitCount = 32
        buf = ctypes.create_string_buffer(width * height * 4)
        lines = gdi32.GetDIBits(mem_dc, bitmap, 0, height, buf, ctypes.byref(header), 0)
        if not lines:
            return None
        img = Image.frombuffer("RGB", (width, height), buf, "raw", "BGRX", 0, 1).copy()
    finally:
        if mem_dc and old:
            gdi32.SelectObject(mem_dc, old)
        if bitmap:
            gdi32.DeleteObject(bitmap)
        if mem_dc:
            gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(hwnd, hwnd_dc)
    return img


def build_trip_screenshot_path(save_path: str, *, stamp: Optional[str] = None) -> str:
    """与录波 CSV 同目录：{stem}_trip_{stamp}.png。"""
    from utils.wt_save_path import ensure_dewetron_save_dir

    stamp = stamp or time.strftime("%Y%m%d_%H%M%S")
    base = (save_path or "").strip()
    if base:
        folder = os.path.dirname(os.path.abspath(base)) or ensure_dewetron_save_dir()
        stem = os.path.splitext(os.path.basename(base))[0] or "dewetron"
    else:
        folder = ensure_dewetron_save_dir()
        stem = "dewetron"
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{stem}_trip_{stamp}.png")
