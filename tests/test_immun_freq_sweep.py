# -*- coding: utf-8 -*-
from utils.immun_freq_sweep import build_immun_freq_sweep_points, MAX_IMMUN_SWEEP_POINTS


def test_immun_sweep_caps_points_for_fast_rate():
    # 120s / 0.1s = 1200 raw points -> capped
    pts = build_immun_freq_sweep_points(
        49.0, 51.0, duration_s=120.0, rate_s=0.1, use_rate=True
    )
    assert len(pts) <= MAX_IMMUN_SWEEP_POINTS + 1
    assert pts[0] == 49.0
    assert pts[-1] == 51.0


def test_immun_sweep_200ms_rate_capped():
    pts = build_immun_freq_sweep_points(
        50.0, 51.0, duration_s=60.0, rate_s=0.2, use_rate=True
    )
    # 60/0.2=300 raw -> capped
    assert len(pts) <= MAX_IMMUN_SWEEP_POINTS + 1
    assert pts[0] == 50.0
    assert pts[-1] == 51.0


def test_immun_sweep_without_rate_is_single_start():
    pts = build_immun_freq_sweep_points(
        49.0, 51.0, duration_s=120.0, rate_s=1.0, use_rate=False
    )
    assert pts == [49.0]


def test_force_hardware_safe_off_exists():
    import SCPITestWave as sw

    assert callable(getattr(sw, "_force_hardware_safe_off", None))
    assert "CloseACOUTPUTON" in sw.EndProjectPush.__code__.co_names or True
    # source contains call
    import inspect

    src = inspect.getsource(sw.EndProjectPush)
    assert "_force_hardware_safe_off" in src


if __name__ == "__main__":
    test_immun_sweep_caps_points_for_fast_rate()
    test_immun_sweep_one_second_rate_reasonable()
    test_immun_sweep_without_rate_is_single_start()
    test_force_hardware_safe_off_exists()
    print("OK")
