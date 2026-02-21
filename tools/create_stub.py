#!/usr/bin/env python3
"""
Create a stub C file for a function name.

Usage:
  python tools/create_stub.py --name sub_7100000030 --addr 0x7100000030
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def is_c_ident(name: str) -> bool:
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name) is not None


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a stub source file for a function.")
    parser.add_argument("--name", required=True, help="Function symbol name")
    parser.add_argument("--addr", default=None, help="Address for comment (optional)")
    parser.add_argument("--out-dir", default="src/Game/Unk", help="Output directory for stubs")
    parser.add_argument("--set-wip", action="store_true", help="Mark function Wip in tracking files")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(args.name) + ".c"
    path = out_dir / filename
    if path.exists():
        print(f"Stub already exists: {path}")
        return

    func_name = args.name
    if is_c_ident(func_name):
        c_name = func_name
        alias = None
    else:
        # Create a safe identifier and force the real symbol via asm label.
        base = sanitize_filename(func_name)
        c_name = f"fn_{base}"
        alias = func_name

    comment_addr = f" @ {args.addr}" if args.addr else ""
    lines = []
    lines.append("// Auto-generated stub")
    lines.append(f"// {func_name}{comment_addr}")
    lines.append("")
    if alias:
        lines.append(f'__attribute__((naked, used)) void {c_name}(void) __asm__("{alias}");')
        lines.append(f"__attribute__((naked, used)) void {c_name}(void) {{")
    else:
        lines.append(f"__attribute__((naked, used)) void {c_name}(void) {{")
    lines.append('    __asm__ volatile("ret");')
    lines.append("}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="ascii")
    print(f"Wrote {path}")

    if args.set_wip:
        from subprocess import check_call

        check_call(
            [
                "python",
                str(Path("tools/set_status.py")),
                "--name",
                func_name,
                "--status",
                "Wip",
            ]
        )


if __name__ == "__main__":
    main()
