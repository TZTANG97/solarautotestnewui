# -*- coding: utf-8 -*-
"""空白截图不能当成功保存。不连仪器、不抓真实窗口。"""
from __future__ import annotations

import io

from PIL import Image

from utils.screen_capture import (
    extract_image_bytes,
    is_blank_image,
    load_usable_bytes,
    save_usable_image,
)


def _png_bytes(color, size=(80, 60)) -> bytes:
    img = Image.new("RGB", size, color)
    if color == (0, 0, 0):
        pass
    else:
        px = img.load()
        px[10, 10] = (220, 40, 40)
        px[20, 20] = (40, 180, 80)
        px[30, 15] = (30, 80, 200)
        px[40, 40] = (240, 200, 40)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_solid_frame_is_blank():
    img = Image.new("RGB", (200, 120), (0, 0, 0))
    assert is_blank_image(img)


def test_colored_frame_is_not_blank():
    img = Image.new("RGB", (200, 120), (18, 22, 28))
    px = img.load()
    for x in range(0, 180, 7):
        px[x, 40] = (0, 180, 160)
        px[x, 80] = (220, 80, 60)
    assert not is_blank_image(img)


def test_png_trim_ignores_iend_bytes_inside_chunk():
    def chunk(tag: bytes, payload: bytes) -> bytes:
        return len(payload).to_bytes(4, "big") + tag + payload + b"\x00\x00\x00\x00"

    body = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", b"IEND-inside") + chunk(b"IEND", b"")
    assert extract_image_bytes(body) == body


def test_extract_ieee_block_png():
    body = _png_bytes((20, 40, 60))
    header = f"#{len(str(len(body)))}{len(body)}".encode("ascii")
    raw = b":IMAGE " + header + body + b"\n"
    got = extract_image_bytes(raw)
    assert got.startswith(b"\x89PNG")
    assert got == body


def test_blank_payload_is_rejected(tmp_path):
    img, msg = load_usable_bytes(_png_bytes((0, 0, 0)))
    assert img is None
    assert "空白" in msg
    ok, msg2 = save_usable_image(Image.new("RGB", (40, 40), (255, 255, 255)), str(tmp_path / "x.png"))
    assert ok is False
    assert not (tmp_path / "x.png").exists()
    assert "空白" in msg2


def test_usable_payload_is_saved(tmp_path):
    raw = _png_bytes((12, 18, 24))
    img, msg = load_usable_bytes(raw)
    assert img is not None
    assert msg == ""
    dest = tmp_path / "shot.png"
    ok, saved = save_usable_image(img, str(dest))
    assert ok is True
    assert dest.is_file()
    assert dest.stat().st_size > 32
    assert "shot.png" in saved
