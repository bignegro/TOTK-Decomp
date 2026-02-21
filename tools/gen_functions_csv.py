#!/usr/bin/env python3
"""
Generate a viking-compatible functions CSV from IDA exports.

Format required by tools/check (viking):
Address,Quality,Size,Name
0x0000007100000030,U,000308,sub_7100000030
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_text_segment(seg_path: Path) -> tuple[int, int]:
    text_start = None
    text_end = None
    for line in seg_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line.startswith(".text "):
            continue
        parts = line.split()
        if len(parts) >= 3:
            text_start = int(parts[1], 16)
            text_end = int(parts[2], 16)
            break
    if text_start is None or text_end is None:
        raise SystemExit("Could not find .text segment in ida_segments.txt")
    return text_start, text_end


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate functions.csv from IDA CSV exports.")
    parser.add_argument("--ida-csv", default="orig/ida_functions.csv", help="IDA functions CSV.")
    parser.add_argument("--ida-segments", default="orig/ida_segments.txt", help="IDA segments text file.")
    parser.add_argument("--out", default="data/functions.csv", help="Output CSV path.")
    parser.add_argument("--sort", action="store_true", help="Sort by start address.")
    args = parser.parse_args()

    ida_csv = Path(args.ida_csv)
    ida_segments = Path(args.ida_segments)
    out_path = Path(args.out)

    if not ida_csv.exists():
        raise SystemExit(f"Missing IDA CSV: {ida_csv}")
    if not ida_segments.exists():
        raise SystemExit(f"Missing IDA segments: {ida_segments}")

    text_start, text_end = parse_text_segment(ida_segments)
    entries = []

    with ida_csv.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                start_ea = int(row["start_ea"], 16)
                end_ea = int(row["end_ea"], 16)
            except Exception:
                continue
            if start_ea < text_start or start_ea >= text_end:
                continue
            if end_ea > text_end:
                end_ea = text_end
            size = end_ea - start_ea
            if size <= 0:
                continue
            name = row.get("name") or ""
            entries.append((start_ea, size, name))

    if args.sort:
        entries.sort(key=lambda e: e[0])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["Address", "Quality", "Size", "Name"])
        for start_ea, size, name in entries:
            writer.writerow([f"0x{start_ea:016x}", "U", f"{size:06d}", name])

    print(f"Wrote {out_path} with {len(entries)} entries.")


if __name__ == "__main__":
    main()
