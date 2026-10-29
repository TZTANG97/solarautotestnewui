# -*- coding: utf-8 -*-
import json
from pathlib import Path
from threading import Thread

from utils.status_json_devices import measures_from_supply_command, note_supply_command, status_json_lock


def test_parse_volt_freq_and_output():
    assert measures_from_supply_command("VOLT 230.5")["voltage"] == "230.5"
    assert measures_from_supply_command("FREQ 50")["frequency"] == "50"
    assert measures_from_supply_command("OUTP OFF")["output"] == "off"
    assert measures_from_supply_command("OUTP ON")["output"] == "on"
    assert measures_from_supply_command("*IDN?") == {}


def test_note_supply_command_updates_status_json(tmp_path: Path):
    path = tmp_path / "status.json"
    path.write_text(
        json.dumps(
            {"devices": [{"name": "交流电源", "connected": True, "voltage": "220", "measures": {"voltage": "220"}}]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    assert note_supply_command(str(path), device_name="交流电源", command="VOLT 240")
    data = json.loads(path.read_text(encoding="utf-8"))
    ac = data["devices"][0]
    assert ac["voltage"] == "240"
    assert ac["measures"]["voltage"] == "240"


def _rewrite_progress(path: Path):
    """与试验进度落盘相同：持锁读整份再只改 project。"""
    with status_json_lock(str(path)):
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("project", {})["progress"] = 10
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_progress_rewrite_does_not_drop_voltage(tmp_path: Path):
    path = tmp_path / "status.json"
    path.write_text(
        json.dumps({"devices": [{"name": "交流电源", "voltage": "220"}], "project": {}}, ensure_ascii=False),
        encoding="utf-8",
    )
    errors = []

    def bump_voltage():
        try:
            for volts in ("231", "240", "251"):
                note_supply_command(str(path), device_name="交流电源", command=f"VOLT {volts}")
        except Exception as exc:
            errors.append(exc)

    def bump_progress():
        try:
            for _ in range(8):
                _rewrite_progress(path)
        except Exception as exc:
            errors.append(exc)

    threads = [Thread(target=bump_voltage), Thread(target=bump_progress)]
    for item in threads:
        item.start()
    for item in threads:
        item.join()
    assert errors == []
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["devices"][0]["voltage"] == "251"
    assert data["project"]["progress"] == 10
