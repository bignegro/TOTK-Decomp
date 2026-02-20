# objdiff workflow

We use `objdiff` to export assembly matches and measure how much of `main.nso` (and other binaries) has been reconstructed. Keep the binary dumps under `orig/` and point the exporter at that directory before building.

Typical workflow:

1. Build the reconstructed `src/` code to produce an `objdump` (or use your toolchain’s assembly output).
2. Run `objdiff export --config config/objdiff-totk.toml --build-dir build --orig_dir orig`.
3. Commit the resulting `objdiff.json`/`objdiff.dump` artifacts in `tools/objdiff/` if you track them manually, then push to GitHub.
4. `decomp.dev` automatically picks up the latest `objdiff` export via the webhook and updates the progress bars for each binary/section.

See `config/objdiff-totk.toml` for a sample configuration tailored to the Switch `main.nso` and helper modules.
