Param()

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path ".").Path
$decompDir = Join-Path $repoRoot "tools/decomp.dev"
$patchPath = Join-Path $repoRoot "tools\\patches\\decomp_dev.patch"

if (Test-Path $patchPath) {
  $alreadyApplied = $false
  try {
    git -C $decompDir apply --reverse --check $patchPath 2>$null
    if ($LASTEXITCODE -eq 0) { $alreadyApplied = $true }
  } catch {}
  if (-not $alreadyApplied) {
    git -C $decompDir apply $patchPath
  }
}

Push-Location $decompDir
try {
  if (-not (Test-Path "node_modules")) {
    npm install
  }
  npm start
} finally {
  Pop-Location
}
