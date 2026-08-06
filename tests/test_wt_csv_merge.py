# -*- coding: utf-8 -*-
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.wt_csv_merge import append_round_to_merge, candidate_save_dirs, find_wt_csv


def test_append_round_to_merge_adds_round_column(tmp_path):
    src = tmp_path / "P100_cos0.9.CSV"
    src.write_text(
        "StoreNo,Date,P-1\n1,2026/08/05,7658\n2,2026/08/05,7660\n",
        encoding="utf-8-sig",
    )
    merge = tmp_path / "staticcosPhi_merged.CSV"
    n = append_round_to_merge(str(merge), str(src), "P100_cos0.9", delete_source=True)
    assert n == 2
    assert not src.exists()
    text = merge.read_text(encoding="utf-8-sig")
    assert text.splitlines()[0].startswith("Round,StoreNo,Date,P-1")
    assert "P100_cos0.9,1,2026/08/05,7658" in text

    src2 = tmp_path / "P90_cos1.0.CSV"
    src2.write_text(
        "StoreNo,Date,P-1\n1,2026/08/05,6900\n",
        encoding="utf-8-sig",
    )
    n2 = append_round_to_merge(str(merge), str(src2), "P90_cos1.0", delete_source=True)
    assert n2 == 1
    text2 = merge.read_text(encoding="utf-8-sig")
    assert text2.count("Round,StoreNo") == 1
    assert "P90_cos1.0,1,2026/08/05,6900" in text2


def test_find_wt_csv_prefers_existing(tmp_path):
    f = tmp_path / "P100_cos0.9.CSV"
    f.write_text("a,b\n1,2\n", encoding="utf-8")
    hit = find_wt_csv("P100_cos0.9", [str(tmp_path)], wait_s=0.1)
    assert hit and os.path.samefile(hit, f)


def test_candidate_save_dirs_dedupe():
    dirs = candidate_save_dirs(r"D:\foo", extra=[r"D:\foo", r"E:\bar"])
    assert dirs[0].lower().endswith("foo")
    assert len([d for d in dirs if d.lower().endswith("foo")]) == 1
