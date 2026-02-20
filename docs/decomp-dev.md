# decomp.dev integration

The `decomp.dev` tracker (https://decomp.dev) lets Switch clean-room teams show progress by consuming `objdiff` exports. This repo will appear on the tracker once you register it at `https://decomp.dev/projects` and link the GitHub repository.

Steps to connect:

1. **Create the GitHub repo** (`gh repo create <owner>/TOTK-Decomp --public --source=. --remote=origin`) so there is a remote for `decomp.dev` to watch.
2. **Register on decomp.dev** with the same GitHub repository URL. Pick an appropriate project slug (`totk` or `tears-of-the-kingdom`) during registration.
3. **Authorize the tracker** so it can read the repo. The `encounter/decomp.dev` backend handles webhook delivery and comment automation; you only need to grant read access to the repo.
4. **Wire objdiff exports**: when you make progress on a binary, run `objdiff` (see `docs/objdiff.md`) and push the generated stats. The tracker uses those artifacts to render completeness bars.

For more setup details or to run a local copy of the tracker, consult the upstream source at `https://github.com/encounter/decomp.dev`. Reuse their API keys/webhooks if you want a staging tracker or wish to submit smaller PRs to their repo.
