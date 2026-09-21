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
        return "未配置（将尝试自动上线）"
    try:
        import json

        data = json.loads(config_file().read_text(encoding="utf-8"))
        token = str(data.get("agent_token") or "").strip()
        pid = str(data.get("pythonid") or "").strip()
        if not token or token.startswith("请填写"):
            return f"已上报待添加设备" + (f" ({pid})" if pid else "")
    except Exception:
        pass
    if is_running():
        return f"运行中 (pid={_read_pid()})"
    return "未运行"


def _hidden_popen_kwargs():
    """Windows 下后台启动时隐藏控制台（避免多出一个黑窗/Windows Terminal）。"""
    kwargs = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
    }
    if os.name != "nt":
        kwargs["close_fds"] = True
        return kwargs
    # 不要同时用 DETACHED_PROCESS：部分环境下反而会再挂一个可见控制台
    kwargs["creationflags"] = int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = int(getattr(subprocess, "SW_HIDE", 0))
        kwargs["startupinfo"] = si
    except Exception:
        pass
    return kwargs


def _agent_launch_commands() -> list:
    """优先当前解释器 / pythonw，避免再走 `uv run` 弹窗。"""
    cmds = []
    exe = Path(sys.executable).resolve() if sys.executable else None
    if exe is not None and exe.is_file():
        if os.name == "nt":
            pythonw = exe.with_name("pythonw.exe")
            if pythonw.is_file():
                cmds.append([str(pythonw), "-m", "agent"])
        cmds.append([str(exe), "-m", "agent"])
    # 最后才回退 uv（可能闪窗，仅当上面都不可用）
    cmds.append(["uv", "run", "python", "-m", "agent"])
    return cmds


def start_agent(*, allow_without_token: bool = False) -> Tuple[bool, str]:
    """后台启动 Agent（无控制台窗口）。返回 (ok, message)。"""
    if is_running():
        return True, f"Agent 已在运行 (pid={_read_pid()})"
    cfg = config_file()
    if not cfg.is_file():
        return False, "缺少 config/solar_agent.json"
    try:
        import json

        data = json.loads(cfg.read_text(encoding="utf-8"))
        token = str(data.get("agent_token") or "").strip()
        if not allow_without_token and (not token or token.startswith("请填写")):
            return False, "config/solar_agent.json 尚无有效令牌"
    except Exception:
        return False, "无法读取 Agent 配置"
    root = repo_root()
    env = os.environ.copy()
    for k in ("PYTHONUNBUFFERED",):
        env.pop(k, None)
    popen_kwargs = _hidden_popen_kwargs()
    last_exc: Optional[BaseException] = None
    proc = None
    for cmd in _agent_launch_commands():
        try:
            proc = subprocess.Popen(cmd, cwd=str(root), env=env, **popen_kwargs)
            break
        except FileNotFoundError as exc:
            last_exc = exc
            continue
        except Exception as exc:
            last_exc = exc
            continue
    if proc is None:
        return False, f"启动失败: {last_exc}"
    try:
        pid_file().write_text(str(proc.pid), encoding="utf-8")
    except OSError:
        pass
    return True, f"已启动 Agent (pid={proc.pid})"


def ensure_agent_running(*, silent: bool = True) -> Tuple[bool, str]:
    """软件启动时调用：无令牌则自动向 IOT 登记，再后台拉起 Agent。"""
    try:
        from agent.bootstrap import ensure_configured_and_start

        return ensure_configured_and_start()
    except Exception as exc:
        if not silent:
            return False, str(exc)
        return False, f"自动配置/启动 Agent 失败: {exc}"


def _terminate_process_tree(pid: int, *, timeout_sec: float = 5.0) -> None:
    """结束 pid 及其子进程（uv/python 包装层残留）。"""
    try:
        import psutil

        root = psutil.Process(pid)
        children = root.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except Exception:
                pass
        try:
            root.terminate()
        except Exception:
            pass
        _, alive = psutil.wait_procs([root, *children], timeout=timeout_sec)
        for p in alive:
            try:
                p.kill()
            except Exception:
                pass
        return
    except Exception:
        pass
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    else:
        try:
            os.kill(pid, 15)
        except OSError:
            pass


def _iter_repo_agent_pids() -> list:
    """扫描本仓库目录下仍在跑的 ``python -m agent``（含 bat 手动启动）。"""
    root = str(repo_root().resolve()).lower()
    found: list = []
    try:
        import psutil
    except Exception:
        return found
    for proc in psutil.process_iter(["pid", "cmdline", "cwd"]):
        try:
            info = proc.info or {}
            cmd = info.get("cmdline") or []
            if not isinstance(cmd, (list, tuple)) or len(cmd) < 2:
                continue
            low = [str(x).lower() for x in cmd]
            is_agent = False
            for i in range(len(low) - 1):
                if low[i] == "-m" and low[i + 1] in ("agent", "agent.__main__", "agent.main_loop"):
                    is_agent = True
                    break
            if not is_agent:
                continue
            cwd = str(info.get("cwd") or "").lower()
            if cwd and (cwd == root or cwd.startswith(root + os.sep) or cwd.startswith(root + "/")):
                found.append(int(info["pid"]))
                continue
            # cwd 为空时：命令行里带本仓库路径也算
            joined = " ".join(low)
            if root.replace("\\", "/") in joined.replace("\\", "/"):
                found.append(int(info["pid"]))
        except Exception:
            continue
    return found


def stop_agent() -> Tuple[bool, str]:
    pid = _read_pid()
    if pid is None or not _pid_alive(pid):
        try:
            pid_file().unlink(missing_ok=True)
        except Exception:
            pass
        return True, "Agent 未在运行"
    _terminate_process_tree(pid)
    try:
        pid_file().unlink(missing_ok=True)
    except Exception:
        pass
    return True, f"已停止 Agent (pid={pid})"


def stop_agent_for_app_exit() -> Tuple[bool, str]:
    """主界面退出时调用：停掉 pid 文件记录的 Agent，并清掉同仓库残留进程。"""
    msgs: list = []
    ok, msg = stop_agent()
    msgs.append(msg)
    orphans = _iter_repo_agent_pids()
    cleaned = 0
    for opid in orphans:
        if not _pid_alive(opid):
            continue
        _terminate_process_tree(opid)
        cleaned += 1
    if cleaned:
        msgs.append(f"已清理残留 Agent {cleaned} 个")
    try:
        pid_file().unlink(missing_ok=True)
    except Exception:
        pass
    return True, "; ".join(msgs)