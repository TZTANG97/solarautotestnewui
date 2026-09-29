from pathlib import Path
p = Path(r"E:\solarautotestnewui\pyproject.toml")
t = p.read_text(encoding="utf-8")
needle = '    "paho-mqtt>=2.1.0",'
insert = '    "paho-mqtt>=2.1.0",\n    "pyserial>=3.5",'
if "pyserial" in t:
    print("pyserial already")
elif needle not in t:
    raise SystemExit("paho needle missing")
else:
    p.write_text(t.replace(needle, insert, 1), encoding="utf-8")
    print("pyserial added")
print("local_endpoints head:")
print(Path(r"E:\solarautotestnewui\agent\local_endpoints.py").read_text(encoding="utf-8")[:200])
