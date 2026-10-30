# -*- coding: utf-8 -*-
"""屏幕图是否为空、仪器回传的图像块怎么剥出来。不连真机。"""
from __future__ import annotations

import os
from typing import Optional, Tuple

from PIL import Image


def is_blank_image(img: Image.Image) -> bool:
    """几乎单色的图（全黑、全白、GDI 抓到的空帧）视为没截到画面。"""
    gray = img.convert("L")
    lo, hi = gray.getextrema()
    if hi - lo >= 24:
        return False
    small = gray.resize((32, 32), Image.Resampling.NEAREST)
    colors = small.getcolors(32 * 32)
    if colors is not None and len(colors) <= 2:
        return True
    return hi - lo < 12


def looks_like_image(data: bytes) -> bool:
    if len(data) < 32:
        return False
    return (
        data.startswith(b"\x89PNG")
        or data.startswith(b"BM")
        or data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"II*\x00")
        or data.startswith(b"MM\x00*")
    )


def extract_image_bytes(raw: bytes) -> bytes:
    """从 IEEE 488.2 块或带 SCPI 头的缓冲里取出图片字节。"""
    data = bytes(raw or b"")
    if looks_like_image(data):
        return _trim_image(data)
    parsed = _parse_ieee488_block(data)
    if parsed and looks_like_image(parsed):
        return _trim_image(parsed)
    for magic in (b"\x89PNG", b"BM", b"\xff\xd8\xff", b"II*\x00", b"MM\x00*"):
        idx = data.find(magic)
        if idx >= 0 and looks_like_image(data[idx:]):
            return _trim_image(data[idx:])
    return b""


def _trim_image(data: bytes) -> bytes:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return data
    pos = 8
    while pos + 8 <= len(data):
        length = int.from_bytes(data[pos : pos + 4], "big")
        ctype = data[pos + 4 : pos + 8]
        nxt = pos + 12 + length
        if nxt > len(data) or length < 0:
            return data
        if ctype == b"IEND":
            return data[:nxt]
        pos = nxt
    return data


def _parse_ieee488_block(data: bytes) -> bytes:
    start = data.find(b"#")
    if start < 0 or start + 2 >= len(data):
        return b""
    ndigits = data[start + 1] - ord("0")
    if ndigits < 1 or ndigits > 9:
        return b""
    size_at = start + 2
    if size_at + ndigits > len(data):
        return b""
    try:
        nbytes = int(data[size_at : size_at + ndigits])
    except ValueError:
        return b""
    body = data[size_at + ndigits : size_at + ndigits + nbytes]
    if len(body) != nbytes:
        return b""
    return body


def save_usable_image(img: Image.Image, path: str) -> Tuple[bool, str]:
    """空白图不落盘。返回 (ok, message)。"""
    if img is None:
        return False, "没有画面"
    if is_blank_image(img):
        return False, "截到的是空白画面，未保存"
    folder = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(folder, exist_ok=True)
    out = img.convert("RGB")
    out.save(path, format="PNG")
    return True, f"已保存截图: {path} ({out.size[0]}x{out.size[1]})"


def load_usable_bytes(data: bytes) -> Tuple[Optional[Image.Image], str]:
    body = extract_image_bytes(data)
    if not body:
        return None, f"回传不是图片（{len(data or b'')} 字节）"
    try:
        from io import BytesIO

        img = Image.open(BytesIO(body))
        img.load()
    except Exception as exc:
        return None, f"图片无法打开: {exc}"
    if is_blank_image(img):
        return None, "仪器回传的是空白画面"
    return img, ""
