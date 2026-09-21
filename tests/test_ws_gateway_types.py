# -*- coding: utf-8 -*-
from agent.ws_gateway import (
    TYPE_CONTROL,
    TYPE_CONTROL_RETURN,
    TYPE_INSTRUMENT_STATUS,
    TYPE_START,
    iot_base_to_ws_url,
)


def test_iot_base_to_ws_url():
    assert iot_base_to_ws_url("https://www.example.com/nss").startswith("wss://")
    assert "/nss/" in iot_base_to_ws_url("https://www.example.com/nss")
    assert iot_base_to_ws_url("http://127.0.0.1:18082/nss").startswith("ws://")


def test_message_type_constants():
    assert TYPE_CONTROL == "control_instrument"
    assert TYPE_CONTROL_RETURN == "control_instrument_return"
    assert TYPE_INSTRUMENT_STATUS == "instrument_status"
    assert TYPE_START == "startexper"
