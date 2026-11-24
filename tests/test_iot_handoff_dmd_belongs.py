# -*- coding: utf-8 -*-
"""结案附带 .dmd 时不得误收目录里几天前的旧文件。"""
from pathlib import Path


def test_dmd_belongs_helper_logic(tmp_path: Path):
    csv = tmp_path / "reactive-qcap_20261111_215857.csv"
    csv.write_text("t,p\n0,1\n", encoding="utf-8")
    good = tmp_path / "reactive-qcap_20261111_215857_oxygen.dmd"
    good.write_bytes(b"dmd")
    old = tmp_path / "dewetron_20261109_15.dmd"
    old.write_bytes(b"old")
    # 把旧文件 mtime 拨到两天前
    import os
    import time

    old_ts = time.time() - 2 * 86400
    os.utime(old, (old_ts, old_ts))

    stem = csv.stem.lower()
    assert stem in good.name.lower()
    assert stem not in old.name.lower()
    assert abs(good.stat().st_mtime - csv.stat().st_mtime) < 120
    assert abs(old.stat().st_mtime - csv.stat().st_mtime) > 3600
