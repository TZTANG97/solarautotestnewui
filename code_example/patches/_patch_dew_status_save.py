# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("SCPITestWave.py")
t = p.read_text(encoding="utf-8")
i = t.find("def _save_device_status")
assert i >= 0, "missing _save_device_status"
j = t.find("\ndef _update_project_status", i)
assert j > i, "missing _update_project_status after save"

new = '''def _save_device_status(device_name, connected, resource="", extra=None):
    """更新 status.json 中的设备连接状态，刷新首页显示。"""
    import json
    import os
    from utils.status_json_devices import apply_device_connection, empty_status_payload

    _status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
    try:
        with open(_status_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = empty_status_payload()
    data = apply_device_connection(
        data,
        device_name=device_name,
        connected=bool(connected),
        resource=resource or "",
        extra=extra if isinstance(extra, dict) else None,
    )
    with open(_status_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 刷新首页
    if hasattr(ui, '_home_dots') and hasattr(ui, 'stackedWidget'):
        ui.stackedWidget.widget(0).update() if hasattr(ui.stackedWidget.widget(0), 'update') else None
        _reload_home_status(data)


def _dewetron_status_extra():
    """桌面德威创页当前参数，写入 status.json 供 Web 回填。"""
    try:
        from utils.status_json_devices import read_dewetron_ui_snapshot

        return read_dewetron_ui_snapshot(globals().get("uiDewetronSetting"))
    except Exception:
        return {"brand": "dewetron", "widgets": {}}
'''

t2 = t[:i] + new + t[j:]
old_call = '_save_device_status("DEWETRON", True, tcp_addr)'
new_call = '_save_device_status("DEWETRON", True, tcp_addr, extra=_dewetron_status_extra())'
count = t2.count(old_call)
t2 = t2.replace(old_call, new_call)
p.write_text(t2, encoding="utf-8")
print(f"replaced_calls={count} helper_refs={t2.count('_dewetron_status_extra')}")
