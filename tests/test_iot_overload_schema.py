# -*- coding: utf-8 -*-
from utils.iot_overload_schema import default_widgets, field_names, load_overload_schema


def test_overload_schema_loaded():
    s = load_overload_schema()
    assert s["testType"] == "overload"
    assert len(s["fields"]) >= 40


def test_default_widgets_keys():
    w = default_widgets()
    assert "textEdit_S1_AC_VOLT" in w
    assert set(field_names()) >= set(w.keys())
