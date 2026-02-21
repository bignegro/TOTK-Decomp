#!/usr/bin/env python3
"""
Convert an NSO to a minimal ELF (PT_LOAD segments + section headers).
This is a fallback when nx2elf is unavailable.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def lz4_decompress(data: bytes, expected_size: int) -> bytes:
    import lz4.block as lz4_block
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


def align(value: int, align_to: int) -> int:
    return (value + (align_to - 1)) & ~(align_to - 1)


def build_elf(text: bytes, ro: bytes, data: bytes, hdr: dict, out_path: Path) -> None:
    # ELF64 header constants
    EI_NIDENT = 16
    ET_DYN = 3
    EM_AARCH64 = 183
    EV_CURRENT = 1

    # Program headers
    phnum = 3
    phentsize = 56
    ehsize = 64
    phoff = ehsize
    shentsize = 64

    # Offsets for segment data
    text_off = align(phoff + phnum * phentsize, 0x1000)
    ro_off = align(text_off + len(text), 0x1000)
    data_off = align(ro_off + len(ro), 0x1000)

    # Section header string table
    shstr = (
        b"\x00.text\x00.rodata\x00.data\x00.bss\x00.dynsym\x00.dynstr\x00.rela.dyn\x00.shstrtab\x00"
    )
    shstr_off = align(data_off + len(data), 0x1000)

    # Section headers: null + .text + .rodata + .data + .bss + .dynsym + .dynstr + .rela.dyn + .shstrtab
    shnum = 9
    shoff = align(shstr_off + len(shstr), 0x10)

    # ELF header
    e_ident = bytearray(EI_NIDENT)
    e_ident[0:4] = b"\x7fELF"
    e_ident[4] = 2  # 64-bit
    e_ident[5] = 1  # little-endian
    e_ident[6] = 1  # version
    e_ident[7] = 0  # System V

    e_type = ET_DYN
    e_machine = EM_AARCH64
    e_version = EV_CURRENT
    e_entry = 0
    e_flags = 0
    e_shstrndx = 8

    elf_header = struct.pack(
        "<16sHHIQQQIHHHHHH",
        bytes(e_ident),
        e_type,
        e_machine,
        e_version,
        e_entry,
        phoff,
        shoff,
        e_flags,
        ehsize,
        phentsize,
        phnum,
        shentsize,
        shnum,
        e_shstrndx,
    )

    # Program headers (PT_LOAD)
    PT_LOAD = 1
    PF_X = 1
    PF_W = 2
    PF_R = 4
    p_align = 0x1000

    ph_text = struct.pack(
        "<IIQQQQQQ",
        PT_LOAD,
        PF_R | PF_X,
        text_off,
        hdr["text_mem_offset"],
        hdr["text_mem_offset"],
        len(text),
        len(text),
        p_align,
    )
    ph_ro = struct.pack(
        "<IIQQQQQQ",
        PT_LOAD,
        PF_R,
        ro_off,
        hdr["ro_mem_offset"],
        hdr["ro_mem_offset"],
        len(ro),
        len(ro),
        p_align,
    )
    ph_data = struct.pack(
        "<IIQQQQQQ",
        PT_LOAD,
        PF_R | PF_W,
        data_off,
        hdr["data_mem_offset"],
        hdr["data_mem_offset"],
        len(data),
        len(data) + hdr["bss_size"],
        p_align,
    )

    # Section headers
    def sh(name_off, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link=0, sh_info=0, sh_addralign=0x10, sh_entsize=0):
        return struct.pack(
            "<IIQQQQIIQQ",
            name_off,
            sh_type,
            sh_flags,
            sh_addr,
            sh_offset,
            sh_size,
            sh_link,
            sh_info,
            sh_addralign,
            sh_entsize,
        )

    # name offsets in shstr
    off_text = shstr.find(b".text")
    off_ro = shstr.find(b".rodata")
    off_data = shstr.find(b".data")
    off_bss = shstr.find(b".bss")
    off_dynsym = shstr.find(b".dynsym")
    off_dynstr = shstr.find(b".dynstr")
    off_rela = shstr.find(b".rela.dyn")
    off_shstr = shstr.find(b".shstrtab")

    SHT_NULL = 0
    SHT_PROGBITS = 1
    SHT_STRTAB = 3
    SHT_RELA = 4
    SHT_DYNSYM = 11
    SHT_NOBITS = 8
    SHF_ALLOC = 0x2
    SHF_EXECINSTR = 0x4
    SHF_WRITE = 0x1

    sh_null = sh(0, SHT_NULL, 0, 0, 0, 0)
    sh_text = sh(off_text, SHT_PROGBITS, SHF_ALLOC | SHF_EXECINSTR, hdr["text_mem_offset"], text_off, len(text))
    sh_ro = sh(off_ro, SHT_PROGBITS, SHF_ALLOC, hdr["ro_mem_offset"], ro_off, len(ro))
    sh_data = sh(off_data, SHT_PROGBITS, SHF_ALLOC | SHF_WRITE, hdr["data_mem_offset"], data_off, len(data))
    sh_bss = sh(off_bss, SHT_NOBITS, SHF_ALLOC | SHF_WRITE, hdr["data_mem_offset"] + len(data), data_off + len(data), hdr["bss_size"])
    # Minimal dynamic sections (empty) so viking can resolve .rela.dyn
    sh_dynsym = sh(off_dynsym, SHT_DYNSYM, SHF_ALLOC, 0, 0, 0, sh_link=6, sh_info=0, sh_addralign=8, sh_entsize=24)
    sh_dynstr = sh(off_dynstr, SHT_STRTAB, 0, 0, 0, 0, sh_addralign=1)
    sh_rela = sh(off_rela, SHT_RELA, 0, 0, 0, 0, sh_link=5, sh_info=0, sh_addralign=8, sh_entsize=24)
    sh_shstr = sh(off_shstr, SHT_PROGBITS, 0, 0, shstr_off, len(shstr))

    # Build file
    out = bytearray()
    out += elf_header
    out += ph_text + ph_ro + ph_data
    out += b"\x00" * (text_off - len(out))
    out += text
    out += b"\x00" * (ro_off - len(out))
    out += ro
    out += b"\x00" * (data_off - len(out))
    out += data
    out += b"\x00" * (shstr_off - len(out))
    out += shstr
    out += b"\x00" * (shoff - len(out))
    out += sh_null + sh_text + sh_ro + sh_data + sh_bss + sh_dynsym + sh_dynstr + sh_rela + sh_shstr

    out_path.write_bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert NSO to a minimal ELF (fallback).")
    parser.add_argument("nso", type=Path)
    parser.add_argument("--out", type=Path, default=Path("data/main.elf"))
    args = parser.parse_args()

    data = args.nso.read_bytes()
    hdr = parse_nso_header(data)

    def extract_section(file_offset, file_size, mem_size, flag_bit):
        blob = data[file_offset : file_offset + (file_size or mem_size)]
        is_compressed = (hdr["flags"] & flag_bit) != 0 or (file_size and file_size != mem_size)
        if is_compressed:
            return lz4_decompress(blob, mem_size)
        return blob[:mem_size]

    text = extract_section(hdr["text_file_offset"], hdr["text_file_size"], hdr["text_size"], 0x1)
    ro = extract_section(hdr["ro_file_offset"], hdr["ro_file_size"], hdr["ro_size"], 0x2)
    dat = extract_section(hdr["data_file_offset"], hdr["data_file_size"], hdr["data_size"], 0x4)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    build_elf(text, ro, dat, hdr, args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
