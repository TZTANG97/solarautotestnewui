# -*- coding: utf-8 -*-
"""WT3000 网口旧协议：组帧 / 登录 / *IDN?。"""
from __future__ import annotations

from devices.wt3000_legacy_ethernet import (
    YokogawaLegacySocketHandle,
    encode_frame,
    parse_socket_resource,
    recv_frame,
    try_idn_over_legacy,
)
from devices.wt_controller import WT3000Controller


def test_encode_frame_empty_password():
    assert encode_frame(b"") == b"\x80\x00\x00\x00"


def test_encode_frame_anonymous():
    assert encode_frame(b"anonymous") == b"\x80\x00\x00\x09anonymous"


def test_parse_socket_resource():
    assert parse_socket_resource("TCPIP0::192.168.40.19::10001::SOCKET") == (
        "192.168.40.19",
        10001,
    )
    assert parse_socket_resource("192.168.40.19:10001") == ("192.168.40.19", 10001)


class _FakeSock:
    def __init__(self, data: bytes):
        self._buf = bytearray(data)
        self.sent = []
        self.timeout = None

    def settimeout(self, value):
        self.timeout = value

    def sendall(self, data):
        self.sent.append(bytes(data))

    def recv(self, size):
        if not self._buf:
            raise TimeoutError("timed out")
        take = min(int(size), len(self._buf))
        piece = bytes(self._buf[:take])
        del self._buf[:take]
        return piece

    def close(self):
        return None


def test_recv_frame_single_packet():
    payload = b"YOKOGAWA,WT3000,1,1.0\n"
    sock = _FakeSock(encode_frame(payload))
    assert recv_frame(sock) == payload


def test_legacy_handle_query_strips_header():
    idn = b"YOKOGAWA,WT3000,ABC,1.0\n"
    sock = _FakeSock(encode_frame(idn))
    handle = YokogawaLegacySocketHandle(sock, "192.168.40.19", 10001)
    assert "WT3000" in handle.query("*IDN?")
    assert sock.sent[0] == encode_frame(b"*IDN?")


def test_try_idn_over_legacy_login_and_idn(monkeypatch):
    stream = b"".join(
        [
            encode_frame(b"username"),
            encode_frame(b"password"),
            encode_frame(b"OK"),
            encode_frame(b"YOKOGAWA,WT3000,1,1.0\n"),
        ]
    )

    def _fake_create(addr, timeout=None):
        return _FakeSock(stream)

    monkeypatch.setattr(
        "devices.wt3000_legacy_ethernet.socket.create_connection",
        _fake_create,
    )
    monkeypatch.setattr("devices.wt3000_legacy_ethernet.time.sleep", lambda *_: None)
    handle, idn = try_idn_over_legacy("192.168.40.19", 10001, timeout_s=1.0)
    assert handle is not None
    assert "WT3000" in idn
    assert len(handle._sock.sent) == 3
    assert handle._sock.sent[0] == encode_frame(b"anonymous")
    assert handle._sock.sent[1] == encode_frame(b"")


def test_legacy_retries_when_port_refuses(monkeypatch):
    calls = {"n": 0}

    class _Ok(_FakeSock):
        pass

    stream = b"".join(
        [
            encode_frame(b"username"),
            encode_frame(b"password"),
            encode_frame(b"OK"),
            encode_frame(b"YOKOGAWA,WT3000,1,1.0\n"),
        ]
    )

    def _fake_create(addr, timeout=None):
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionRefusedError(
                "[WinError 10061] 由于目标计算机积极拒绝，无法连接。"
            )
        return _FakeSock(stream)

    monkeypatch.setattr(
        "devices.wt3000_legacy_ethernet.socket.create_connection",
        _fake_create,
    )
    monkeypatch.setattr("devices.wt3000_legacy_ethernet.time.sleep", lambda *_: None)
    handle, idn = try_idn_over_legacy("192.168.40.19", 10001, timeout_s=1.0)
    assert calls["n"] == 3
    assert handle is not None
    assert "WT3000" in idn


def test_controller_falls_back_to_legacy_after_plain_timeout(monkeypatch):
    class _Log:
        def info(self, *a, **k):
            return None

    class _BadHandle:
        timeout = None
        write_termination = None
        read_termination = None

        def query(self, cmd):
            raise TimeoutError("VI_ERROR_TMO")

        def close(self):
            return None

    class _RM:
        def open_resource(self, name):
            raise AssertionError(f"10001 不应先开裸 SCPI: {name}")

    ctrl = WT3000Controller(_Log(), lambda *a, **k: None, rm=_RM())

    class _LegacyHandle:
        resource_name = "TCPIP0::192.168.40.19::10001::SOCKET"

        def write(self, cmd):
            return None

        def query(self, cmd):
            return "YOKOGAWA,WT3000,1,1.0"

        def close(self):
            return None

    monkeypatch.setattr(
        "devices.wt_controller.try_idn_over_legacy",
        lambda host, port, timeout_s=10.0: (_LegacyHandle(), "YOKOGAWA,WT3000,1,1.0"),
    )
    monkeypatch.setattr(
        ctrl,
        "_candidate_resources",
        lambda tcp: ["TCPIP0::192.168.40.19::10001::SOCKET"],
    )

    import pyvisa

    monkeypatch.setattr(
        pyvisa,
        "ResourceManager",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no @py")),
    )

    handle, ok = ctrl.connect("192.168.40.19:10001")
    assert ok == "1"
    assert ctrl.connected
    assert handle is not None


def test_explicit_10001_does_not_open_raw_scpi_first(monkeypatch):
    """填 10001 时先登录。不能先开 5025，也不能对 10001 裸发 *IDN?。"""
    opened = []

    class _Log:
        def info(self, *a, **k):
            return None

    class _RM:
        def open_resource(self, name):
            opened.append(name)
            raise AssertionError(f"不应先开裸 SCPI: {name}")

    class _LegacyHandle:
        def write(self, cmd):
            return None

        def close(self):
            return None

    def _legacy(host, port, timeout_s=10.0):
        assert (host, int(port)) == ("192.168.40.19", 10001)
        return _LegacyHandle(), "YOKOGAWA,WT3004E,1,1.0"

    ctrl = WT3000Controller(_Log(), lambda *a, **k: None, rm=_RM())
    monkeypatch.setattr("devices.wt_controller.try_idn_over_legacy", _legacy)
    import pyvisa

    monkeypatch.setattr(
        pyvisa,
        "ResourceManager",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no @py")),
    )
    _handle, ok = ctrl.connect("192.168.40.19:10001")
    assert ok == "1"
    assert opened == []
    assert ctrl.resource.endswith("::10001::SOCKET")


def test_legacy_timeout_does_not_open_another_socket(monkeypatch):
    """10001 已经接通但登录失败时，不能再去敲 5025 / VXI-11，否则仪器报忙碌。"""
    opened = []

    class _Log:
        def info(self, *a, **k):
            return None

    class _RM:
        def open_resource(self, name):
            opened.append(name)
            raise AssertionError(name)

    def _legacy(host, port, timeout_s=10.0):
        return None, "timed out"

    ctrl = WT3000Controller(_Log(), lambda *a, **k: None, rm=_RM())
    monkeypatch.setattr("devices.wt_controller.try_idn_over_legacy", _legacy)
    monkeypatch.setattr("devices.wt_controller.time.sleep", lambda *_: None)
    _handle, ok = ctrl.connect("192.168.40.19:10001")
    assert ok == "0"
    assert opened == []
