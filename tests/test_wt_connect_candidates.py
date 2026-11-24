# -*- coding: utf-8 -*-
"""WT 连接候选资源串：避免只试少数形式导致 RSRC_NFOUND。"""
from devices.wt_controller import WT3000Controller


def test_wt_candidates_for_ip_port():
    ctrl = WT3000Controller(lambda *a, **k: None, lambda *a, **k: None, rm=None)
    cands = ctrl._candidate_resources("192.168.40.19:5025")
    # 显式 5025（WT5000）必须排在第一位
    assert cands[0] == "TCPIP0::192.168.40.19::5025::SOCKET"
    assert "TCPIP0::192.168.40.19::INSTR" in cands
    assert "TCPIP0::192.168.40.19::inst0::INSTR" in cands


def test_wt_candidates_for_bare_ip():
    ctrl = WT3000Controller(lambda *a, **k: None, lambda *a, **k: None, rm=None)
    cands = ctrl._candidate_resources("192.168.40.19")
    assert cands[0] == "TCPIP0::192.168.40.19::5025::SOCKET"
    assert "TCPIP0::192.168.40.19::10001::SOCKET" in cands
    assert "TCPIP0::192.168.40.19::INSTR" in cands
    assert ctrl._legacy_first_resource("192.168.40.19") == ""
    assert ctrl._legacy_first_resource("192.168.40.19:5025") == ""
    assert ctrl._legacy_first_resource("192.168.40.19:10001").endswith("::10001::SOCKET")
    remembered = ctrl._candidate_resources("192.168.40.19:10001")
    assert remembered[0] == "TCPIP0::192.168.40.19::10001::SOCKET"
    assert remembered.index("TCPIP0::192.168.40.19::10001::SOCKET") < remembered.index(
        "TCPIP0::192.168.40.19::5025::SOCKET"
    )


def test_wt_candidates_skip_power_port():
    ctrl = WT3000Controller(lambda *a, **k: None, lambda *a, **k: None, rm=None)
    cands = ctrl._candidate_resources("192.168.40.100:502")
    assert all("::502::" not in item for item in cands)
    assert cands[0] == "TCPIP0::192.168.40.100::5025::SOCKET"


class _Log:
    def info(self, *args, **kwargs):
        return None


def _controller():
    return WT3000Controller(_Log(), lambda *a, **k: None, rm=None)


def test_socket_open_does_not_set_baud():
    touched = []

    class Handle:
        def __setattr__(self, name, value):
            touched.append(name)
            object.__setattr__(self, name, value)

    class RM:
        def open_resource(self, name):
            return Handle()

    handle = _controller()._try_open(RM(), "TCPIP0::192.168.40.19::10001::SOCKET")
    assert "baud_rate" not in touched
    assert handle.write_termination == "\n"


def test_socket_idn_plain_timeout_raises_for_legacy_fallback():
    queries = []

    class Handle:
        def __init__(self):
            self.timeout = None
            self.write_termination = None
            self.read_termination = None
            self.resource_name = "TCPIP0::192.168.40.19::10001::SOCKET"

        def query(self, cmd):
            queries.append((cmd, self.write_termination, self.timeout))
            raise TimeoutError("VI_ERROR_TMO (-1073807339): Timeout expired")

        def close(self):
            return None

    class RM:
        def open_resource(self, name):
            return Handle()

    try:
        _controller()._open_identified(RM(), "TCPIP0::192.168.40.19::10001::SOCKET")
        raised = False
    except TimeoutError:
        raised = True
    assert raised
    # 裸 SCPI 只试一轮 LF；WT3000 改由 connect() 走横河旧协议
    assert queries == [("*IDN?", "\n", 2000)]


def test_resource_not_found_does_not_retry_terminator():
    opens = []

    class RM:
        def open_resource(self, name):
            opens.append(name)
            raise RuntimeError("VI_ERROR_RSRC_NFOUND (-1073807343)")

    try:
        _controller()._open_identified(RM(), "TCPIP0::192.168.40.19::10001::SOCKET")
        raised = False
    except RuntimeError:
        raised = True
    assert raised
    assert opens == ["TCPIP0::192.168.40.19::10001::SOCKET"]


def test_later_resource_not_found_keeps_idn_timeout():
    from devices.wt_controller import choose_wt_connect_error

    shown = choose_wt_connect_error(
        RuntimeError("VI_ERROR_RSRC_NFOUND (-1073807343)"),
        socket_timeout_error=TimeoutError("VI_ERROR_TMO: Timeout expired"),
    )
    assert "TMO" in str(shown)


def test_wt_candidates_rewrite_power_visa():
    ctrl = WT3000Controller(lambda *a, **k: None, lambda *a, **k: None, rm=None)
    cands = ctrl._candidate_resources("TCPIP0::192.168.40.100::502::SOCKET")
    assert "TCPIP0::192.168.40.100::502::SOCKET" not in cands
    assert "TCPIP0::192.168.40.100::5025::SOCKET" in cands
