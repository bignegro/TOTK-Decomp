#!/usr/bin/env python3
"""
Update function status in:
  - data/functions.csv (viking)
  - data/file_list.yml (progress list)

Usage:
  python tools/set_status.py --name sub_7100000030 --status Wip
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import tempfile
import os


STATUS_TO_CODE = {
    "Matching": "O",
    "NonMatchingMinor": "m",
    "NonMatchingMajor": "M",
    "NotDecompiled": "U",
    "Wip": "W",
    "Library": "L",
}


def update_functions_csv(path: Path, name: str, status: str) -> bool:
    if status not in STATUS_TO_CODE:
        raise SystemExit(f"Unknown status: {status}")
    code = STATUS_TO_CODE[status]
    updated = False

    fd, tmp_path = tempfile.mkstemp(prefix="functions_", suffix=".csv", dir=path.parent)
    os.close(fd)
    tmp = Path(tmp_path)
    try:
        with path.open("r", encoding="utf-8", newline="") as inp, tmp.open(
            "w", encoding="utf-8", newline=""
        ) as out:
            reader = csv.reader(inp)
            writer = csv.writer(out)
            for row in reader:
                if row and row[0] == "Address":
                    writer.writerow(row)
                    continue
                if len(row) >= 4 and row[3] == name:
                    row[1] = code
                    updated = True
                writer.writerow(row)
        if updated:
            tmp.replace(path)
        else:
            tmp.unlink(missing_ok=True)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return updated


def update_file_list(path: Path, name: str, status: str) -> bool:
    updated = False
    pending = False
    fd, tmp_path = tempfile.mkstemp(prefix="file_list_", suffix=".yml", dir=path.parent)
    os.close(fd)
    tmp = Path(tmp_path)
    try:
        with path.open("r", encoding="utf-8", errors="replace") as inp, tmp.open(
            "w", encoding="utf-8", errors="replace"
        ) as out:
            for line in inp:
                stripped = line.strip()
                if stripped.startswith("label:"):
                    label = stripped.split(" ", 1)[-1].strip()
                    pending = (label == name)
                    out.write(line)
                    continue
                if pending and stripped.startswith("status:"):
                    indent = line.split("status:")[0]
                    out.write(f"{indent}status: {status}\n")
                    updated = True
                    pending = False
                    continue
                out.write(line)
        if updated:
            tmp.replace(path)
        else:
            tmp.unlink(missing_ok=True)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Update function status in tracking files.")
    parser.add_argument("--name", required=True, help="Function name")
    parser.add_argument(
        "--status",
        required=True,
        choices=list(STATUS_TO_CODE.keys()),
        help="New status",
    )
    parser.add_argument("--functions-csv", default="data/functions.csv")
    parser.add_argument("--file-list", default="data/file_list.yml")
    args = parser.parse_args()

    functions_csv = Path(args.functions_csv)
    file_list = Path(args.file_list)

    updated_csv = functions_csv.exists() and update_functions_csv(functions_csv, args.name, args.status)
    updated_yaml = file_list.exists() and update_file_list(file_list, args.name, args.status)

    if not updated_csv and not updated_yaml:
        print("No entries updated.")
        return

    if updated_csv:
        print("Updated data/functions.csv")
    if updated_yaml:
        print("Updated data/file_list.yml")


if __name__ == "__main__":
    main()
