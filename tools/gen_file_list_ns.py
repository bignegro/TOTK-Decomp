#!/usr/bin/env python3
"""
Generate a file_list.yml by grouping functions into object-like buckets.

Heuristic:
- Demangle C++ symbols (if cxxfilt is available)
- Use namespace/class names to derive a file path (e.g. ksys::act::Actor -> KingSystem/act/Actor.o)
- Unknown/ungrouped symbols go into the "UNKNOWN" bucket

This is a best-effort starting point that mirrors Odyssey-style file lists,
but you should expect to move/rename files as you learn more about the binary.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_ROOT_MAP = {
    "ksys": "KingSystem",
    "gdt": "Game",
    "uking": "Game",
    "al": "al",
    "sead": "sead",
    "nn": "nn",
    "agl": "agl",
    "oe": "nn/oe",
    "gfx": "gfx",
    "vfx": "vfx",
}


def parse_text_segment(seg_path: Path) -> Tuple[int, int]:
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


def _demangle_with_cxxfilt(names: Iterable[str]) -> Optional[Dict[str, str]]:
    try:
        import cxxfilt
        from cxxfilt import LibraryNotFound  # type: ignore
    except Exception:
        return None

    out: Dict[str, str] = {}
    tested = False
    for name in names:
        try:
            out[name] = cxxfilt.demangle(name, external_only=False)
            tested = True
        except Exception as exc:
            if isinstance(exc, LibraryNotFound):
                return None
            out[name] = name
            tested = True
    if not tested:
        return None
    return out


def _demangle_with_llvm_cxxfilt(names: Iterable[str]) -> Optional[Dict[str, str]]:
    tool = shutil.which("llvm-cxxfilt") or shutil.which("c++filt")
    if not tool:
        llvm_default = Path(r"C:\Program Files\LLVM\bin\llvm-cxxfilt.exe")
        if llvm_default.is_file():
            tool = str(llvm_default)
    if not tool:
        llvm_alt = Path(r"C:\Program Files\LLVM\bin\c++filt.exe")
        if llvm_alt.is_file():
            tool = str(llvm_alt)
    if not tool:
        return None

    unique = list(dict.fromkeys(names))
    if not unique:
        return {}

    proc = subprocess.run(
        [tool],
        input=("\n".join(unique) + "\n").encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    output = proc.stdout.decode("utf-8", errors="replace").splitlines()
    if len(output) != len(unique):
        return None

    return dict(zip(unique, output))


def demangle_map(names: Iterable[str]) -> Dict[str, str]:
    names = list(names)
    # Prefer cxxfilt when available (fast), fall back to llvm-cxxfilt
    mapping = _demangle_with_cxxfilt(names)
    if mapping is not None:
        return mapping
    mapping = _demangle_with_llvm_cxxfilt(names)
    if mapping is not None:
        return mapping
    return {name: name for name in names}


def strip_templates(text: str) -> str:
    out = []
    depth = 0
    for ch in text:
        if ch == "<":
            depth += 1
            continue
        if ch == ">":
            depth = max(0, depth - 1)
            continue
        if depth == 0:
            out.append(ch)
    return "".join(out)


def clean_part(part: str) -> str:
    part = strip_templates(part)
    part = part.replace("~", "")
    part = part.replace("operator ", "operator_")
    part = part.replace("operator", "operator_")
    part = part.replace(" ", "")
    part = re.sub(r"[^A-Za-z0-9_]", "_", part)
    part = re.sub(r"_+", "_", part)
    return part.strip("_") or "Anon"


def is_probably_namespace(part: str) -> bool:
    if not part:
        return True
    if part[0].islower():
        return True
    if part in {"detail", "internal", "impl"}:
        return True
    return False


def load_root_map(path: Optional[Path]) -> Tuple[Dict[str, str], str]:
    root_map = dict(DEFAULT_ROOT_MAP)
    fallback_root = "UNKNOWN"
    if not path or not path.exists():
        return root_map, fallback_root
    try:
        import yaml
    except Exception:
        return root_map, fallback_root

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    roots = data.get("roots", {})
    for key, value in roots.items():
        root_map[str(key)] = str(value)
    fallback_root = str(data.get("fallback_root", fallback_root))
    return root_map, fallback_root


def load_status_map(path: Optional[Path]) -> Dict[str, str]:
    if not path or not path.exists():
        return {}
    try:
        import yaml
    except Exception:
        return {}

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    status_map: Dict[str, str] = {}
    if not isinstance(data, dict):
        return status_map
    for _, sections in data.items():
        if not isinstance(sections, dict):
            continue
        for _, entries in sections.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                label = entry.get("label")
                status = entry.get("status")
                if not status:
                    continue
                if isinstance(label, list):
                    for name in label:
                        if isinstance(name, str):
                            status_map[name] = status
                elif isinstance(label, str):
                    status_map[label] = status
    return status_map


def derive_file_key(
    mangled_name: str,
    demangled: Optional[str],
    root_map: Dict[str, str],
    fallback_root: str,
) -> str:
    name = demangled or mangled_name
    signature = name.split("(", 1)[0]
    if "::" not in signature:
        return fallback_root
    parts = [clean_part(p) for p in signature.split("::") if p]
    if len(parts) < 2:
        return fallback_root

    root = parts[0]
    root_dir = root_map.get(root)
    if not root_dir:
        return fallback_root

    if len(parts) >= 3:
        container = parts[-2]
        func = parts[-1]
        if is_probably_namespace(container):
            file_base = container
            ns_parts = parts[1:-1]  # drop root + function
        else:
            file_base = container
            ns_parts = parts[1:-2]
    else:
        file_base = parts[-1]
        ns_parts = []

    if not file_base:
        return fallback_root

    path_parts = [root_dir]
    for part in ns_parts:
        if part and part != file_base:
            path_parts.append(part)
    path_parts.append(f"{file_base}.o")
    return "/".join(path_parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a namespaced file_list.yml from IDA CSV exports.")
    parser.add_argument("--ida-csv", default="orig/ida_functions.csv", help="IDA functions CSV.")
    parser.add_argument("--ida-segments", default="orig/ida_segments.txt", help="IDA segments text file.")
    parser.add_argument("--out", default="data/file_list.yml", help="Output YAML path.")
    parser.add_argument("--roots", default="config/file_map.yml", help="Root namespace mapping (YAML).")
    parser.add_argument("--preserve", default="data/file_list.yml", help="Existing file_list.yml to preserve statuses.")
    parser.add_argument("--sort", action="store_true", help="Sort by start address (global).")
    args = parser.parse_args()

    ida_csv = Path(args.ida_csv)
    ida_segments = Path(args.ida_segments)
    out_path = Path(args.out)
    roots_path = Path(args.roots) if args.roots else None
    preserve_path = Path(args.preserve) if args.preserve else None

    if not ida_csv.exists():
        raise SystemExit(f"Missing IDA CSV: {ida_csv}")
    if not ida_segments.exists():
        raise SystemExit(f"Missing IDA segments: {ida_segments}")

    text_start, text_end = parse_text_segment(ida_segments)
    root_map, fallback_root = load_root_map(roots_path)
    status_map = load_status_map(preserve_path)

    entries: List[Tuple[int, int, str]] = []
    mangled_names: List[str] = []
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
            if name.startswith("_Z"):
                mangled_names.append(name)

    if args.sort:
        entries.sort(key=lambda e: e[0])

    demangled = demangle_map(mangled_names)

    grouped: Dict[str, List[Tuple[int, int, str]]] = {}
    for start_ea, size, name in entries:
        file_key = derive_file_key(name, demangled.get(name), root_map, fallback_root)
        grouped.setdefault(file_key, []).append((start_ea, size, name))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as out:
        def write_group(key: str, items: List[Tuple[int, int, str]]) -> None:
            out.write(f"{key}:\n")
            out.write("  '.text':\n")
            by_key: Dict[Tuple[int, int], Dict[str, Any]] = {}
            for start_ea, size, name in sorted(items, key=lambda e: e[0]):
                offset = start_ea - text_start
                entry_key = (offset, size)
                entry = by_key.get(entry_key)
                if entry is None:
                    entry = {
                        "offset": offset,
                        "size": size,
                        "labels": [name],
                        "guess": is_guess_name(name),
                        "status": status_map.get(name, "NotDecompiled"),
                    }
                    by_key[entry_key] = entry
                else:
                    entry["labels"].append(name)
                    entry["guess"] = entry["guess"] and is_guess_name(name)
            for entry in by_key.values():
                out.write(f"  - offset: 0x{entry['offset']:06X}\n")
                out.write(f"    size: {entry['size']}\n")
                labels = entry["labels"]
                if len(labels) == 1:
                    out.write(f"    label: {labels[0]}\n")
                else:
                    out.write("    label:\n")
                    for label in labels:
                        out.write(f"    - {label}\n")
                out.write(f"    status: {entry['status']}\n")
                if entry["guess"]:
                    out.write("    guess: true\n")

        # UNKNOWN (fallback) first, then alphabetical
        if fallback_root in grouped:
            write_group(fallback_root, grouped.pop(fallback_root))
        for key in sorted(grouped.keys()):
            write_group(key, grouped[key])

    print(f"Wrote {out_path} with {len(entries)} entries across {len(grouped) + 1} groups.")


if __name__ == "__main__":
    main()
