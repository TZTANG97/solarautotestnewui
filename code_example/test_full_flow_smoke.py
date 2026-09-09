# -*- coding: utf-8 -*-
"""整套流程关键路径冒烟（不连仪器）。"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_decorator_arg_forwarding():
    """无参函数丢弃 clicked(bool)；有参函数保留实参。"""
    import importlib.util

    # 不整包导入 SCPITestWave；就地复刻装饰器逻辑做契约测试
    def make_decorator():
        def _with_device_ui_busy(reason):
            def _decorator(fn):
                try:
                    _param_count = len(
                        [
                            p
                            for p in inspect.signature(fn).parameters.values()
                            if p.kind
                            in (
                                inspect.Parameter.POSITIONAL_ONLY,
                                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            )
                        ]
                    )
                except Exception:
                    _param_count = None

                def _wrapped(*args, **kwargs):
                    call_args = args
                    call_kwargs = kwargs
                    if (
                        _param_count == 0
                        and len(args) == 1
                        and type(args[0]) is bool
                        and not kwargs
                    ):
                        call_args = ()
                    return fn(*call_args, **call_kwargs)

                return _wrapped

            return _decorator

        return _with_device_ui_busy

    deco = make_decorator()

    @deco("x")
    def connect_dc1():
        return "ok"

    @deco("y")
    def apply_dew(name):
        return f"applied:{name}"

    assert connect_dc1() == "ok"
    assert connect_dc1(False) == "ok"  # clicked(bool)
    assert connect_dc1(True) == "ok"
    assert apply_dew("电压闪变") == "applied:电压闪变"
    assert apply_dew("过频降载") == "applied:过频降载"
    print("DECORATOR_OK")


def test_overfreq_pipeline():
    from utils.overfreq_ladder_commands import append_freq_point_rows, parse_freq_hz_list

    pts = parse_freq_hz_list("50,50.25,50.5")
    rows = []
    for f in pts:
        append_freq_point_rows(rows, "三相", "230", f, 50)
    freqs = [r for r in rows if any(str(c).upper().startswith("FREQ") for c in r)]
    assert len(freqs) == 3
    assert any("EDIT ALL" in str(c) for r in rows for c in r)
    print("OVERFREQ_OK", len(rows))


def test_scpi_probe_short():
    import socket
    from unittest.mock import patch
    from devices.scpi_socket import ScpiSocket

    s = ScpiSocket("127.0.0.1", port=None, timeout=10)
    with patch.object(ScpiSocket, "_try_connect", side_effect=socket.timeout("x")):
        try:
            s.connect()
            raise AssertionError("expected fail")
        except ConnectionError:
            pass
    print("SCPI_PROBE_OK")


def main():
    test_decorator_arg_forwarding()
    test_overfreq_pipeline()
    test_scpi_probe_short()
    # 复用已有交叉冒烟
    import runpy

    runpy.run_path(str(ROOT / "code_example" / "test_overfreq_cross_smoke.py"), run_name="__main__")
    print("FLOW_SMOKE_ALL_OK")


if __name__ == "__main__":
    main()
