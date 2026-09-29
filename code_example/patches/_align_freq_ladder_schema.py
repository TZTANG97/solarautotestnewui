# -*- coding: utf-8 -*-
"""对齐过频降载 / 欠频升载：Web schema 只展示桌面可见的 FrequencyLadder，隐藏 S3~S17 旧卡片。"""
from __future__ import annotations

import json
import re
from pathlib import Path

IOT = Path(r"E:/IOT/iot/app/services/solar_test_schemas")
SOLAR = Path(r"E:/solarautotestnewui/utils")

SPECS = {
    "guopinjiangzai": {
        "iot": IOT / "guopinjiangzai_fields.json",
        "sw": SOLAR / "iot_guopinjiangzai_schema_data.json",
        "step3_title": "③ 过频设置",
        "labels": {
            "checkBox_S3": "启用频率台阶",
            "textEdit_FrequencyLadder_VOLT": "交流电压(V)",
            "textEdit_FrequencyLadder": "频率Hz(list)",
            "textEdit_FrequencyLadder_TIME": "每点驻留",
            "comboBox_FrequencyLadder_TIME": "驻留单位",
        },
        "defaults": {
            "checkBox_S3": True,
            "textEdit_FrequencyLadder_VOLT": "230",
            "textEdit_FrequencyLadder": "50,50.25,50.7,51.15,50.7,50.25,50",
            "textEdit_FrequencyLadder_TIME": "60",
            "comboBox_FrequencyLadder_TIME": "秒",
        },
    },
    "qianpinshengzai": {
        "iot": IOT / "qianpinshengzai_fields.json",
        "sw": SOLAR / "iot_qianpinshengzai_schema_data.json",
        "step3_title": "③ 欠频设置",
        "labels": {
            "checkBox_S3": "启用频率台阶",
            "textEdit_FrequencyLadder_VOLT": "交流电压(V)",
            "textEdit_FrequencyLadder": "频率Hz(list)",
            "textEdit_FrequencyLadder_TIME": "每点驻留",
            "comboBox_FrequencyLadder_TIME": "驻留单位",
        },
        "defaults": {
            "checkBox_S3": True,
            "textEdit_FrequencyLadder_VOLT": "230",
            "textEdit_FrequencyLadder": "50,49.75,49.5,49.25,49.0,49.25,49.5,49.75,50",
            "textEdit_FrequencyLadder_TIME": "60",
            "comboBox_FrequencyLadder_TIME": "秒",
        },
    },
}

# 桌面可见控件（step3）；其余 S3~S17 旧卡片控件隐藏
_VISIBLE = {
    "checkBox_S3",
    "textEdit_FrequencyLadder",
    "textEdit_FrequencyLadder_VOLT",
    "textEdit_FrequencyLadder_TIME",
    "comboBox_FrequencyLadder_TIME",
}

_LEGACY_RE = re.compile(
    r"^(?:checkBox_S(?:[3-9]|1[0-7])|"
    r"textEdit_S(?:[3-9]|1[0-7])_|"
    r"comboBox_S(?:[3-9]|1[0-7])_)"
)


def _is_legacy_step3(name: str) -> bool:
    if name in _VISIBLE:
        return False
    return bool(_LEGACY_RE.match(name or ""))


def _patch(path: Path, meta: dict) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for g in data.get("groups") or []:
        if g.get("id") == "step3_freq":
            if g.get("title") != meta["step3_title"]:
                g["title"] = meta["step3_title"]
                changed += 1
    labels = meta["labels"]
    defaults = meta["defaults"]
    for f in data.get("fields") or []:
        name = f.get("name") or ""
        if name in labels and f.get("label") != labels[name]:
            f["label"] = labels[name]
            changed += 1
        if name in defaults and f.get("default") != defaults[name]:
            f["default"] = defaults[name]
            changed += 1
        if f.get("group") == "step3_freq" and _is_legacy_step3(name):
            if not f.get("hidden"):
                f["hidden"] = True
                f["uiHint"] = f.get("uiHint") or "legacy_hidden"
                changed += 1
        elif name in _VISIBLE and f.get("hidden"):
            f.pop("hidden", None)
            if f.get("uiHint") == "legacy_hidden":
                f.pop("uiHint", None)
            changed += 1
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def main() -> None:
    for key, meta in SPECS.items():
        for kind in ("iot", "sw"):
            path = meta[kind]
            n = _patch(path, meta)
            print(f"{key} {kind}: {path.name} changed={n}")


if __name__ == "__main__":
    main()
