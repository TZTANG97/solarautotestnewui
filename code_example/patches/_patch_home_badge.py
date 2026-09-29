# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("SCPITestWave.py")
t = p.read_text(encoding="utf-8")
old = """        if name in getattr(ui, '_home_dots', {}):
            color = \"#22c55e\" if dev.get(\"connected\") else \"#ef4444\"
            ui._home_dots[name].setStyleSheet(f\"background-color: {color}; border-radius: 5px;\")
"""
new = """        if name in getattr(ui, '_home_dots', {}):
            ok = bool(dev.get(\"connected\"))
            color = \"#059669\" if ok else \"#dc2626\"
            text = \"已连接\" if ok else \"未连接\"
            badge = ui._home_dots[name]
            badge.setText(text)
            # Text badge only — never solid fill (became huge red blocks)
            badge.setStyleSheet(
                f\"color: {color}; font-size: 11px; font-weight: 700; \"
                f\"background: transparent; padding: 0;\"
            )
            try:
                badge.setMinimumSize(0, 0)
                badge.setMaximumSize(16777215, 16777215)
            except Exception:
                pass
"""
if old not in t:
    raise SystemExit("old block not found")
p.write_text(t.replace(old, new, 1), encoding="utf-8")
print("patched _reload_home_status")
