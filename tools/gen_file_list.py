#!/usr/bin/env python3
"""
Generate a minimal file_list.yml from IDA exports.

This mirrors the style used by some decomp projects, but keeps things simple:
- One bucket: UNKNOWN
- One section: .text
- Every function from ida_functions.csv becomes a NotDecompiled entry

Usage:
  python tools/gen_file_list.py --ida-csv orig/ida_functions.csv --ida-segments orig/ida_segments.txt --out data/file_list.yml
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


def is_guess_name(name: str) -> bool:
    return name.startswith("sub_") or name.startswith("nullsub_") or name.startswith("unk_")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate file_list.yml from IDA CSV exports.")
    parser.add_argument("--ida-csv", default="orig/ida_functions.csv", help="IDA functions CSV.")
    parser.add_argument("--ida-segments", default="orig/ida_segments.txt", help="IDA segments text file.")
    parser.add_argument("--out", default="data/file_list.yml", help="Output YAML path.")
    parser.add_argument("--sort", action="store_true", help="Sort by start address (uses extra memory).")
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
    count = 0
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.sort:
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
                name = row.get("name") or f"sub_{start_ea:08X}"
                entries.append((start_ea, size, name))

        entries.sort(key=lambda e: e[0])
        with out_path.open("w", encoding="utf-8") as out:
            out.write("UNKNOWN:\n")
            out.write("  '.text':\n")
            for start_ea, size, name in entries:
                offset = start_ea - text_start
                out.write(f"  - offset: 0x{offset:06X}\n")
                out.write(f"    size: {size}\n")
                out.write(f"    label: {name}\n")
                out.write("    status: NotDecompiled\n")
                if is_guess_name(name):
                    out.write("    guess: true\n")
                count += 1
    else:
        with out_path.open("w", encoding="utf-8") as out, ida_csv.open("r", encoding="utf-8") as f:
            out.write("UNKNOWN:\n")
            out.write("  '.text':\n")
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
                name = row.get("name") or f"sub_{start_ea:08X}"
                offset = start_ea - text_start
                out.write(f"  - offset: 0x{offset:06X}\n")
                out.write(f"    size: {size}\n")
                out.write(f"    label: {name}\n")
                out.write("    status: NotDecompiled\n")
                if is_guess_name(name):
                    out.write("    guess: true\n")
                count += 1

    print(f"Wrote {out_path} with {count} entries.")


if __name__ == "__main__":
    main()
