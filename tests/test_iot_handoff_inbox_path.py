# -*- coding: utf-8 -*-
from pathlib import Path

from agent.config import _repo_root
from agent.runners import get_runner
from agent.ui_mutex import default_mutex_path
from utils.iot_ui_handoff import IotUiHandoffService


def test_inbox_paths_align_to_install_root():
    root = _repo_root()
    runner = get_runner("overload", execution_mode="handoff")
    assert Path(runner.repo_root).resolve() == root.resolve()
    assert default_mutex_path().resolve() == (root / ".solar_agent_mutex").resolve()
    svc = IotUiHandoffService(repo_root=root, resolve_overload_ui=lambda: None, overload_append=lambda: None)
    dirs = [p.resolve() for p in svc._inbox_dirs()]
    assert (root / "iot_job_inbox").resolve() in dirs
    assert (root / "agent" / "iot_job_inbox").resolve() in dirs
