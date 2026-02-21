import os

import ida_auto
import ida_bytes
import ida_funcs
import idaapi
import ida_ua
import idautils
import idc


ENTRY = 0x710000000
OUT_PATH = r"G:\repos\TOTK-Decomp\orig\ida_entry.txt"


def dump_segments(f):
    f.write("Segments:\n")
    for seg_ea in idautils.Segments():
        seg = idaapi.getseg(seg_ea)
        if not seg:
            continue
        name = idaapi.get_segm_name(seg)
        f.write(f"  {name}: {seg.start_ea:016X} - {seg.end_ea:016X}\n")
    f.write("\n")


def dump_disasm(f, start_ea, count=200):
    ea = start_ea
    dumped = 0
    while dumped < count and ea != idc.BADADDR:
        if not ida_bytes.is_code(ida_bytes.get_full_flags(ea)):
            ida_bytes.del_items(ea, 0)
            ida_ua.create_insn(ea)
            ida_auto.auto_wait()
        line = idc.GetDisasm(ea)
        if not line:
            line = idaapi.generate_disasm_line(ea, 0) or ""
        if not line:
            raw = ida_bytes.get_bytes(ea, 16) or b""
            line = f"db {raw.hex()}"
        f.write(f"{ea:016X}: {line}\n")
        dumped += 1
        ea = idaapi.next_head(ea, idc.BADADDR)


def main():
    ida_auto.auto_wait()

    entry_ea = ENTRY
    seg = idaapi.getseg(entry_ea)
    if seg is None:
        for seg_ea in idautils.Segments():
            seg_obj = idaapi.getseg(seg_ea)
            if seg_obj and idaapi.get_segm_name(seg_obj) == ".text":
                entry_ea = seg_obj.start_ea
                break

    if ida_funcs.get_func(entry_ea) is None:
        ida_funcs.add_func(entry_ea)
        ida_auto.auto_wait()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"Entry: {ENTRY:016X}\n\n")
        dump_segments(f)
        f.write(f"Requested entry: {ENTRY:016X}\n")
        f.write(f"Resolved entry:  {entry_ea:016X}\n")
        seg = idaapi.getseg(entry_ea)
        if seg:
            f.write(f"Entry segment: {idaapi.get_segm_name(seg)} "
                    f"{seg.start_ea:016X}-{seg.end_ea:016X}\n")
        else:
            f.write("Entry segment: <none>\n")
        raw = ida_bytes.get_bytes(entry_ea, 16)
        f.write(f"Entry bytes: {raw.hex() if raw else '<none>'}\n\n")
        f.write("Disassembly:\n")
        try:
            dump_disasm(f, entry_ea, 200)
        except Exception as exc:
            f.write(f"\n<error dumping disasm: {exc}>\n")

    idaapi.qexit(0)


if __name__ == "__main__":
    main()
