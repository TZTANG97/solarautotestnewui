# -*- coding: utf-8 -*-
"""启动「模拟工况机」Agent：接 IOT 任务，不跑仪器，落样例 CSV 后走结案分析/上传。

前置
----
1. 在 IOT 已有一台台架（或测试服用 announce 领过令牌）
2. 复制配置并填写令牌::

       copy config\\solar_agent.sim.example.json config\\solar_agent.sim.json
       （编辑 agent_token / pythonid / iot_base）

3. 本机有 SolarTestDataAnalysisApp（过载巴西分析），或设 SOLAR_DATA_ANALYSIS_ROOT

启动::

    cd /d E:\\solarautotestnewui
    uv run python code_example/run_sim_bench_agent.py

IOT 开测
--------
选该 PythonID 绑定的台架 → 试验「过载」→ 标准「巴西 Ordinance 140」→ 填 Pn → 开始。

Agent 会：领取任务 → sim 落 CSV → success 结案 → 调 BRAZIL_140/5.4.2 → upload_report。
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="启动无真机模拟工况机 Agent")
    ap.add_argument(
        "--config",
        default=str(ROOT / "config" / "solar_agent.sim.json"),
        help="默认 config/solar_agent.sim.json",
    )
    ap.add_argument(
        "--iot-base",
        default="",
        help="覆盖 IOT 地址（也可用环境变量 SOLAR_IOT_BASE）",
    )
    args = ap.parse_args()

    cfg = Path(args.config)
    example = ROOT / "config" / "solar_agent.sim.example.json"
    if not cfg.is_file():
        if example.is_file() and cfg.name == "solar_agent.sim.json":
            print(f"未找到 {cfg}")
            print(f"请先复制: copy {example} {cfg}")
            print("并填写 agent_token / pythonid / iot_base")
            return 2
        print(f"配置不存在: {cfg}")
        return 2

    os.environ.setdefault("SOLAR_AGENT_EXECUTION_MODE", "sim")
    os.environ.setdefault("SOLAR_AGENT_SIM_INSTRUMENTS", "1")
    os.environ["SOLAR_AGENT_CONFIG"] = str(cfg.resolve())
    if args.iot_base.strip():
        os.environ["SOLAR_IOT_BASE"] = args.iot_base.strip().rstrip("/")

    # 确保能 import agent
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    print("=== 模拟工况机 Agent ===")
    print("config:", cfg)
    print("execution_mode: sim（落样例 CSV，不接仪器）")
    print("IOT 开测：过载 + 巴西 Ordinance 140 + Pn → 开始")
    print("Ctrl+C 结束")
    print()

    from agent.main_loop import main as agent_main

    return int(agent_main(["--config", str(cfg)]))


if __name__ == "__main__":
    raise SystemExit(main())
