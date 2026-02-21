#!/usr/bin/env python3
"""
Create a target object from an NSO's .text and IDA function list.
Supports LZ4-compressed NSO segments (requires the `lz4` Python module).

This generates:
  build/target/main.text.bin
  build/target/main_target.S
  build/target/main_target.o
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import subprocess
from pathlib import Path


def lz4_decompress(data: bytes, expected_size: int) -> bytes:
    try:
        import lz4.block as lz4_block
    except Exception as exc:
        raise SystemExit("lz4 module required for compressed NSO segments. Run: python -m pip install lz4") from exc
    return lz4_block.decompress(data, uncompressed_size=expected_size)


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def parse_nso_header(data: bytes) -> dict:
    if data[:4] != b"NSO0":
        raise ValueError("Not an NSO0 file")
    return {
        "flags": read_u32(data, 0x0C),
        "text_file_offset": read_u32(data, 0x10),
        "text_mem_offset": read_u32(data, 0x14),
        "text_size": read_u32(data, 0x18),
        "ro_file_offset": read_u32(data, 0x20),
        "ro_mem_offset": read_u32(data, 0x24),
        "ro_size": read_u32(data, 0x28),
        "data_file_offset": read_u32(data, 0x30),
        "data_mem_offset": read_u32(data, 0x34),
        "data_size": read_u32(data, 0x38),
        "bss_size": read_u32(data, 0x3C),
        "text_file_size": read_u32(data, 0x60),
        "ro_file_size": read_u32(data, 0x64),
        "data_file_size": read_u32(data, 0x68),
    }


def is_valid_symbol(name: str) -> bool:
    return re.match(r"^[A-Za-z_.$][A-Za-z0-9_.$]*$", name) is not None


def main() -> None:
    default_nso = "data/main.nso" if Path("data/main.nso").exists() else "orig/main"
    parser = argparse.ArgumentParser(description="Generate target object from NSO + IDA symbols.")
    parser.add_argument("--nso", default=default_nso, help=f"Path to NSO (default: {default_nso}).")
    parser.add_argument("--ida-csv", default="orig/ida_functions.csv", help="IDA functions CSV.")
    parser.add_argument("--out-dir", default="build/target", help="Output directory.")
    parser.add_argument("--base-dir", default="build/base", help="Base output directory (zero-filled).")
    parser.add_argument("--load-base", default="0x7100000000", help="Load base address.")
    parser.add_argument("--text-limit", default=None, help="Optional max size of .text to include (e.g., 0x200000).")
    parser.add_argument("--clang", default=r"C:\Program Files\LLVM\bin\clang.exe", help="Path to clang.")
    args = parser.parse_args()

    nso_path = Path(args.nso)
    out_dir = Path(args.out_dir)
    base_dir = Path(args.base_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base_dir.mkdir(parents=True, exist_ok=True)

    data = nso_path.read_bytes()
    hdr = parse_nso_header(data)

    text_start = hdr["text_file_offset"]
    text_size = hdr["text_size"]
    if args.text_limit:
        limit = int(args.text_limit, 0)
        text_size = min(text_size, limit)
    text_file_size = hdr["text_file_size"] or hdr["text_size"]
    text_blob = data[text_start : text_start + text_file_size]
    if len(text_blob) < text_file_size:
        raise SystemExit("NSO text blob shorter than expected; file may be truncated.")

    is_text_compressed = (hdr["flags"] & 0x1) != 0 or text_file_size != hdr["text_size"]
    if is_text_compressed:
        full_text = lz4_decompress(text_blob, hdr["text_size"])
    else:
        full_text = text_blob[: hdr["text_size"]]
    text_bytes = full_text[:text_size]

    text_bin = out_dir / "main.text.bin"
    text_bin.write_bytes(text_bytes)
    zero_bin = base_dir / "main.text.zero.bin"
    zero_bin.write_bytes(bytes(text_size))

    text_base = int(args.load_base, 0) + hdr["text_mem_offset"]

    asm_path = out_dir / "main_target.S"
    base_asm_path = base_dir / "main_base.S"
    used = set()

    def write_asm(path: Path, bin_path: Path) -> None:
        with path.open("w", encoding="ascii") as f:
            f.write(".section .text\n")
            f.write(".align 4\n")
            f.write(".global __text_start\n")
            f.write("__text_start:\n")
            f.write(f'.incbin "{bin_path.as_posix()}"\n')
            f.write(".global __text_end\n")
            f.write(f".set __text_end, __text_start + 0x{text_size:X}\n\n")

            if Path(args.ida_csv).exists():
                with Path(args.ida_csv).open("r", encoding="utf-8") as csvf:
                    reader = csv.DictReader(csvf)
                    for row in reader:
                        name = row.get("name", "")
                        try:
                            start_ea = int(row["start_ea"], 16)
                            end_ea = int(row["end_ea"], 16)
                        except Exception:
                            continue
                        text_end = text_base + text_size
                        if start_ea < text_base or start_ea >= text_end:
                            continue
                        if end_ea > text_end:
                            end_ea = text_end
                        if not name or not is_valid_symbol(name):
                            continue
                        if name in used:
                            continue
                        used.add(name)
                        offset = start_ea - text_base
                        size = max(0, end_ea - start_ea)
                        if size == 0:
                            continue
                        f.write(f".global {name}\n")
                        f.write(f".type {name}, %function\n")
                        f.write(f".set {name}, __text_start + 0x{offset:X}\n")
                        f.write(f".size {name}, 0x{size:X}\n")
            else:
                f.write(".global __text_start_only\n")
                f.write(".set __text_start_only, __text_start\n")

    write_asm(asm_path, text_bin)
    write_asm(base_asm_path, zero_bin)

    # assemble into object
    obj_path = out_dir / "main_target.o"
    base_obj_path = base_dir / "main_base.o"
    clang = Path(args.clang)
    if not clang.exists():
        raise SystemExit(f"clang not found: {clang}")
    cmd = [
        str(clang),
        "--target=aarch64-none-elf",
        "-c",
        str(asm_path),
        "-o",
        str(obj_path),
    ]
    print(" ".join([f'\"{c}\"' if " " in c else c for c in cmd]))
    subprocess.run(cmd, check=True)

    base_cmd = [
        str(clang),
        "--target=aarch64-none-elf",
        "-c",
        str(base_asm_path),
        "-o",
        str(base_obj_path),
    ]
    print(" ".join([f'\"{c}\"' if " " in c else c for c in base_cmd]))
    subprocess.run(base_cmd, check=True)


if __name__ == "__main__":
    main()
