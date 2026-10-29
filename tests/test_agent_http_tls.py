# -*- coding: utf-8 -*-
"""HTTPS 出站：各系统先走 Python ssl，握手失败才回退 curl。"""
from __future__ import annotations

import ssl
import urllib.error

from agent import http_tls


def test_https_context_is_tls12():
    ctx = http_tls.https_context()
    assert ctx.minimum_version == ssl.TLSVersion.TLSv1_2
    assert ctx.maximum_version == ssl.TLSVersion.TLSv1_2
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.options & ssl.OP_LEGACY_SERVER_CONNECT


def test_https_uses_python_ssl_before_curl(monkeypatch):
    calls = []

    def urllib_ok(method, url, data, headers, timeout):
        calls.append("urllib")
        return 200, b"{}"

    def curl_unused(*_a, **_k):
        calls.append("curl")
        raise AssertionError("握手成功时不应调用 curl")

    monkeypatch.setattr(http_tls, "_via_urllib", urllib_ok)
    monkeypatch.setattr(http_tls, "_via_curl", curl_unused)
    status, body = http_tls.http_exchange("POST", "https://www.laidecloud.com/nss/api", data=b"{}")
    assert status == 200
    assert body == b"{}"
    assert calls == ["urllib"]


def test_handshake_eof_retries_then_curl(monkeypatch):
    calls = []

    def urllib_fail(method, url, data, headers, timeout):
        calls.append("urllib")
        raise urllib.error.URLError(ssl.SSLError("UNEXPECTED_EOF_WHILE_READING"))

    def curl_ok(method, url, data, headers, timeout):
        calls.append("curl")
        return 200, b"ok"

    monkeypatch.setattr(http_tls, "_via_urllib", urllib_fail)
    monkeypatch.setattr(http_tls, "_via_curl", curl_ok)
    monkeypatch.setattr(http_tls, "_curl_bin", lambda: "curl")
    monkeypatch.setattr(http_tls.time, "sleep", lambda _s: None)
    status, body = http_tls.http_exchange("POST", "https://www.laidecloud.com/nss/api", data=b"{}")
    assert status == 200
    assert body == b"ok"
    assert calls == ["urllib", "urllib", "curl"]


def test_http_error_does_not_fall_back_to_curl(monkeypatch):
    def urllib_http(method, url, data, headers, timeout):
        return 500, b"nope"

    def curl_unused(*_a, **_k):
        raise AssertionError("HTTP 错误不是握手失败")

    monkeypatch.setattr(http_tls, "_via_urllib", urllib_http)
    monkeypatch.setattr(http_tls, "_via_curl", curl_unused)
    status, body = http_tls.http_exchange("GET", "https://www.laidecloud.com/nss/")
    assert status == 500
    assert body == b"nope"
