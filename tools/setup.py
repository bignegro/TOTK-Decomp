#!/usr/bin/env python3
"""
Set up the TOTK decomp pipeline.

This mirrors the Odyssey-style flow:
  - ensure tools/check (viking) is built
  - convert main.nso -> main.elf + main.uncompressed.nso
  - create a build directory (CMake)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "common"))

from common import setup_common as setup
from common.util import tools as common_tools


def find_tool_maybe(name: str) -> str | None:
    for finder in (
        common_tools.try_find_external_tool,
        common_tools.try_find_toolchain_tool,
        common_tools.try_find_binaries_repo_tool,
        common_tools.try_find_global_tool,
    ):
        path = finder(name)
        if path:
            return path
    return None


def _parse_version_tuple(text: str) -> tuple[int, ...]:
    parts: list[int] = []
    for part in text.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(-1)
    return tuple(parts)


def _find_latest_version_dir(root: Path) -> Path | None:
    if not root.is_dir():
        return None
    candidates = [path for path in root.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: _parse_version_tuple(path.name))


def maybe_set_windows_bindgen_env() -> None:
    if os.name != "nt":
        return
    if os.environ.get("BINDGEN_EXTRA_CLANG_ARGS"):
        return

    llvm_root = Path("C:/Program Files/LLVM")
    msvc_root = Path("C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC")
    sdk_root = Path("C:/Program Files (x86)/Windows Kits/10/Include")

    msvc_ver = _find_latest_version_dir(msvc_root)
    sdk_ver = _find_latest_version_dir(sdk_root)
    clang_ver = _find_latest_version_dir(llvm_root / "lib" / "clang")

    include_args: list[str] = []
    if msvc_ver:
        msvc_inc = msvc_ver / "include"
        if msvc_inc.is_dir():
            include_args.append(f'-I"{msvc_inc}"')

    if sdk_ver:
        for sub in ("ucrt", "shared", "um", "winrt"):
            inc = sdk_ver / sub
            if inc.is_dir():
                include_args.append(f'-I"{inc}"')

    if clang_ver:
        clang_inc = clang_ver / "include"
        if clang_inc.is_dir():
            include_args.append(f'-I"{clang_inc}"')

    if include_args:
        os.environ.setdefault("LIBCLANG_PATH", str(llvm_root / "bin"))
        os.environ.setdefault("CLANG_PATH", str(llvm_root / "bin" / "clang.exe"))
        os.environ.setdefault(
            "BINDGEN_EXTRA_CLANG_ARGS",
            "--target=x86_64-pc-windows-msvc " + " ".join(include_args),
        )


def install_viking_local() -> None:
    print(">>>> installing viking (tools/check)")
    apply_viking_patch()
    src_path = Path("tools/common/viking")
    install_path = Path("tools")

    try:
        subprocess.check_call(
            [
                "cargo",
                "build",
                "--manifest-path",
                str(src_path / "Cargo.toml"),
                "--release",
            ]
        )
    except FileNotFoundError:
        setup.fail("error: install cargo (rust) and try again")

    suffix = ".exe" if os.name == "nt" else ""
    for tool in ("check", "listsym", "decompme"):
        built = src_path / "target" / "release" / f"{tool}{suffix}"
        if not built.is_file():
            setup.fail(f"missing built tool: {built}")
        shutil.copy2(built, install_path / f"{tool}{suffix}")


def apply_viking_patch() -> None:
    patch_path = Path("tools/patches/viking.patch")
    if not patch_path.is_file():
        return

    repo_path = Path("tools/common")
    try:
        subprocess.check_call(
            ["git", "-C", str(repo_path), "apply", "--reverse", "--check", str(patch_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    except subprocess.CalledProcessError:
        pass

    subprocess.check_call(["git", "-C", str(repo_path), "apply", str(patch_path)])


def prepare_executable(original_nso: Path, data_dir: Path) -> None:
    if not original_nso.is_file():
        setup.fail(f"{original_nso} is not a file")

    data_dir.mkdir(parents=True, exist_ok=True)
    target_nso = data_dir / "main.nso"
    if original_nso.resolve() != target_nso.resolve():
        shutil.copy2(original_nso, target_nso)

    nx2elf = find_tool_maybe("nx2elf")
    if nx2elf:
        subprocess.check_call([nx2elf, str(target_nso), "--export-uncompressed"])
    else:
        print(">>> nx2elf not found; using Python fallback (tools/nso_to_elf.py)")
        subprocess.check_call(["python", "tools/nso_to_elf.py", str(target_nso), "--out", "data/main.elf"])

    converted_elf = target_nso.with_suffix(".elf")
    if not converted_elf.is_file():
        setup.fail("ELF conversion failed (missing main.elf)")

    uncompressed = target_nso.with_suffix(".uncompressed.nso")
    if uncompressed.is_file():
        uncompressed.rename(data_dir / "main.uncompressed.nso")


def create_build_dir(cmake_backend: str) -> None:
    build_dir = Path("build")
    if build_dir.is_dir() and (build_dir / "CMakeCache.txt").is_file():
        print(">>> build directory already exists: nothing to do")
        return
    build_dir.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            "cmake",
            "-G",
            cmake_backend,
            "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
            "-DCMAKE_TOOLCHAIN_FILE=toolchain/ToolchainNX64.cmake",
            "-B",
            str(build_dir),
        ]
    )
    print(">>> created build directory")


def maybe_generate_lists() -> None:
    ida_csv = Path("orig/ida_functions.csv")
    ida_segments = Path("orig/ida_segments.txt")
    if not ida_csv.exists() or not ida_segments.exists():
        return

    if not Path("data/file_list.yml").exists():
        subprocess.check_call(
            [
                "python",
                str(Path("tools/gen_file_list.py")),
                "--ida-csv",
                str(ida_csv),
                "--ida-segments",
                str(ida_segments),
                "--out",
                "data/file_list.yml",
            ]
        )

    if not Path("data/functions.csv").exists():
        subprocess.check_call(
            [
                "python",
                str(Path("tools/gen_functions_csv.py")),
                "--ida-csv",
                str(ida_csv),
                "--ida-segments",
                str(ida_segments),
                "--out",
                "data/functions.csv",
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up the TOTK decomp project")
    parser.add_argument("original_nso", type=Path, nargs="?", help="Path to main.nso")
    parser.add_argument("--cmake-backend", default="Ninja", help="CMake generator (Ninja, Unix Makefiles, etc.)")
    parser.add_argument("--project-only", action="store_true", help="Skip NSO conversion")
    parser.add_argument("--skip-viking", action="store_true", help="Skip building tools/check")
    args = parser.parse_args()

    if not args.skip_viking:
        maybe_set_windows_bindgen_env()
        install_viking_local()

    if not args.project_only:
        if args.original_nso is None:
            setup.fail("Please provide a path to main.nso (or use --project-only)")
        prepare_executable(args.original_nso, Path("data"))

    maybe_generate_lists()
    create_build_dir(args.cmake_backend)


if __name__ == "__main__":
    main()
