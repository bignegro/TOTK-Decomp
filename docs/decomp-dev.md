# decomp.dev integration

The `decomp.dev` tracker (https://decomp.dev) lets Switch clean-room teams show progress by consuming `objdiff` exports. This repo will appear on the tracker once you register it at `https://decomp.dev/projects` and link the GitHub repository.

Steps to connect:

1. **Create the GitHub repo** (`gh repo create <owner>/TOTK-Decomp --public --source=. --remote=origin`) so there is a remote for `decomp.dev` to watch.
2. **Register on decomp.dev** with the same GitHub repository URL. Pick an appropriate project slug (`totk` or `tears-of-the-kingdom`) during registration.
3. **Authorize the tracker** so it can read the repo. The `encounter/decomp.dev` backend handles webhook delivery and comment automation; you only need to grant read access to the repo.
4. **Wire objdiff exports**: when you make progress on a binary, run `objdiff` (see `docs/objdiff.md`) and push the generated stats. The tracker uses those artifacts to render completeness bars.

## Local decomp.dev (localhost)

This repo includes the decomp.dev source as a submodule in `tools/decomp.dev`.
Use the helper scripts to run it locally.

1) Create a local config:
   - Copy `config/decomp-dev.local.example.yml` to `tools/decomp.dev/config.yml`
   - Put your GitHub PAT in the `github.token` field
   - Or set `DECOMP_DEV_GITHUB_TOKEN` before running the backend script

2) Start the backend (includes job workers):
```powershell
tools\run_decomp_dev_backend.ps1
```

3) Start the frontend in a second terminal:
```powershell
tools\run_decomp_dev_frontend.ps1
```

4) Open: http://localhost:3000
   - Dev mode is enabled, so you can log in without OAuth.
   - Add the project at `/manage/new` (use your GitHub repo URL).
   - Click "Refresh" to fetch report artifacts from GitHub Actions.

Note: decomp.dev fetches reports from GitHub Actions artifacts. The workflow in
`.github/workflows/progress.yml` uploads `build/report.json` as `${VERSION}_report`.
