# -*- coding: utf-8 -*-
"""交互冒烟：网页 AC 配置 → 连接计划 → 品牌端口校验（不连真实电源）。"""
from __future__ import annotations

from utils.iot_auto_connect import (
    explain_ac_brand_port_mismatch,
    prepare_jobs_from_cloud_instruments,
)

CASES = [
    {
        "name": "截图同款：Chroma网口 + 502（应拦截）",
        "inst": {
            "slot": "ac",
            "kind": "ac",
            "brand": "chroma_ip",
            "host": "192.168.40.210",
            "port": 502,
            "resource": "192.168.40.210:502",
        },
        "expect_block": True,
    },
    {
        "name": "爱科正确：itech + 502",
        "inst": {
            "slot": "ac",
            "kind": "ac",
            "brand": "itech",
            "host": "192.168.40.210",
            "port": 502,
            "resource": "192.168.40.210:502",
        },
        "expect_target": "ac_itech",
    },
    {
        "name": "致茂正确：chroma_ip + 2101",
        "inst": {
            "slot": "ac",
            "kind": "ac",
            "brand": "chroma_ip",
            "host": "192.168.40.210",
            "port": 2101,
            "resource": "192.168.40.210:2101",
        },
        "expect_target": "ac_chroma_ip",
    },
]


def main() -> int:
    failed = 0
    for case in CASES:
        inst = case["inst"]
        mismatch = explain_ac_brand_port_mismatch(
            brand=str(inst.get("brand") or ""),
            port=inst.get("port"),
        )
        jobs = prepare_jobs_from_cloud_instruments([inst])
        target = jobs[0][1].get("target") if jobs else None
        print("==", case["name"])
        print("  mismatch:", mismatch or "(无)")
        print("  plan:", target, "jobs=", len(jobs))
        if case.get("expect_block"):
            if not mismatch:
                print("  FAIL: 应拦截品牌端口错配")
                failed += 1
            else:
                print("  OK: 网页/桌面会提示", mismatch[:40], "…")
            continue
        if mismatch:
            print("  FAIL: 不应拦截", mismatch)
            failed += 1
            continue
        if target != case.get("expect_target"):
            print("  FAIL: target", target, "!=", case.get("expect_target"))
            failed += 1
            continue
        print("  OK")
    print("RESULT", "PASS" if failed == 0 else f"FAIL({failed})")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
