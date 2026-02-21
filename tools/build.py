#!/usr/bin/env python3

import argparse
import subprocess
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the TOTK decomp project")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument("--verbose", action="store_true", help="Verbose build output")
    args = parser.parse_args()

    build_dir = Path("build")
    if not build_dir.is_dir():
        print("Please run tools/setup.py first.")
        raise SystemExit(1)

    cmake_args = ["cmake", "--build", str(build_dir)]
    if args.clean:
        cmake_args.append("--clean-first")
    if args.verbose:
        os.environ["VERBOSE"] = "1"

    try:
        subprocess.run(cmake_args, check=True)
    except subprocess.CalledProcessError:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
