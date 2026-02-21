# Tears of the Kingdom Decomp (WIP)

This repo holds clean-room reconstruction work for the legally obtained Nintendo Switch game Tears of the Kingdom.
No ROMs, game data, or proprietary assets should ever be checked in.

## Status
- decomp.dev project: waiting on project slug/configuration
- progress tracking: objdiff (waiting on exporter config)

## Layout
- orig/   Local dumps (ignored by git)
- src/    Reconstructed source
- include/Headers and types
- tools/  Scripts and tooling
- config/ Tool and build configs
- docs/   Notes and references

## Local Setup (high level)
This repo supports a full Odyssey-style pipeline plus objdiff tracking.

### 1) Dependencies
- Git (and `git submodule update --init --recursive`)
- Python 3.11+
- Ninja + CMake 3.13+
- Rust (for `tools/check`, `tools/listsym`, `tools/decompme`)
- LLVM/Clang + lld (AArch64 target)
- `nx2elf` in your PATH (or set `NX_DECOMP_TOOLS_NX2ELF` env var)

### 2) Prepare the original executable
Use your legally obtained `main.nso` (ExeFS dump only is enough).

```powershell
python tools\setup.py C:\path\to\main.nso
```

This converts to:
- `data/main.nso`
- `data/main.elf`
- `data/main.uncompressed.nso`
and builds the check tools.

### 3) Generate function lists
```powershell
python tools\gen_file_list_ns.py --ida-csv orig\ida_functions.csv --ida-segments orig\ida_segments.txt --out data\file_list.yml --roots config\file_map.yml
python tools\gen_functions_csv.py --ida-csv orig\ida_functions.csv --ida-segments orig\ida_segments.txt --out data\functions.csv
```

### 4) Build and check
```powershell
python tools\build.py
tools\check            # check all
tools\check SomeFunc   # check one
```

### 5) Objdiff / decomp.dev progress
```powershell
python tools\make_target_obj.py
objdiff-cli report generate -o build\report.json
```

## Tracking & Contributions
- Keep proprietary data (ROMs, dumps, binaries) in `orig/` or local-only folders; they stay out of version control.
- Push small, focused commits so `objdiff` diffs are easy to review.
- Link progress to `decomp.dev`; see `docs/decomp-dev.md` for how this repo should connect to the tracker.
