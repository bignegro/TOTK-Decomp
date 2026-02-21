#!/usr/bin/env python3
"""
Find likely shared core between BOTW (ref2) and TOTK by scanning TOTK strings
for BOTW namespace tokens.

This is a heuristic: it does not prove identical code, but helps identify
shared modules (sead/ksys/etc.) to prioritize for naming and grouping.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


DEFAULT_ALLOW = {
    "sead",
    "agl",
    "nn",
    "ksys",
    "gsys",
    "game",
    "engine",
    "hk",
    "gstd",
    "sarc",
    "al",
    "nvn",
}

DEFAULT_STOP = {
    "as",
    "ai",
    "ui",
    "act",
    "res",
    "Player",
    "Weapon",
    "Enemy",
    "Horse",
    "Effect",
    "Sound",
    "Screen",
    "Element",
    "Dragon",
    "Fade",
    "NPC",
    "Swarm",
    "Attention",
    "Terrain",
    "WorldMgr",
    "Graphics",
    "phys",
}

STRONG_PATTERNS = (
    "{mod}::",  # C++ namespace style
    "{mod}__",  # TOTK string convention (game__component__)
    "/{mod}/",  # path component
)


def load_botw_modules(path: Path, allow: set[str], stop: set[str], min_len: int) -> list[str]:
    counts = Counter()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0] == "Address":
                continue
            name = row[3].strip()
            if not name or "::" not in name:
                continue
            mod = name.split("::", 1)[0]
            if mod in stop:
                continue
            if len(mod) >= min_len or mod in allow:
                counts[mod] += 1
    return [m for m, _ in counts.most_common()]


def load_totk_strings(path: Path) -> list[str]:
    strings = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        strings.append(parts[1].strip())
    return strings


def compile_patterns(mod: str) -> list[re.Pattern[str]]:
    escaped = re.escape(mod)
    patterns = []
    for fmt in STRONG_PATTERNS:
        patterns.append(re.compile(fmt.format(mod=escaped)))
    return patterns


def main() -> None:
    parser = argparse.ArgumentParser(description="Find BOTW/TOTK shared module hints.")
    parser.add_argument("--botw-functions", default="ref2/data/uking_functions.csv")
    parser.add_argument("--totk-strings", default="orig/ida_strings.txt")
    parser.add_argument("--min-len", type=int, default=4)
    parser.add_argument("--min-strong", type=int, default=2, help="Minimum strong hits to report a module.")
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--write", default=None, help="Write results to a YAML-ish file.")
    args = parser.parse_args()

    botw_path = Path(args.botw_functions)
    totk_path = Path(args.totk_strings)
    if not botw_path.exists():
        raise SystemExit(f"Missing BOTW function list: {botw_path}")
    if not totk_path.exists():
        raise SystemExit(f"Missing TOTK strings: {totk_path}")

    modules = load_botw_modules(botw_path, DEFAULT_ALLOW, DEFAULT_STOP, args.min_len)
    totk_strings = load_totk_strings(totk_path)

    found: list[tuple[str, int, int, str]] = []
    for mod in modules:
        strong = 0
        weak = 0
        sample = None
        patterns = compile_patterns(mod)
        for s in totk_strings:
            if mod not in s:
                continue
            hit = False
            for pat in patterns:
                if pat.search(s):
                    strong += 1
                    hit = True
                    if sample is None:
                        sample = s
                    break
            if not hit:
                weak += 1
        if strong >= args.min_strong or (mod in DEFAULT_ALLOW and strong > 0):
            found.append((mod, strong, weak, sample or ""))

    found.sort(key=lambda x: (-x[1], -x[2], x[0]))

    print(f"BOTW modules checked: {len(modules)}")
    print(f"Modules found in TOTK strings: {len(found)}")
    print()
    for mod, strong, weak, sample in found[: args.top]:
        print(f"{mod}: strong={strong} weak={weak} (example: {sample})")

    if args.write:
        out_path = Path(args.write)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as out:
            out.write("shared_modules:\n")
            for mod, strong, weak, sample in found:
                out.write(f"  - name: {mod}\n")
                out.write(f"    strong: {strong}\n")
                out.write(f"    weak: {weak}\n")
                out.write(f"    example: {sample}\n")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
