# -*- coding: utf-8 -*-
"""Read IOT DB: discoveries / benches / equ_pythonid_online (no secrets printed)."""
from __future__ import annotations

from pathlib import Path

import pymysql

env_path = Path(r"E:\IOT\iot\.env")
cfg = {}
for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    cfg[k.strip()] = v.strip().strip('"').strip("'")

conn = pymysql.connect(
    host=cfg["DB_HOST"],
    port=int(cfg.get("DB_PORT") or 3306),
    user=cfg["DB_USER"],
    password=cfg["DB_PASSWORD"],
    database=cfg["DB_NAME"],
    charset="utf8mb4",
    connect_timeout=20,
)
cur = conn.cursor()

print("=== equ_pythonid_online (all) ===")
try:
    cur.execute(
        "SELECT python_id, del_status, create_time, update_time "
        "FROM equ_pythonid_online ORDER BY update_time DESC LIMIT 30"
    )
    rows = cur.fetchall()
    if not rows:
        print("(empty)")
    for r in rows:
        print(r)
except Exception as e:
    print("ERR", e)

print("\n=== solar_discoveries (recent) ===")
try:
    cur.execute("SHOW COLUMNS FROM solar_discoveries")
    cols = [c[0] for c in cur.fetchall()]
    print("cols:", cols)
    cur.execute("SELECT * FROM solar_discoveries ORDER BY id DESC LIMIT 20")
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print("ERR", e)

print("\n=== solar_benches ===")
try:
    cur.execute("SHOW COLUMNS FROM solar_benches")
    cols = [c[0] for c in cur.fetchall()]
    print("cols:", cols)
    cur.execute(
        "SELECT id, name, python_id, machine_id, status, last_heartbeat_at, host_name, created_at "
        "FROM solar_benches ORDER BY id DESC LIMIT 30"
    )
except Exception:
    cur.execute("SELECT * FROM solar_benches ORDER BY id DESC LIMIT 20")
for r in cur.fetchall():
    print(r)

print("\n=== equipment python_id like SOLAR% ===")
try:
    cur.execute(
        "SELECT python_id, equ_name, equ_num, del_status "
        "FROM equipments WHERE python_id LIKE 'SOLAR%' AND del_status=0 LIMIT 40"
    )
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print("ERR", e)

conn.close()
