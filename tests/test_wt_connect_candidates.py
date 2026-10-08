# -*- coding: utf-8 -*-
"""WT 连接候选资源串：避免只试少数形式导致 RSRC_NFOUND。"""
from devices.wt_controller import WT3000Controller


def test_wt_candidates_for_ip_port():
    ctrl = WT3000Controller(lambda *a, **k: None, lambda *a, **k: None, rm=None)
    cands = ctrl._candidate_resources("192.168.40.19:5025")
    assert "TCPIP0::192.168.40.19::5025::SOCKET" in cands
    assert "TCPIP0::192.168.40.19::INSTR" in cands
    assert "TCPIP0::192.168.40.19::inst0::INSTR" in cands
    # 旧错误写法不应再优先（缺 board index）
    assert cands[0].startswith("TCPIP0::")


def test_wt_candidates_for_bare_ip():
    ctrl = WT3000Controller(lambda *a, **k: None, lambda *a, **k: None, rm=None)
    cands = ctrl._candidate_resources("192.168.40.19")
    assert "TCPIP0::192.168.40.19::5025::SOCKET" in cands
    assert "TCPIP0::192.168.40.19::INSTR" in cands
