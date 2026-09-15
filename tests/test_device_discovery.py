# -*- coding: utf-8 -*-
import socket
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QComboBox

from utils.device_discovery import (
    FoundDevice,
    classify_idn,
    classify_port,
    connect_plan,
    devices_from_last_resources,
    list_visa_resources,
    merge_devices,
    parse_host_port,
    probe_scpi_idn,
    scan_lan,
    tcp_open,
    validate_assignments,
)


def test_classify_idn_scope_and_wt():
    kind, _brand = classify_idn("YOKOGAWA,DL850E,123,1.0")
    assert kind == "scope"
    kind, _brand = classify_idn("YOKOGAWA,WT3000,SN,FW")
    assert kind == "wt"
    kind, _brand = classify_idn("TEKTRONIX,MSO64,B000,1")
    assert kind == "scope"
    kind, _brand = classify_idn("DEWETRON,OXYGEN,1,1")
    assert kind == "dew"


def test_classify_idn_chroma_ac_dc():
    kind, brand = classify_idn("CHROMA,61815,0,0")
    assert kind == "ac" and brand == "chroma"
    kind, brand = classify_idn("CHROMA,62012P-80-60,0,0")
    assert kind == "dc"


def test_parse_does_not_split_serial_resources():
    assert parse_host_port("ASRL3::INSTR") == ("", None)
    assert parse_host_port("USB0::0x0B21::WT3000::INSTR") == ("", None)
    assert parse_host_port("192.168.40.11:10001") == ("192.168.40.11", 10001)
    assert parse_host_port("TCPIP0::192.168.40.10::INSTR")[0] == "192.168.40.10"


def test_classify_port_dew_and_modbus():
    kind, brand, proto = classify_port(10001)
    assert kind == "dew" and proto == "dew_socket"
    kind, brand, proto = classify_port(8080)
    assert kind == "modbus" and brand == "itech"
    from utils.device_discovery import ALL_PROBE_PORTS

    assert 23 not in ALL_PROBE_PORTS


def test_validate_assignments_requires_human_slot():
    dev = FoundDevice(resource="192.168.1.10:502")
    assert "人手指定" in validate_assignments([(True, "", dev)])
    assert validate_assignments([(True, "dc1", dev)]) is None
    other = FoundDevice(resource="192.168.1.11:502")
    assert "重复" in validate_assignments([(True, "dc1", dev), (True, "dc1", other)])
    assert "勾选" in validate_assignments([(False, "dc1", dev)])


def test_merge_prefers_lan_over_offline_last():
    last = FoundDevice(
        resource="192.168.40.11",
        host="192.168.40.11",
        source="上次",
        extra={"offline": True},
        idn="未响应：端口未开放",
    )
    lan = FoundDevice(
        resource="192.168.40.11:10001",
        host="192.168.40.11",
        port=10001,
        idn="DEWETRON,OXYGEN,1,1",
        kind_hint="dew",
        source="局域网",
    )
    merged = merge_devices([last], [lan])
    assert len(merged) == 1
    assert merged[0].source == "局域网"
    assert merged[0].kind_hint == "dew"


def test_prefixes_include_last_host_subnet():
    from utils.device_discovery import local_ipv4_prefixes

    prefixes = local_ipv4_prefixes(extra_hosts=["10.0.0.5", "192.168.40.210"])
    assert "10.0.0" in prefixes
    assert "192.168.40" in prefixes


def test_merge_drops_bare_ip_when_ported_exists():
    bare = FoundDevice(resource="192.168.40.11", host="192.168.40.11", source="上次")
    dew = FoundDevice(
        resource="192.168.40.11:10001",
        host="192.168.40.11",
        port=10001,
        idn="DEWETRON",
        kind_hint="dew",
        source="局域网",
    )
    merged = merge_devices([bare], [dew])
    assert len(merged) == 1
    assert merged[0].port == 10001
    assert merged[0].kind_hint == "dew"


def test_connect_plan_routes_without_auto_slot():
    dew = FoundDevice(resource="192.168.40.11:10001", host="192.168.40.11", port=10001, brand_hint="dewetron")
    assert connect_plan("dew", dew)["target"] == "dew"
    ac = FoundDevice(resource="192.168.40.10:502", host="192.168.40.10", port=502, protocol="modbus", brand_hint="itech")
    plan = connect_plan("ac", ac)
    assert plan["target"] == "ac_itech"
    dc = FoundDevice(resource="192.168.40.12:502", host="192.168.40.12", port=502, protocol="modbus")
    plan = connect_plan("dc2", dc)
    assert plan["target"] == "dc_modbus" and plan["n"] == 2
    scope = FoundDevice(resource="USB0::0x0B21::DL850::INSTR")
    assert connect_plan("scope", scope)["target"] == "scope"


def test_list_visa_skips_asrl_by_default():
    class FakeRm:
        def list_resources(self):
            return ("ASRL3::INSTR", "USB0::0x0B21::X::INSTR", "TCPIP0::1.2.3.4::INSTR")

    items = list_visa_resources(FakeRm())
    assert "ASRL3::INSTR" not in items
    assert "USB0::0x0B21::X::INSTR" in items
    assert list_visa_resources(FakeRm(), include_serial=True)[0].startswith("ASRL")


def _serve_idn(idn: bytes, n: int = 6):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    port = srv.getsockname()[1]
    ready = threading.Event()

    def _run():
        ready.set()
        try:
            for _ in range(n):
                conn, _addr = srv.accept()
                conn.settimeout(2)
                try:
                    data = conn.recv(64)
                    if data:
                        conn.sendall(idn)
                finally:
                    conn.close()
        except Exception:
            pass
        finally:
            srv.close()

    threading.Thread(target=_run, daemon=True).start()
    ready.wait(1)
    return port


def test_probe_scpi_idn_local_socket():
    port = _serve_idn(b"YOKOGAWA,WT3000,SN,FW\n")
    text = probe_scpi_idn("127.0.0.1", port, timeout=1.0)
    assert "WT3000" in text


def test_scan_lan_hosts_finds_open_port():
    port = _serve_idn(b"CHROMA,61815,0,0\n")
    found = scan_lan(hosts=["127.0.0.1"], ports=(port,), timeout=0.4, skip_hosts=())
    assert any(d.host == "127.0.0.1" and d.port == port for d in found)
    hit = next(d for d in found if d.port == port)
    assert hit.kind_hint == "ac"


def test_tcp_open_closed_port_is_false():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", 0))
    unused = srv.getsockname()[1]
    srv.close()
    assert tcp_open("127.0.0.1", unused, timeout=0.15) is False


def test_devices_from_last_keeps_order():
    items = devices_from_last_resources(["192.168.1.8", "192.168.1.8:10001"])
    assert items[0].host == "192.168.1.8"
    assert items[1].port == 10001


def test_finder_dialog_lists_last_and_blocks_empty_slot(monkeypatch):
    app = QApplication.instance() or QApplication([])
    from components.device_finder_dialog import DeviceFinderDialog

    warned = []
    monkeypatch.setattr(
        "components.device_finder_dialog.QMessageBox.warning",
        lambda *args, **kwargs: warned.append(args),
    )

    dlg = DeviceFinderDialog(last_resources=["192.168.40.11:10001"])
    assert dlg._table.rowCount() == 1
    dlg._table.item(0, 0).setCheckState(Qt.Checked)
    combo = dlg._table.cellWidget(0, 4)
    assert isinstance(combo, QComboBox)
    assert combo.currentData() == ""
    dlg._on_connect()
    assert warned and dlg.checked_jobs() == []
    combo.setCurrentIndex(combo.findData("dew"))
    dlg._on_connect()
    jobs = dlg.checked_jobs()
    assert len(jobs) == 1
    assert jobs[0][0] == "dew"
    dlg.close()
    assert app is not None


def test_last_known_pairs_remembered_port(monkeypatch):
    from utils import device_discovery as dd

    def fake_history(key):
        if key == "ac.ip":
            return ["192.168.40.210"]
        if key == dd._FINDER_HISTORY_KEY:
            return []
        return []

    monkeypatch.setattr("utils.ui_field_helpers.load_history", fake_history)
    monkeypatch.setattr("utils.ui_field_helpers.last_value", lambda key, default="": "8080" if key == "ac.port" else default)
    items = dd.last_known_resources()
    assert "192.168.40.210:8080" in items


def test_enrich_marks_unreachable_last_ip(monkeypatch):
    from utils.device_discovery import FoundDevice, enrich_device

    monkeypatch.setattr("utils.device_discovery.tcp_open", lambda *a, **k: False)
    dev = FoundDevice(resource="10.0.0.5", host="10.0.0.5", source="上次")
    out = enrich_device(dev)
    assert out.extra.get("offline")
    assert "未响应" in out.display_idn()
    assert out.kind_label() == "离线"


def test_summarize_discovery_counts_offline():
    from utils.device_discovery import FoundDevice, summarize_discovery

    devices = [
        FoundDevice(resource="a", host="1.1.1.1", kind_hint="dew", source="局域网"),
        FoundDevice(resource="b", host="2.2.2.2", extra={"offline": True}),
    ]
    text = summarize_discovery(devices)
    assert "识别 1" in text
    assert "离线/未响应 1" in text

