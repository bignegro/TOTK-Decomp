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
- Install Git and configure your GitHub CLI (`gh auth login` recommended).
- Install Python 3.11+ if scripts/tools in `tools/` rely on it.
- Choose a disassembler (Ghidra, IDA, or alike) and point it at the dumped binaries.
- Install `objdiff` and configure it for the Tears of the Kingdom binaries to drive progress tracking.
- Follow `docs/decomp-dev.md` to register the repo with the upstream `decomp.dev` tracker.

## Tracking & Contributions
- Keep proprietary data (ROMs, dumps, binaries) in `orig/` or local-only folders; they stay out of version control.
- Push small, focused commits so `objdiff` diffs are easy to review.
- Link progress to `decomp.dev`; see `docs/decomp-dev.md` for how this repo should connect to the tracker.
