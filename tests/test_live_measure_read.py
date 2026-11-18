# -*- coding: utf-8 -*-
from utils.live_measure_read import append_history, parse_numeric_list, split_item_names, zip_items


def test_parse_skips_absolute_time():
    values = parse_numeric_list(':NUM:NORM:VALue? 2026-09-21 14:17:38,230.1,1.5')
    assert values == [230.1, 1.5]


def test_zip_items_drops_nan():
    mapped = zip_items(["U", "I"], [230.0, float("nan")])
    assert mapped == {"U": 230.0}


def test_append_history_keeps_channels_aligned():
    history = {}
    append_history(history, {"U": 1.0}, limit=2)
    append_history(history, {"U": 2.0, "I": 3.0}, limit=2)
    assert history["U"] == [1.0, 2.0]
    assert history["I"][1] == 3.0
    assert history["I"][0] != history["I"][0]


def test_split_item_names():
    assert split_item_names(":NUM:NORM:ITEMs? U1,I1") == ["U1", "I1"]
