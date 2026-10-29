# -*- coding: utf-8 -*-
"""公网 IOT 的 HTTPS 出站。Windows 与 Linux 都走 Python ssl。

www.laidecloud.com 是 nginx/1.10.2，只协商 TLS 1.2（ECDHE-RSA-AES128-GCM-SHA256）。
握手被掐断或超时时先重试一次；仍失败再交给本机 curl（Windows 上是 Schannel）。
"""
from __future__ import annotations

import os
import shutil
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

_HANDSHAKE_MARKERS = (
    "UNEXPECTED_EOF",
    "EOF occurred in violation of protocol",
    "handshake operation timed out",
    "WRONG_VERSION_NUMBER",
    "TLSV1_ALERT",
    "timed out",
)


def https_context() -> ssl.SSLContext:
    """限制 TLS 1.2，并允许连不支持安全重协商的老服务端。"""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    try:
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    except Exception:
        pass
    legacy = getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0)
    if legacy:
        ctx.options |= legacy
    return ctx


def _curl_bin() -> str:
    return shutil.which("curl") or shutil.which("curl.exe") or ""


def _is_handshake_problem(exc: BaseException) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return False
    reason = getattr(exc, "reason", exc)
    if isinstance(reason, (ssl.SSLError, socket.timeout, TimeoutError)):
        return True
    text = f"{type(exc).__name__}: {exc}"
    return any(mark in text for mark in _HANDSHAKE_MARKERS)


def _via_curl(method: str, url: str, data: Optional[bytes], headers: Dict[str, str], timeout: float) -> Tuple[int, bytes]:
    curl = _curl_bin()
    if not curl:
        raise RuntimeError("未找到 curl，无法访问 HTTPS")
    out_path = ""
    body_path = ""
    try:
        fd, out_path = tempfile.mkstemp(prefix="sat_http_")
        os.close(fd)
        cmd = [
            curl,
            "-sS",
            "--max-time",
            str(max(5, int(timeout))),
            "-X",
            method,
            "-o",
            out_path,
            "-w",
            "%{http_code}",
            url,
        ]
        for key, val in (headers or {}).items():
            cmd.extend(["-H", f"{key}: {val}"])
        if data is not None:
            fd2, body_path = tempfile.mkstemp(prefix="sat_body_")
            os.close(fd2)
            Path(body_path).write_bytes(data)
            cmd.extend(["--data-binary", f"@{body_path}"])
        proc = subprocess.run(
            cmd,
            capture_output=True,
            timeout=float(timeout) + 5.0,
            check=False,
        )
        code_s = (proc.stdout or b"").decode("ascii", errors="replace").strip()
        if not code_s.isdigit():
            err = (proc.stderr or b"").decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"curl 失败 rc={proc.returncode}: {err or code_s}")
        status = int(code_s)
        raw = Path(out_path).read_bytes() if out_path and os.path.exists(out_path) else b""
        return status, raw
    finally:
        for p in (out_path, body_path):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def _via_urllib(method: str, url: str, data: Optional[bytes], headers: Dict[str, str], timeout: float) -> Tuple[int, bytes]:
    req = urllib.request.Request(url, data=data, headers=dict(headers or {}), method=method)
    ctx = https_context() if url.lower().startswith("https://") else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return int(resp.status), resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read()
        return int(exc.code), detail


def http_exchange(
    method: str,
    url: str,
    *,
    data: Optional[bytes] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
) -> Tuple[int, bytes]:
    """返回 (status, body)。HTTPS 先走 Python ssl，握手失败再重试，最后才用 curl。"""
    hdrs = dict(headers or {})
    https = url.lower().startswith("https://")
    if not https:
        return _via_urllib(method, url, data, hdrs, timeout)
    last: Optional[BaseException] = None
    for attempt in range(2):
        try:
            return _via_urllib(method, url, data, hdrs, timeout)
        except Exception as exc:
            last = exc
            if not _is_handshake_problem(exc):
                raise
            if attempt == 0:
                time.sleep(0.4)
    if last is not None and _curl_bin():
        return _via_curl(method, url, data, hdrs, timeout)
    if last is not None:
        raise last
    raise RuntimeError("HTTPS 请求失败")
