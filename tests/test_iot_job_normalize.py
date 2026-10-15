# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from agent.job_normalize import normalize_startexper_job


def test_keeps_job_id_when_experid_is_experiment():
    job = normalize_startexper_job(
        {
            "type": "startexper",
            "id": 99,
            "experid": "250",
            "params": {"experId": "250", "widgets": {}},
            "testType": "overload",
        }
    )
    assert job["id"] == 99
    assert str(job["experid"]) == "250"


def test_does_not_use_experid_as_id_when_params_have_exper():
    job = normalize_startexper_job(
        {
            "experid": "250",
            "params": {"experId": 250},
            "commands": {
                "command": json.dumps(
                    {"testType": "harmonic", "title": "h", "params": {"experId": 250}}
                )
            },
        }
    )
    assert job["id"] == 0
    assert job["testType"] == "harmonic"


def test_parses_commands_and_fallback_id():
    job = normalize_startexper_job(
        {
            "experid": "42",
            "commands": {
                "command": json.dumps(
                    {"testType": "flicker", "title": "f", "params": {"widgets": {}}}
                )
            },
        }
    )
    assert job["id"] == 42
    assert job["testType"] == "flicker"
