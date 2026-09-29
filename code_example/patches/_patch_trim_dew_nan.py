# -*- coding: utf-8 -*-
"""Patch dewetron export to drop leading all-NaN samples."""
from __future__ import annotations

from pathlib import Path


def patch_recording() -> None:
    p = Path(r"E:\solarautotestnewui\utils\dewetron_recording.py")
    t = p.read_text(encoding="utf-8")
    if "trim_leading_all_nan_samples" in t:
        print("recording already has trim")
        return
    # add import math and function before resolve_dewetron_save_paths
    if "import math" not in t:
        t = t.replace(
            "from __future__ import annotations\n\nfrom typing import Any, List, Optional, Sequence\n",
            "from __future__ import annotations\n\nimport math\nfrom typing import Any, List, Optional, Sequence, Tuple\n",
            1,
        )
    else:
        t = t.replace(
            "from typing import Any, List, Optional, Sequence\n",
            "from typing import Any, List, Optional, Sequence, Tuple\n",
            1,
        )

    helper = '''

def _is_nan_number(value: Any) -> bool:
    try:
        return math.isnan(float(value))
    except (TypeError, ValueError):
        text = str(value or "").strip().lower()
        return text in {"nan", "null", "none", ""}


def row_values_all_nan(values: Sequence[Any]) -> bool:
    """True when every channel value is missing/NaN (leading empty Dewetron samples)."""
    if not values:
        return True
    return all(_is_nan_number(v) for v in values)


def trim_leading_all_nan_samples(
    rows: Sequence[Tuple[Any, Sequence[Any]]],
    *,
    rebase_time: bool = True,
) -> List[Tuple[float, List[float]]]:
    """Drop leading rows where all channels are NaN; optionally rebase time to 0 at first keep.

    Dewetron often emits ~0.3–0.5s of empty samples right after ACQUISITION:START.
    """
    source = list(rows or [])
    start = 0
    while start < len(source):
        _t, vals = source[start]
        if not row_values_all_nan(vals or []):
            break
        start += 1
    kept = source[start:]
    out: List[Tuple[float, List[float]]] = []
    if not kept:
        return out
    t0 = 0.0
    if rebase_time:
        try:
            t0 = float(kept[0][0])
        except (TypeError, ValueError):
            t0 = 0.0
    for raw_t, vals in kept:
        try:
            tt = float(raw_t) - t0
        except (TypeError, ValueError):
            tt = 0.0
        nums: List[float] = []
        for v in list(vals or []):
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                nums.append(float("nan"))
        out.append((tt, nums))
    return out


'''
    marker = "def resolve_dewetron_save_paths("
    if marker not in t:
        raise SystemExit("resolve marker missing")
    t = t.replace(marker, helper + marker, 1)
    p.write_text(t, encoding="utf-8")
    print("recording patched")


def patch_collector() -> None:
    p = Path(r"E:\solarautotestnewui\devices\dewetron_data_collector.py")
    t = p.read_text(encoding="utf-8")
    old = '''            rows = self.get_run_rows(run_id)
            csv_dir = os.path.dirname(csv_path)
            if csv_dir:
                os.makedirs(csv_dir, exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as output:
                writer = csv.writer(output)
                writer.writerow(header)
                expect_n = max(len(header) - 1, 0)
                for time_val, values in rows:
                    aligned = list(values or [])[:expect_n]
                    if len(aligned) < expect_n:
                        aligned.extend([float("nan")] * (expect_n - len(aligned)))
                    writer.writerow(
                        [f"{time_val:.4f}"]
                        + [f"{value:.7f}" for value in aligned]
                    )
            print(f"[Collector][export_run_to_csv] 导出完成: {csv_path} ({len(rows)} 行)")'''
    new = '''            rows = self.get_run_rows(run_id)
            try:
                from utils.dewetron_recording import trim_leading_all_nan_samples

                trimmed = trim_leading_all_nan_samples(rows, rebase_time=True)
                dropped = max(0, len(rows) - len(trimmed))
            except Exception:
                trimmed = list(rows or [])
                dropped = 0
            csv_dir = os.path.dirname(csv_path)
            if csv_dir:
                os.makedirs(csv_dir, exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as output:
                writer = csv.writer(output)
                writer.writerow(header)
                expect_n = max(len(header) - 1, 0)
                for time_val, values in trimmed:
                    aligned = list(values or [])[:expect_n]
                    if len(aligned) < expect_n:
                        aligned.extend([float("nan")] * (expect_n - len(aligned)))
                    writer.writerow(
                        [f"{float(time_val):.4f}"]
                        + [f"{value:.7f}" for value in aligned]
                    )
            msg = f"[Collector][export_run_to_csv] 导出完成: {csv_path} ({len(trimmed)} 行)"
            if dropped:
                msg += f"，已去掉开头空测点 {dropped} 行"
            print(msg)'''
    if "trim_leading_all_nan_samples" in t:
        print("collector already trimmed")
        return
    if old not in t:
        raise SystemExit("collector export block missing")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("collector patched")


def patch_tests() -> None:
    p = Path(r"E:\solarautotestnewui\tests\test_dewetron_recording.py")
    t = p.read_text(encoding="utf-8")
    if "trim_leading_all_nan_samples" in t:
        print("tests already have trim")
        return
    t = t.replace(
        "from utils.dewetron_recording import (\n"
        "    apply_dewetron_recording_boundaries,\n"
        "    is_measure_wait_row,\n"
        "    resolve_dewetron_save_paths,\n"
        ")\n",
        "from utils.dewetron_recording import (\n"
        "    apply_dewetron_recording_boundaries,\n"
        "    is_measure_wait_row,\n"
        "    resolve_dewetron_save_paths,\n"
        "    trim_leading_all_nan_samples,\n"
        ")\n",
        1,
    )
    t += '''

def test_trim_leading_all_nan_and_rebase_time():
    rows = [
        (0.0, [float("nan"), float("nan")]),
        (0.1, [float("nan"), float("nan")]),
        (0.409, [230.1, 0.16]),
        (0.509, [230.2, 0.17]),
    ]
    got = trim_leading_all_nan_samples(rows, rebase_time=True)
    assert len(got) == 2
    assert abs(got[0][0] - 0.0) < 1e-9
    assert abs(got[1][0] - 0.1) < 1e-9
    assert got[0][1][0] == 230.1


def test_trim_keeps_partial_nan_rows():
    rows = [
        (0.0, [230.0, float("nan")]),
        (0.1, [231.0, 1.0]),
    ]
    got = trim_leading_all_nan_samples(rows, rebase_time=True)
    assert len(got) == 2
    assert got[0][1][0] == 230.0
'''
    p.write_text(t, encoding="utf-8")
    print("tests patched")


if __name__ == "__main__":
    patch_recording()
    patch_collector()
    patch_tests()
