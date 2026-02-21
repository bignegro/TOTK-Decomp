Param(
  [string]$Config = "config/splat_nx.yml"
)

$ErrorActionPreference = "Stop"

python tools\patch_splat.py
python tools\extract_nso_segments.py data\main.nso
python -m splat split $Config --skip-version-check
