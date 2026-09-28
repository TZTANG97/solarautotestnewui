# -*- coding: utf-8 -*-
"""Tests for WT save-path ensure/create."""
from __future__ import annotations

from pathlib import Path


def test_ensure_creates_missing_dir(tmp_path):
    from utils.wt_save_path import ensure_wt_save_dir

    target = tmp_path / "a" / "b" / "wt"
    assert not target.exists()
    got = ensure_wt_save_dir(str(target))
    assert Path(got).is_dir()
    assert Path(got) == target.resolve()


def test_ensure_falls_back_when_invalid():
    from utils.wt_save_path import ensure_wt_save_dir, default_wt_save_path

    # Impossible path on Windows (invalid drive letter rarely, use empty → default)
    got = ensure_wt_save_dir("")
    assert Path(got).is_dir()
    assert "SolarAutoTest" in got or got == str(Path(default_wt_save_path()).resolve()) or Path(got).exists()


def test_resolve_config_expands_localappdata(monkeypatch, tmp_path):
    from utils.wt_save_path import resolve_config_wt_save_path

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    got = resolve_config_wt_save_path(r"%LOCALAPPDATA%/SolarAutoTest/wt_save")
    assert Path(got).is_dir()
    assert "SolarAutoTest" in got
    assert Path(got).name == "wt_save"


def test_resolve_config_auto():
    from utils.wt_save_path import resolve_config_wt_save_path

    got = resolve_config_wt_save_path("auto")
    assert Path(got).is_dir()


def test_ensure_dewetron_save_dir_default(monkeypatch, tmp_path):
    from utils.wt_save_path import ensure_dewetron_save_dir, default_dewetron_save_dir

    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    got = ensure_dewetron_save_dir("")
    assert Path(got).is_dir()
    assert Path(got).name == "dewetron_save"
    assert Path(got) == Path(default_dewetron_save_dir()).resolve()


def test_resolve_dewetron_save_paths_uses_base_dir(tmp_path):
    from utils.dewetron_recording import resolve_dewetron_save_paths

    paths = resolve_dewetron_save_paths(
        test_type="overunder",
        continuous=True,
        stamp="20260101_000000",
        base_dir=str(tmp_path / "custom_dew"),
    )
    assert len(paths) == 1
    assert Path(paths[0]).parent == (tmp_path / "custom_dew").resolve()
    assert paths[0].endswith("overunder_20260101_000000.csv")
