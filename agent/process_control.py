# -*- coding: utf-8 -*-
"""本机启动 / 停止 / 查询 IOT Agent 进程（供桌面一键按钮使用）。"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def pid_file() -> Path:
    return repo_root() / ".solar_agent.pid"


def config_file() -> Path:
    return repo_root() / "config" / "solar_agent.json"


def _read_pid() -> Optional[int]:
    p = pid_file()
    if not p.is_file():
        return None
    try:
        return int(p.read_text(encoding="utf-8").strip().splitlines()[0])
    except (ValueError, OSError):
        return None


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        import psutil

        return psutil.pid_exists(pid)
    except Exception:
        # Windows fallback
        if os.name == "nt":
            try:
                out = subprocess.check_output(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    text=True,
                    errors="ignore",
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                return str(pid) in out
            except Exception:
                return False
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def is_running() -> bool:
    pid = _read_pid()
    if pid is None:
        return False
    if _pid_alive(pid):
        return True
    try:
        pid_file().unlink(missing_ok=True)
    except TypeError:
        if pid_file().is_file():
            pid_file().unlink()
    except OSError:
        pass
    return False


def status_text() -> str:
    if not config_file().is_file():
        return "未配置（请先 setup_SolarAgentConfig / 填入令牌）"
    if is_running():
        return f"运行中 (pid={_read_pid()})"
    return "未运行"


def start_agent() -> Tuple[bool, str]:
    """后台启动 Agent。返回 (ok, message)。"""
    if is_running():
        return True, f"Agent 已在运行 (pid={_read_pid()})"
    cfg = config_file()
    if not cfg.is_file():
        return False, "缺少 config/solar_agent.json，请先配置 Agent 令牌"
    root = repo_root()
    env = os.environ.copy()
    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(
            subprocess, "DETACHED_PROCESS", 0x00000008
        )
    try:
        # 优先 uv run，与项目惯例一致
        cmd = ["uv", "run", "python", "-m", "agent"]
        proc = subprocess.Popen(
            cmd,
            cwd=str(root),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
    except FileNotFoundError:
        try:
            proc = subprocess.Popen(
                [sys.executable, "-m", "agent"],
                cwd=str(root),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
                close_fds=True,
            )
        except Exception as exc:
            return False, f"启动失败: {exc}"
    except Exception as exc:
        return False, f"启动失败: {exc}"
    try:
        pid_file().write_text(str(proc.pid), encoding="utf-8")
    except OSError:
        pass
    return True, f"已启动 Agent (pid={proc.pid})"


def stop_agent() -> Tuple[bool, str]:
    pid = _read_pid()
    if pid is None or not _pid_alive(pid):
        try:
            pid_file().unlink(missing_ok=True)
        except Exception:
            pass
        return True, "Agent 未在运行"
    try:
        import psutil

        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(timeout=5)
        except Exception:
            p.kill()
    except Exception:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        else:
            try:
                os.kill(pid, 15)
            except OSError as exc:
                return False, f"停止失败: {exc}"
    try:
        pid_file().unlink(missing_ok=True)
    except Exception:
        pass
    return True, f"已停止 Agent (pid={pid})"
