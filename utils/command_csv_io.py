# -*- coding: utf-8 -*-
"""Write AutoTest command CSV lists; always create parent dirs first."""

from __future__ import annotations

import csv
import os
from typing import Iterable, Sequence


def ensure_command_save_dirs(base_path: str = "./command_save_files") -> str:
    """Create command_data / dewetron_data under base_path. Return absolute base."""
    base = os.path.abspath(base_path or "./command_save_files")
    for sub in ("command_data", "dewetron_data"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)
    return base


def write_command_csv(file_path: str, rows: Iterable[Sequence]) -> str:
    """Write rows to CSV; create parent directory if missing. Return abs path."""
    path = os.path.abspath(file_path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w+", newline="", encoding="utf-8") as out:
        writer = csv.writer(out, dialect="excel")
        for row in rows:
            writer.writerow(row)
    return path
