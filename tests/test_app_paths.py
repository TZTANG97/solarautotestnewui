# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


def test_data_root_env_override(monkeypatch, tmp_path):
    from utils import app_paths

    app_paths.clear_path_cache()
    monkeypatch.setenv("SOLARAUTOTEST_DATA", str(tmp_path / "data"))
    monkeypatch.delenv("SOLARAUTOTEST_RUNTIME", raising=False)
    got = app_paths.data_root(force_reload=True)
    assert Path(got) == (tmp_path / "data").resolve()
    assert Path(got).is_dir()


def test_data_subdir_and_runtime(monkeypatch, tmp_path):
    from utils import app_paths

    app_paths.clear_path_cache()
    monkeypatch.setenv("SOLARAUTOTEST_DATA", str(tmp_path / "data"))
    monkeypatch.setenv("SOLARAUTOTEST_RUNTIME", str(tmp_path / "rt"))
    sub = app_paths.data_subdir("command_save_files", "dewetron_presets")
    assert Path(sub).is_dir()
    assert Path(sub).name == "dewetron_presets"
    rt = app_paths.runtime_root(force_reload=True)
    assert Path(rt) == (tmp_path / "rt").resolve()


def test_paths_ini_in_home(monkeypatch, tmp_path):
    from utils import app_paths

    app_paths.clear_path_cache()
    monkeypatch.delenv("SOLARAUTOTEST_DATA", raising=False)
    monkeypatch.delenv("SOLARAUTOTEST_RUNTIME", raising=False)
    home = tmp_path / "install"
    cfg = home / "config_files"
    cfg.mkdir(parents=True)
    (cfg / "paths.ini").write_text(
        "[paths]\ndata_root = {}\nruntime_root = {}\n".format(
            tmp_path / "ini_data", tmp_path / "ini_rt"
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SOLARAUTOTEST_HOME", str(home))
    assert Path(app_paths.data_root(force_reload=True)) == (tmp_path / "ini_data").resolve()
    assert Path(app_paths.runtime_root(force_reload=True)) == (tmp_path / "ini_rt").resolve()
