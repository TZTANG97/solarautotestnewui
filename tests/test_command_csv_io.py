# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.command_csv_io import ensure_command_save_dirs, write_command_csv


def test_write_command_csv_creates_missing_dirs(tmp_path):
    target = tmp_path / "command_save_files" / "command_data" / "xiebodianliu_commands_test.csv"
    assert not target.parent.exists()
    path = write_command_csv(str(target), [["AC", "query", "*IDN?"], ["DC1", "write", "OUTP ON"]])
    assert os.path.isfile(path)
    text = Path(path).read_text(encoding="utf-8")
    assert "OUTP ON" in text


def test_ensure_command_save_dirs(tmp_path):
    base = ensure_command_save_dirs(str(tmp_path / "command_save_files"))
    assert (Path(base) / "command_data").is_dir()
    assert (Path(base) / "dewetron_data").is_dir()
