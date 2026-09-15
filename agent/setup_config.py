# -*- coding: utf-8 -*-
"""
生成 / 更新本机 Agent 配置（不进 Git）。

用法：
  uv run python -m agent.setup_config
  uv run python -m agent.setup_config --iot-base https://云地址/nss --token sat_1_xxx
  uv run python -m agent.setup_config --interactive
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent.config import _repo_root


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="配置 Solar Agent（写入 config/solar_agent.json）")
    parser.add_argument("--iot-base", default="", help="IOT 根路径，如 http://127.0.0.1:18088/nss")
    parser.add_argument("--token", default="", help="台架 Agent 令牌明文")
    parser.add_argument("--dry-run", default="true", choices=["true", "false"])
    parser.add_argument("--interactive", "-i", action="store_true", help="交互填写")
    args = parser.parse_args(argv)

    example = _repo_root() / "config" / "solar_agent.example.json"
    target = _repo_root() / "config" / "solar_agent.json"
    data = {}
    if target.is_file():
        data = json.loads(target.read_text(encoding="utf-8"))
    elif example.is_file():
        data = json.loads(example.read_text(encoding="utf-8"))

    iot_base = (args.iot_base or data.get("iot_base") or "http://127.0.0.1:18088/nss").rstrip("/")
    token = (args.token or data.get("agent_token") or "").strip()
    dry = args.dry_run == "true"

    if args.interactive or not token or token.startswith("请填写"):
        print("=== Solar Agent 本机配置 ===")
        print("说明：令牌在 IOT 网页「光伏自动化试验 → 台架管理」创建/重置时只显示一次。")
        print("      每台工控机用各自台架的令牌；不要把 solar_agent.json 提交到 Git。\n")
        ib = input(f"IOT 地址 [{iot_base}]: ").strip()
        if ib:
            iot_base = ib.rstrip("/")
        tk = input(f"Agent 令牌 [{'(已有)' if token and not token.startswith('请') else '必填'}]: ").strip()
        if tk:
            token = tk
        dr = input(f"dry_run 仅模拟不控仪器? (Y/n) [{'Y' if dry else 'n'}]: ").strip().lower()
        if dr in ("n", "no", "0", "false"):
            dry = False
        elif dr in ("y", "yes", "1", "true", ""):
            dry = True

    if not token or token.startswith("请填写"):
        print("错误：仍未填写 agent_token。请先在 IOT 创建台架拿到令牌。", file=sys.stderr)
        # 仍写入 iot_base，方便下一步只补 token
        data.update(
            {
                "iot_base": iot_base,
                "agent_token": "",
                "poll_interval_sec": int(data.get("poll_interval_sec") or 15),
                "heartbeat_interval_sec": int(data.get("heartbeat_interval_sec") or 15),
                "dry_run": dry,
                "mutex_path": data.get("mutex_path") or "",
                "agent_version": data.get("agent_version") or "0.1.0",
            }
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"已写入部分配置: {target}")
        return 2

    data.update(
        {
            "iot_base": iot_base,
            "agent_token": token,
            "poll_interval_sec": int(data.get("poll_interval_sec") or 15),
            "heartbeat_interval_sec": int(data.get("heartbeat_interval_sec") or 15),
            "dry_run": dry,
            "mutex_path": data.get("mutex_path") or "",
            "agent_version": data.get("agent_version") or "0.1.0",
            "comment": "本机私有配置，勿提交 Git。其他电脑请各自运行 setup_SolarAgentConfig.bat",
        }
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写入: {target}")
    print(f"  iot_base = {iot_base}")
    print(f"  dry_run  = {dry}")
    print(f"  token    = {token[:12]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
