# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("SCPITestWave.py")
t = p.read_text(encoding="utf-8")

old_visa = """            print("[DEBUG_STARTUP] 4/9 VISA ResourceManager...", flush=True)
            # rm = visa.ResourceManager(local_file_path + '/visa32.dll')
            rm = _create_visa_resource_manager(local_file_path)
            str1 = rm.list_resources()
            print(f"[DEBUG_STARTUP]    list_resources = {str1}", flush=True)
            if len(str1) > 0:
                iNumber = len(str1)
                print(iNumber)
                EQUList = str1
            else:
                EQUList = ['未发现可连接设备']
"""

new_visa = """            print("[DEBUG_STARTUP] 4/9 VISA ResourceManager...", flush=True)
            # rm = visa.ResourceManager(local_file_path + '/visa32.dll')
            rm = _create_visa_resource_manager(local_file_path)
            # Do NOT list_resources() on the UI startup path — NI-VISA LAN/USB scan
            # can freeze the process for several seconds before the window appears.
            EQUList = ['未发现可连接设备']
            print("[DEBUG_STARTUP]    list_resources deferred (non-blocking startup)", flush=True)
"""

if old_visa not in t:
    raise SystemExit("visa block not found")
t = t.replace(old_visa, new_visa, 1)

old_timer = """                QTimer.singleShot(800, _startup_auto_connect_last_devices)
"""
new_timer = """                # After first paint; VISA scan is also deferred here so open isn't multi-second frozen
                def _deferred_visa_then_autoconnect():
                    global EQUList
                    try:
                        str1 = rm.list_resources()
                        print(f"[DEBUG_STARTUP]    deferred list_resources = {str1}", flush=True)
                        EQUList = list(str1) if str1 else ['未发现可连接设备']
                    except Exception as _visa_exc:
                        print(f"[DEBUG_STARTUP]    deferred list_resources fail: {_visa_exc}", flush=True)
                        EQUList = ['未发现可连接设备']
                    try:
                        app.processEvents()
                    except Exception:
                        pass
                    _startup_auto_connect_last_devices()

                QTimer.singleShot(600, _deferred_visa_then_autoconnect)
"""

if old_timer not in t:
    raise SystemExit("timer block not found")
t = t.replace(old_timer, new_timer, 1)

p.write_text(t, encoding="utf-8")
print("patched visa defer")
