#!/usr/bin/env python3
"""
Pick the next NotDecompiled function from data/functions.csv.

Usage:
  python tools/next_function.py --max-size 256
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Pick next function to decompile.")
    parser.add_argument("--functions-csv", default="data/functions.csv")
    parser.add_argument("--max-size", type=int, default=None, help="Only consider functions <= this size")
    args = parser.parse_args()

    path = Path(args.functions_csv)
    if not path.exists():
        raise SystemExit(f"Missing functions CSV: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == "Address":
                continue
            if len(row) < 4:
                continue
            addr, status, size_str, name = row[0], row[1], row[2], row[3]
            if status != "U":
                continue
            try:
                size = int(size_str)
            except Exception:
                continue
            if args.max_size is not None and size > args.max_size:
                continue
            print(f"{name} {addr} size={size}")
            return

    print("No matching functions found.")


if __name__ == "__main__":
    main()
