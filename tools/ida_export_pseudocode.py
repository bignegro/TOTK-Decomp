import idaapi
import ida_hexrays
import ida_name
import ida_funcs
import idc
from pathlib import Path


def get_arg(args, key, default=None):
    if key in args:
        idx = args.index(key)
        if idx + 1 < len(args):
            return args[idx + 1]
    return default


def main():
    args = list(idc.ARGV)
    name = get_arg(args, "--name")
    addr = get_arg(args, "--addr")
    out_path = get_arg(args, "--out", "orig/ida_pseudocode.txt")

    if not ida_hexrays.init_hexrays_plugin():
        Path(out_path).write_text("Hex-Rays decompiler not available.\n", encoding="utf-8")
        idaapi.qexit(0)

    if name:
        ea = ida_name.get_name_ea(idaapi.BADADDR, name)
    elif addr:
        ea = int(addr, 16)
    else:
        Path(out_path).write_text("Missing --name or --addr.\n", encoding="utf-8")
        idaapi.qexit(0)

    if ea == idaapi.BADADDR:
        Path(out_path).write_text("Function not found.\n", encoding="utf-8")
        idaapi.qexit(0)

    func = ida_funcs.get_func(ea)
    if not func:
        ida_funcs.add_func(ea)
        func = ida_funcs.get_func(ea)

    if not func:
        Path(out_path).write_text("Function not found after add_func.\n", encoding="utf-8")
        idaapi.qexit(0)

    try:
        cfunc = ida_hexrays.decompile(func)
    except Exception as exc:
        Path(out_path).write_text(f"Decompile error: {exc}\n", encoding="utf-8")
        idaapi.qexit(0)

    Path(out_path).write_text(str(cfunc), encoding="utf-8")
    idaapi.qexit(0)


if __name__ == "__main__":
    main()
