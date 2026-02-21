#!/usr/bin/env python3
"""
Print key fields from an NSO header so you can set up IDA/dbg with the correct base and entrypoint.

Usage:
  python tools/nso-info.py orig/main.nso --load-base 0x710000000

Entry point (per Switchbrew's Homebrew ABI) is always `binary_ptr + 0`, so once you've
chosen a load base for the file (e.g., `0x710000000` for Tears of the Kingdom), that value
is the address you should type into IDA's "Manual load" dialog as the entrypoint.
The script prints section offsets so you can verify the load layout while importing.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def read_utf8(data: bytes) -> str:
    try:
        return data.decode("utf-8").rstrip("\x00")
    except UnicodeDecodeError:
        return data.hex()


def fmt_hex(value: int, width: int = 16) -> str:
    return f"0x{value:0{width}x}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump NSO header statistics for IDA/loader setup.")
    parser.add_argument("nso", type=Path, help="Path to the NSO file (e.g., orig/main.nso).")
    parser.add_argument(
        "--load-base",
        type=lambda v: int(v, 0),
        default=0,
        help="Base address the loader will map the binary to (entrypoint = base + 0). Defaults to 0.",
    )
    args = parser.parse_args()

    data = args.nso.read_bytes()
    if len(data) < 0x90:
        raise SystemExit("NSO is too small to contain a complete header.")

    if data[:4] != b"NSO0":
        raise SystemExit("File does not start with NSO0 magic.")

    header = {
        "version": read_u32(data, 0x04),
        "flags": read_u32(data, 0x0C),
        "text_file_offset": read_u32(data, 0x10),
        "text_memory_offset": read_u32(data, 0x14),
        "text_size": read_u32(data, 0x18),
        "module_name_offset": read_u32(data, 0x1C),
        "ro_file_offset": read_u32(data, 0x20),
        "ro_memory_offset": read_u32(data, 0x24),
        "ro_size": read_u32(data, 0x28),
        "module_name_size": read_u32(data, 0x2C),
        "data_file_offset": read_u32(data, 0x30),
        "data_memory_offset": read_u32(data, 0x34),
        "data_size": read_u32(data, 0x38),
        "bss_size": read_u32(data, 0x3C),
        "text_file_size": read_u32(data, 0x60),
        "ro_file_size": read_u32(data, 0x64),
        "data_file_size": read_u32(data, 0x68),
    }

    module_id = data[0x40 : 0x60]
    module_name_bytes = b""
    if header["module_name_offset"] and header["module_name_size"]:
        start = header["module_name_offset"]
        end = start + header["module_name_size"]
        module_name_bytes = data[start:end]

    print(f"NSO: {args.nso}")
    print(f"Version: {header['version']}")
    print(f"Flags: {fmt_hex(header['flags'], width=8)}")
    print()
    print("Section offsets/sizes (file vs. in-memory):")
    print(f"  .text   file@{fmt_hex(header['text_file_offset'], 8)} size={header['text_size']} mem offset={fmt_hex(header['text_memory_offset'], 8)}")
    print(f"  .rodata file@{fmt_hex(header['ro_file_offset'], 8)} size={header['ro_size']} mem offset={fmt_hex(header['ro_memory_offset'], 8)}")
    print(f"  .data   file@{fmt_hex(header['data_file_offset'], 8)} size={header['data_size']} mem offset={fmt_hex(header['data_memory_offset'], 8)}")
    print(f"  .bss    size={header['bss_size']} (zero-filled in memory)")
    print()
    print("Compressed blob sizes (if sections are LZ4-compressed):")
    print(f"  .text: {header['text_file_size']} bytes")
    print(f"  .rodata: {header['ro_file_size']} bytes")
    print(f"  .data: {header['data_file_size']} bytes")
    print()
    module_name = read_utf8(module_name_bytes) if module_name_bytes else ""
    print(f"Module name: {module_name or '<unknown>'}")
    print(f"Module ID: {module_id.hex()}")
    print()
    if args.load_base:
        entry = args.load_base
        print(f"Entry point (binary_ptr + 0): {fmt_hex(entry)}")
        print(f"Use that address for IDA’s manual load entry/analysis base.")
    else:
        print("Entry point = binary_ptr + 0. Provide --load-base if you need an absolute address.")
    print("Per Switchbrew's Homebrew ABI, the very first instruction is the entrypoint (a branch).")


if __name__ == "__main__":
    main()
