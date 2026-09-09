# -*- coding: utf-8 -*-
import csv
import re
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

path = "E:/solarautotestnewui/command_save_files/command_data/voltageadaptability_commands2026_08_22_13.csv"
volt = 0
with open(path, encoding="utf-8") as f:
    for row in csv.reader(f):
        if len(row) > 2 and row[1] == "write" and str(row[2]).startswith("VOLT"):
            volt += 1
        if len(row) > 6 and str(row[6]).strip() == "ASYNC_START":
            print("ASYNC_START at row", volt)
        if len(row) > 6 and str(row[6]).strip() == "WAIT_END":
            print("WAIT_END found")
print("VOLT writes", volt)
with open(path, encoding="utf-8") as f:
    row0 = f.readline()
m = re.search(r"textEdit_StopTime': '([^']+)'", row0)
print("StopTime", m.group(1) if m else "N/A")

from utils.voltage_adaptability_commands import estimate_continuous_record_01s

rows = []
with open(path, encoding="utf-8") as f:
    for row in csv.reader(f):
        rows.append(row)
wall, wait, nv, nd = estimate_continuous_record_01s(rows[1:])
print("estimate from csv rows:", wall, wait, nv, nd, "stop_sec", int(round(wall / 10.0 + 15)))
# sum col9 waits in band only (after ASYNC)
in_band = False
wsum = 0
for row in rows[1:]:
    if len(row) > 6 and str(row[6]).strip() == "ASYNC_START":
        in_band = True
    if in_band and len(row) > 9 and row[9]:
        try:
            wsum += int(row[9])
        except ValueError:
            pass
print("sum col9 wait_01s in band:", wsum)
