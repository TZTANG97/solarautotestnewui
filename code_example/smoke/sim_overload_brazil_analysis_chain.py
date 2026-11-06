# -*- coding: utf-8 -*-
"""无真机模拟：过载 + 巴西 Ordinance 140 → 结案分析 →（可选）模拟 upload_report。

不连仪器、不连 IOT 开测；用样例 CSV 假装台架已跑完。

用法（在 solarautotestnewui 根目录）::

    uv run python code_example/sim_overload_brazil_analysis_chain.py
    uv run python code_example/sim_overload_brazil_analysis_chain.py --upload-mock
    uv run python code_example/sim_overload_brazil_analysis_chain.py --keep

环境::

    SOLAR_DATA_ANALYSIS_ROOT  默认 E:\\MyProject\\SolarTestDataAnalysisApp
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIXTURE_DIR = ROOT / "tests" / "fixtures" / "brazil_overload_542"


def main() -> int:
    ap = argparse.ArgumentParser(description="模拟过载巴西分析全链路（无真机）")
    ap.add_argument(
        "--analysis-root",
        default="",
        help="SolarTestDataAnalysisApp 根目录（默认读环境变量或本机常见路径）",
    )
    ap.add_argument(
        "--upload-mock",
        action="store_true",
        help="模拟 IOT upload_report：把将上传的文件清单写到 upload_mock.json",
    )
    ap.add_argument(
        "--keep",
        action="store_true",
        help="保留临时台架目录（默认结束后删除）",
    )
    ap.add_argument("--pn", type=float, default=10000, help="额定功率 Pn（W）")
    ap.add_argument("--semax", type=float, default=0, help="SeMax，0 表示=Pn")
    args = ap.parse_args()

    if not FIXTURE_DIR.is_dir() or not list(FIXTURE_DIR.glob("*.csv")):
        print("FAIL: 缺少样例 CSV", FIXTURE_DIR)
        return 2

    if args.analysis_root:
        import os

        os.environ["SOLAR_DATA_ANALYSIS_ROOT"] = str(Path(args.analysis_root))

    from utils.iot_data_analysis_bridge import (
        remember_analysis_input_dir,
        run_analysis_after_job,
    )
    from utils.iot_data_analysis_map import PHASE1_PILOT, resolve_analysis_target

    target = resolve_analysis_target(
        test_type=PHASE1_PILOT["test_type"],
        solar_standard=PHASE1_PILOT["solar_standard"],
    )
    if not target:
        print("FAIL: 标准映射失败")
        return 2
    print("1) 映射:", target)

    tmp = Path(tempfile.mkdtemp(prefix="sim_br_overload_"))
    try:
        # 假装台架 command_data 已有过载 CSV
        data_dir = tmp / "command_save_files" / "command_data" / "overload_sim_job"
        data_dir.mkdir(parents=True)
        for src in FIXTURE_DIR.glob("*.csv"):
            shutil.copy2(src, data_dir / src.name)
        print("2) 假台架 CSV:", data_dir)
        for p in sorted(data_dir.glob("*.csv")):
            print("   -", p.name)

        job = {
            "id": 91001,
            "testType": "overload",
            "widgets": {
                "solarStandard": "br_ord140",
                "analysis_Pn": args.pn,
                "analysis_SeMax": args.semax or args.pn,
            },
            "params": {},
        }
        result = {
            "status": "success",
            "result_summary": {
                "testType": "overload",
                "report_files": [
                    {"path": str(p), "name": p.name} for p in data_dir.glob("*.csv")
                ],
            },
        }

        print("3) 假结案 success → remember CSV 目录")
        remember_analysis_input_dir(result, tmp)

        print("4) 调分析 BRAZIL_140 / 5.4.2 …")
        info = run_analysis_after_job(
            repo_root=tmp, job=job, result=result, timeout_sec=180
        )
        print("   ran=", info.get("ran"), "success=", info.get("success"))
        if info.get("reason"):
            print("   reason=", info.get("reason"))
        if not info.get("success"):
            print("FAIL:", json.dumps(info, ensure_ascii=False, default=str)[:2000])
            return 1

        out_files = [Path(x) for x in (info.get("output_files") or [])]
        print("5) 分析产出:")
        for p in out_files:
            print("   -", p.name, "→", p)

        listed = (result.get("result_summary") or {}).get("report_files") or []
        analysis_listed = [
            x
            for x in listed
            if isinstance(x, dict)
            and (
                x.get("kind") == "analysis_report"
                or "analysis_reports" in str(x.get("path") or "")
            )
        ]
        print("6) 回填 report_files(analysis):", len(analysis_listed))

        if args.upload_mock:
            # 模拟 main_loop: collect + upload_report（不连 IOT）
            upload_plan = []
            for item in listed:
                if not isinstance(item, dict):
                    continue
                path = Path(str(item.get("path") or ""))
                if path.is_file():
                    upload_plan.append(
                        {
                            "job_id": job["id"],
                            "path": str(path),
                            "name": item.get("name") or path.name,
                            "kind": item.get("kind") or "raw_or_analysis",
                            "mock": "would call client.upload_report",
                        }
                    )
            mock_path = tmp / "upload_mock.json"
            mock_path.write_text(
                json.dumps(upload_plan, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print("7) 模拟上传清单:", mock_path)
            for u in upload_plan:
                print("   upload_report", u["job_id"], u["name"], f"({u['kind']})")
        else:
            print("7) 跳过上传模拟（加 --upload-mock 可写 upload_mock.json）")

        meta = (result.get("result_summary") or {}).get("data_analysis") or {}
        print("\n=== 模拟链路 OK ===")
        print("台架临时目录:", tmp)
        print("data_analysis.success:", meta.get("success", info.get("success")))
        print("output_dir:", info.get("output_dir"))
        if args.keep:
            print("(已保留临时目录，可自行查看 analysis_reports/)")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
