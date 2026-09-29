from pathlib import Path

p = Path(r"E:\solarautotestnewui\agent\main_loop.py")
text = p.read_text(encoding="utf-8")
if "ws_gateway.push_instrument_status()" in text and "HTTPS 心跳成功后顺便经 WS" in text:
    print("main_loop already patched")
else:
    old = """    data_hb = hb.get(\"data\") if isinstance(hb, dict) else None
    if isinstance(data_hb, dict):
        if data_hb.get(\"pythonid\"):
            client.pythonid = str(data_hb.get(\"pythonid\") or \"\")
        _handle_pending_actions(data_hb)
    return data_hb if isinstance(data_hb, dict) else None"""
    new = """    data_hb = hb.get(\"data\") if isinstance(hb, dict) else None
    if isinstance(data_hb, dict):
        if data_hb.get(\"pythonid\"):
            client.pythonid = str(data_hb.get(\"pythonid\") or \"\")
        _handle_pending_actions(data_hb)
    # HTTPS 心跳成功后顺便经 WS 推一帧串口/仪器，供网页即时刷新
    try:
        from agent import ws_gateway

        ws_gateway.push_instrument_status()
    except Exception:
        pass
    return data_hb if isinstance(data_hb, dict) else None"""
    if old not in text:
        raise SystemExit("needle not found in main_loop")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("main_loop patched ok")
