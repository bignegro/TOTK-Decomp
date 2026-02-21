#!/usr/bin/env python3
"""
Patch the installed splat package to support an unsupported platform (e.g., NX).

This adds:
- a NullDisassembler fallback when options.opts.is_unsupported_platform is true
- a stub platform module splat.platforms.nx
"""

from __future__ import annotations

from pathlib import Path


def patch_disassembler_instance(root: Path) -> None:
    path = root / "disassembler" / "disassembler_instance.py"
    text = path.read_text(encoding="utf-8")

    marker = "if options.opts.is_unsupported_platform:"
    if marker in text:
        return

    insert_after = "from ..util import options"
    if insert_after not in text:
        raise SystemExit("unexpected splat version: could not find options import")

    text = text.replace(
        insert_after,
        insert_after
        + "\n\n# Allow unsupported platforms by using a NullDisassembler.\n",
    )

    needle = "def create_disassembler_instance"
    idx = text.find(needle)
    if idx == -1:
        raise SystemExit("unexpected splat version: missing create_disassembler_instance")

    lines = text.splitlines()
    out_lines: list[str] = []
    inserted = False
    for line in lines:
        out_lines.append(line)
        if line.strip().startswith("def create_disassembler_instance"):
            inserted = True
        elif inserted and line.strip().startswith("global __instance"):
            # Insert after globals are declared.
            out_lines.append("    if options.opts.is_unsupported_platform:")
            out_lines.append("        __instance = NullDisassembler()")
            out_lines.append("        __initialized = True")
            out_lines.append("        return")
            inserted = False

    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def ensure_platform_nx(root: Path) -> None:
    plat = root / "platforms" / "nx.py"
    if plat.exists():
        return
    plat.write_text(
        "def init(_rom_bytes: bytes) -> None:\n    pass\n",
        encoding="utf-8",
    )


def main() -> None:
    import splat  # type: ignore

    root = Path(splat.__file__).resolve().parent
    patch_disassembler_instance(root)
    ensure_platform_nx(root)
    print(f"Patched splat in {root}")


if __name__ == "__main__":
    main()
