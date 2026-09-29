# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("SCPITestWave.py")
t = p.read_text(encoding="utf-8")

old = """                # After first paint; VISA scan is also deferred here so open isn't multi-second frozen
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

new = """                # After first paint: VISA scan in a daemon thread so the home page
                # stays responsive; then auto-connect on the UI thread.
                from PyQt5.QtCore import QObject, pyqtSignal

                class _VisaBootBridge(QObject):
                    done = pyqtSignal(object)

                _visa_bridge = _VisaBootBridge(main_window)

                def _on_visa_done(resources):
                    global EQUList
                    try:
                        if resources:
                            EQUList = list(resources)
                        else:
                            EQUList = ['未发现可连接设备']
                        print(f"[DEBUG_STARTUP]    deferred list_resources = {EQUList}", flush=True)
                    except Exception as _e:
                        print(f"[DEBUG_STARTUP]    apply EQUList fail: {_e}", flush=True)
                        EQUList = ['未发现可连接设备']
                    _startup_auto_connect_last_devices()

                _visa_bridge.done.connect(_on_visa_done)

                def _visa_worker():
                    try:
                        str1 = rm.list_resources()
                        _visa_bridge.done.emit(tuple(str1) if str1 else tuple())
                    except Exception as _visa_exc:
                        print(f"[DEBUG_STARTUP]    deferred list_resources fail: {_visa_exc}", flush=True)
                        _visa_bridge.done.emit(tuple())

                def _kick_visa_scan():
                    import threading
                    threading.Thread(target=_visa_worker, name="visa-list-boot", daemon=True).start()

                QTimer.singleShot(400, _kick_visa_scan)
"""

if old not in t:
    raise SystemExit("block not found")
p.write_text(t.replace(old, new, 1), encoding="utf-8")
print("patched async visa")
