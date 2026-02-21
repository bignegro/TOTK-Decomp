#!/usr/bin/env python3
"""
Extract and decompress NSO segments into a flat binary image.

Outputs:
  data/main.uncompressed.bin  (memory layout image: text + padding + rodata + padding + data)
  data/segments/text.bin
  data/segments/rodata.bin
  data/segments/data.bin
"""

from __future__ import annotations

import argparse
from pathlib import Path


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def lz4_decompress(data: bytes, expected_size: int) -> bytes:
    try:
        import lz4.block as lz4_block
    except Exception as exc:
        raise SystemExit("lz4 module required. Run: python -m pip install lz4") from exc
    return lz4_block.decompress(data, uncompressed_size=expected_size)


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


def extract_section(data: bytes, file_offset: int, file_size: int, mem_size: int, flag_bit: int, flags: int) -> bytes:
    blob = data[file_offset : file_offset + (file_size or mem_size)]
    is_compressed = (flags & flag_bit) != 0 or (file_size and file_size != mem_size)
    if is_compressed:
        return lz4_decompress(blob, mem_size)
    return blob[:mem_size]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract NSO sections to a flat binary image.")
    parser.add_argument("nso", type=Path, help="Path to main.nso")
    parser.add_argument("--out", type=Path, default=Path("data/main.uncompressed.bin"))
    args = parser.parse_args()

    nso_path = args.nso
    data = nso_path.read_bytes()
    hdr = parse_nso_header(data)

    text = extract_section(
        data,
        hdr["text_file_offset"],
        hdr["text_file_size"],
        hdr["text_size"],
        0x1,
        hdr["flags"],
    )
    ro = extract_section(
        data,
        hdr["ro_file_offset"],
        hdr["ro_file_size"],
        hdr["ro_size"],
        0x2,
        hdr["flags"],
    )
    dat = extract_section(
        data,
        hdr["data_file_offset"],
        hdr["data_file_size"],
        hdr["data_size"],
        0x4,
        hdr["flags"],
    )

    out = bytearray(hdr["data_mem_offset"] + hdr["data_size"])
    out[hdr["text_mem_offset"] : hdr["text_mem_offset"] + len(text)] = text
    out[hdr["ro_mem_offset"] : hdr["ro_mem_offset"] + len(ro)] = ro
    out[hdr["data_mem_offset"] : hdr["data_mem_offset"] + len(dat)] = dat

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(out)

    seg_dir = Path("data/segments")
    seg_dir.mkdir(parents=True, exist_ok=True)
    (seg_dir / "text.bin").write_bytes(text)
    (seg_dir / "rodata.bin").write_bytes(ro)
    (seg_dir / "data.bin").write_bytes(dat)

    print(f"Wrote {args.out}")
    print(f"Segments: text={len(text)} rodata={len(ro)} data={len(dat)} bss={hdr['bss_size']}")


if __name__ == "__main__":
    main()
