# -*- coding: utf-8 -*-
"""本机互斥：云任务 vs 本地 UI 手动试验。"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        import psutil

        return bool(psutil.pid_exists(pid))
    except Exception:
        pass
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, int(pid))
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


class LocalMutex:
    """
    基于文件的简单互斥（同机多进程约定）。
    - Agent 执行云任务前 acquire(owner=\"agent\")
    - 桌面 UI 手动开测前可 acquire(owner=\"ui\")（后续接入）
    - 对方已占用则失败
    - 持有者 PID 已退出时自动清锁，避免关软件后永久卡「等待台架确认」
    """

    # UI 锁超过此时长且无有效心跳语义时也可清（PID 丢失的兜底）
    STALE_TTL_SEC = 120.0

    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> Optional[dict]:
        if not self.path.is_file():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def _unlink(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except TypeError:
            if self.path.is_file():
                self.path.unlink()
        except OSError:
            pass

    def clear_if_stale(self, *, ttl_sec: Optional[float] = None) -> bool:
        """
        持有者进程已死，或锁文件过旧 → 删除锁。
        返回 True 表示清理了陈旧锁。
        """
        data = self._read()
        if not data:
            return False
        try:
            pid = int(data.get("pid") or 0)
        except (TypeError, ValueError):
            pid = 0
        if pid > 0 and _pid_alive(pid):
            return False
        # 无 pid 或 pid 已死：再看时间戳兜底（避免误清刚写入但 pid 瞬时查失败）
        limit = float(self.STALE_TTL_SEC if ttl_sec is None else ttl_sec)
        at = str(data.get("at") or "").strip()
        age_ok_to_clear = True
        if at and pid > 0:
            # pid 已确认死亡 → 立刻清
            age_ok_to_clear = True
        elif at and pid <= 0:
            try:
                ts = time.mktime(time.strptime(at, "%Y-%m-%d %H:%M:%S"))
                age_ok_to_clear = (time.time() - ts) >= limit
            except Exception:
                age_ok_to_clear = True
        if not age_ok_to_clear:
            return False
        self._unlink()
        return True

    def is_held_by_other(self, owner: str) -> Optional[str]:
        self.clear_if_stale()
        data = self._read()
        if not data:
            return None
        held = str(data.get("owner") or "")
        if held and held != owner:
            return held
        return None

    def acquire(self, owner: str, meta: str = "") -> bool:
        other = self.is_held_by_other(owner)
        if other:
            return False
        payload = {
            "owner": owner,
            "pid": os.getpid(),
            "meta": meta or "",
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return True

    def release(self, owner: str) -> None:
        data = self._read()
        if not data:
            return
        if str(data.get("owner") or "") != owner:
            return
        self._unlink()

    def force_clear(self) -> None:
        """启动/退出时清理本机锁，避免残留挡住云开测。"""
        self._unlink()
