#!/usr/bin/env python3
"""
Minimal progress summary for data/file_list.yml.

This intentionally avoids YAML dependencies and does a fast line scan.
It expects the standard format:
  - offset: ...
    size: ...
    label: ...
    status: ...
    guess: true (optional)
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict


def parse_file_list(path: Path):
    size = None
    label = None
    status = None

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("size:"):
                try:
                    size = int(line.split()[-1])
                except Exception:
                    size = None
            elif line.startswith("label:"):
                label = line.split(" ", 1)[-1].strip()
            elif line.startswith("status:"):
                status = line.split()[-1]
                if size is not None:
                    yield (label or ""), status, size
                size = None
                label = None
                status = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Print progress from data/file_list.yml")
    parser.add_argument("--file", default="data/file_list.yml", help="Path to file_list.yml")
    parser.add_argument("--csv", action="store_true", help="Print CSV line instead of human-readable output")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"Missing file list: {path}")

    counts: DefaultDict[str, int] = defaultdict(int)
    sizes: DefaultDict[str, int] = defaultdict(int)
    total_count = 0
    total_size = 0

    for _label, status, size in parse_file_list(path):
        total_count += 1
        total_size += size
        counts[status] += 1
        sizes[status] += size

    if total_count == 0:
        print("No entries found.")
        return

    if args.csv:
        # version, total_count, total_size, matching_count, matching_size, eq_count, eq_size, nm_count, nm_size
        def get(label: str):
            return counts.get(label, 0), sizes.get(label, 0)

        m_cnt, m_sz = get("Matching")
        eq_cnt, eq_sz = get("NonMatchingMinor")
        nm_cnt, nm_sz = get("NonMatchingMajor")
        print(f"1,{total_count},{total_size},{m_cnt},{m_sz},{eq_cnt},{eq_sz},{nm_cnt},{nm_sz}")
        return

    def fmt_pct(count: int, size: int):
        pct = (count / total_count) * 100.0
        spct = (size / total_size) * 100.0
        return f"{pct:.3f}% | size: {spct:.3f}%"

    print()
    print(f"{total_count:>7d} functions (size: ~{total_size} bytes)")
    print()
    decomp_count = (
        counts.get("Matching", 0)
        + counts.get("NonMatchingMinor", 0)
        + counts.get("NonMatchingMajor", 0)
    )
    decomp_size = (
        sizes.get("Matching", 0)
        + sizes.get("NonMatchingMinor", 0)
        + sizes.get("NonMatchingMajor", 0)
    )

    print(f"{decomp_count:>7d} decompiled ({fmt_pct(decomp_count, decomp_size)})")
    print(f"{counts.get('Matching', 0):>7d} matching ({fmt_pct(counts.get('Matching', 0), sizes.get('Matching', 0))})")
    print(
        f\"{counts.get('NonMatchingMinor', 0):>7d} non-matching (minor) ({fmt_pct(counts.get('NonMatchingMinor', 0), sizes.get('NonMatchingMinor', 0))})\"
    )
    print(
        f\"{counts.get('NonMatchingMajor', 0):>7d} non-matching (major) ({fmt_pct(counts.get('NonMatchingMajor', 0), sizes.get('NonMatchingMajor', 0))})\"
    )
    print()


if __name__ == "__main__":
    main()
