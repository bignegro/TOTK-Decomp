import csv
import os

import ida_auto
import idaapi
import idautils
import idc


OUT_DIR = r"G:\repos\TOTK-Decomp\orig"
FUNC_CSV = os.path.join(OUT_DIR, "ida_functions.csv")
SEGS_TXT = os.path.join(OUT_DIR, "ida_segments.txt")
STRINGS_TXT = os.path.join(OUT_DIR, "ida_strings.txt")


def dump_segments():
    with open(SEGS_TXT, "w", encoding="utf-8") as f:
        f.write("Segments:\n")
        for seg_ea in idautils.Segments():
            seg = idaapi.getseg(seg_ea)
            if not seg:
                continue
            name = idaapi.get_segm_name(seg)
            f.write(f"{name} {seg.start_ea:016X} {seg.end_ea:016X}\n")


def dump_functions():
    with open(FUNC_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["start_ea", "end_ea", "size", "name"])
        for ea in idautils.Functions():
            end_ea = idc.get_func_attr(ea, idc.FUNCATTR_END)
            name = idc.get_func_name(ea)
            size = end_ea - ea if end_ea != idc.BADADDR else 0
            writer.writerow([f"0x{ea:016X}", f"0x{end_ea:016X}", size, name])


def dump_strings():
    with open(STRINGS_TXT, "w", encoding="utf-8") as f:
        for s in idautils.Strings():
            try:
                f.write(f"0x{s.ea:016X} {str(s)}\n")
            except Exception:
                continue


def main():
    ida_auto.auto_wait()
    os.makedirs(OUT_DIR, exist_ok=True)
    dump_segments()
    dump_functions()
    dump_strings()
    idaapi.qexit(0)


if __name__ == "__main__":
    main()
