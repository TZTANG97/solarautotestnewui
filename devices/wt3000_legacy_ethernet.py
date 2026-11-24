# -*- coding: utf-8 -*-
"""Yokogawa WT3000 / WT1600 网口旧协议（Ethernet Legacy）。

10001 上能 TCP 握手，但裸发 ``*IDN?`` 会一直超时：仪器要先 anonymous
登录，并且每条消息带 4 字节长度头（最高位表示最后一包）。

见横河 FAQ「How to connect to legacy Yokogawa products using Ethernet protocol」。
"""
from __future__ import annotations

import socket
import struct
import time
from typing import Optional, Tuple


def _is_connection_refused(exc) -> bool:
    text = str(exc or "")
    upper = text.upper()
    return (
        "10061" in text
        or "积极拒绝" in text
        or "ACTIVELY REFUSED" in upper
        or "CONNECTION REFUSED" in upper
        or "WSAECONNREFUSED" in upper
    )


def encode_frame(payload: bytes) -> bytes:
    """编码一帧：``0x80xxxxxx`` + payload（最高位=最后一包）。"""
    data = bytes(payload or b"")
    if len(data) > 0x7FFFFFFF:
        raise ValueError("legacy ethernet payload too large")
    return struct.pack(">I", 0x80000000 | len(data)) + data


def decode_header(header: bytes) -> Tuple[int, bool]:
    if len(header) != 4:
        raise ValueError("legacy ethernet header must be 4 bytes")
    word = struct.unpack(">I", header)[0]
    return word & 0x7FFFFFFF, bool(word & 0x80000000)


def parse_socket_resource(resource_string: str) -> Tuple[str, int]:
    """从 ``TCPIP0::ip::port::SOCKET`` / ``ip:port`` 取出主机和端口。"""
    text = str(resource_string or "").strip()
    upper = text.upper()
    if upper.startswith("TCPIP") and "::" in text:
        parts = [p.strip() for p in text.split("::") if p.strip()]
        host = parts[1] if len(parts) >= 2 else ""
        port = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 10001
        return host, port
    if ":" in text:
        host, _, rest = text.partition(":")
        if rest.isdigit():
            return host.strip(), int(rest)
    if text.count(".") == 3:
        return text, 10001
    return "", 10001


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = []
    remaining = int(size)
    while remaining > 0:
        piece = sock.recv(remaining)
        if not piece:
            raise ConnectionError("WT3000 legacy socket closed while reading")
        chunks.append(piece)
        remaining -= len(piece)
    return b"".join(chunks)


def recv_frame(sock: socket.socket) -> bytes:
    """读完整一帧（可含续包），返回去掉长度头后的 payload。"""
    chunks = []
    while True:
        length, last = decode_header(_recv_exact(sock, 4))
        if length:
            chunks.append(_recv_exact(sock, length))
        if last:
            break
    return b"".join(chunks)


class YokogawaLegacySocketHandle:
    """冒充 VISA handle：``write`` / ``query`` / ``close``。"""

    def __init__(self, sock: socket.socket, host: str, port: int):
        self._sock = sock
        self.resource_name = f"TCPIP0::{host}::{int(port)}::SOCKET"
        self.timeout = 10000
        self.write_termination = "\n"
        self.read_termination = "\n"

    def _timeout_s(self) -> float:
        try:
            ms = float(self.timeout)
        except (TypeError, ValueError):
            ms = 10000.0
        if ms > 1000:
            return max(0.5, ms / 1000.0)
        return max(0.5, ms)

    def _apply_timeout(self) -> None:
        self._sock.settimeout(self._timeout_s())

    def write_payload(self, payload: bytes) -> None:
        self._apply_timeout()
        self._sock.sendall(encode_frame(payload))

    def read_payload(self) -> bytes:
        self._apply_timeout()
        return recv_frame(self._sock)

    def write(self, command) -> None:
        # 长度头已经标明结尾，不再额外补换行，避免和上位机的帧不一致。
        text = str(command or "")
        self.write_payload(text.encode("ascii", errors="ignore"))

    def query(self, command) -> str:
        self.write(command)
        raw = self.read_payload()
        return raw.decode("ascii", errors="ignore").strip()

    def close(self) -> None:
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self._sock.close()
        except Exception:
            pass


def connect_legacy_ethernet(
    host: str,
    port: int = 10001,
    *,
    username: str = "anonymous",
    password: str = "",
    timeout_s: float = 10.0,
) -> YokogawaLegacySocketHandle:
    """TCP 连接 → 读登录提示 → 发用户名/密码 → 返回可 query 的句柄。"""
    host = str(host or "").strip()
    if not host:
        raise ValueError("WT3000 legacy ethernet host is empty")
    sock = socket.create_connection((host, int(port)), timeout=float(timeout_s))
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except Exception:
        pass
    handle = YokogawaLegacySocketHandle(sock, host, int(port))
    # 登录提示马上就会来。读不到就立刻关掉，不要空等再把别的口也打开。
    handle.timeout = int(min(float(timeout_s), 3.0) * 1000)
    try:
        handle.read_payload()
        handle.write_payload(str(username or "anonymous").encode("ascii", errors="ignore"))
        handle.read_payload()
        handle.write_payload(str(password or "").encode("ascii", errors="ignore"))
        handle.read_payload()
        return handle
    except Exception:
        handle.close()
        raise


def try_idn_over_legacy(
    host: str,
    port: int = 10001,
    *,
    username: str = "anonymous",
    password: str = "",
    timeout_s: float = 10.0,
) -> Tuple[Optional[YokogawaLegacySocketHandle], str]:
    """登录后发 ``*IDN?``。成功返回 (handle, idn)，失败返回 (None, 原因)。

    裸 SCPI 刚关掉时，WT3000 会短暂拒绝第二个连接，这里多试几次。
    """
    last = ""
    for attempt in range(3):
        handle = None
        try:
            if attempt:
                time.sleep(1.0)
            handle = connect_legacy_ethernet(
                host,
                port,
                username=username,
                password=password,
                timeout_s=timeout_s,
            )
            idn = handle.query("*IDN?")
            return handle, idn
        except Exception as exc:
            last = str(exc)
            if handle is not None:
                try:
                    handle.close()
                except Exception:
                    pass
            if _is_connection_refused(exc) and attempt < 2:
                continue
            return None, last
    return None, last
