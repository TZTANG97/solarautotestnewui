# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from utils.instrument_identity import infer_brand, infer_serial, parse_usb_visa


def test_usb_chroma_vid_0a69_and_sn():
    # 官方 usb.ids：0x0A69 = Chroma ate, Inc.（不是爱科）
    vid, pid, sn = parse_usb_visa("USB0::0x0A69::0x084B::S50000002314::INSTR")
    assert vid == "0A69"
    assert pid == "084B"
    assert sn == "S50000002314"
    assert infer_brand(kind="dc", resource="USB0::0x0A69::0x084B::S50000002314::INSTR") == "CHROMA"
    assert infer_serial(kind="dc", resource="USB0::0x0A69::0x084B::S50000002314::INSTR") == "S50000002314"


def test_usb_itech_vid_2ec7():
    assert infer_brand(kind="dc", resource="USB0::0x2EC7::0x0001::SN1::INSTR") == "ITECH"


def test_tcpip_ac_chroma_sat_serial():
    res = "TCPIP0::192.168.40.10::INSTR"
    assert infer_brand(kind="ac", resource=res) == "CHROMA"
    seq = infer_serial(
        kind="ac",
        resource=res,
        slot="ac",
        host_name="SOLAR-PC-8F670",
        machine_id="deadbeefcafebabe",
    )
    assert seq.startswith("SAT-AC-SOLAR-PC-8F670-")
    assert "::" not in seq
    assert "192.168" not in seq


def test_ac_port_502_is_itech_dc_port_502_is_bluesight():
    assert infer_brand(kind="ac", resource="192.168.40.210:502") == "ITECH"
    assert infer_brand(kind="dc", resource="192.168.40.12:502") == "Bluesight"
    assert infer_brand(kind="dc", resource="TCPIP0::192.168.40.12::502::INSTR") == "Bluesight"
    assert infer_brand(kind="dc", resource="192.168.40.12:30000") == "ITECH"
    # 桌面已经写了品牌时，端口不能再把蓝点改成爱科
    assert infer_brand(kind="dc", resource="192.168.40.12:502", brand="bluesight") == "Bluesight"
    assert infer_brand(kind="dc", resource="192.168.40.12:502", brand="itech") == "ITECH"
    assert infer_brand(kind="ac", resource="192.168.40.210:502", brand="itech") == "ITECH"


def test_dew_ip_not_used_as_serial():
    seq = infer_serial(
        kind="dew",
        resource="192.168.40.24:10001",
        host_name="BENCH-A",
        machine_id="1122334455667788",
    )
    assert infer_brand(kind="dew", resource="192.168.40.24:10001") == "DEWETRON"
    assert seq == "SAT-DEW-BENCH-A-55667788"
