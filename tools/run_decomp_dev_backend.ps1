Param(
  [string]$ConfigTemplate = "config/decomp-dev.local.example.yml"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path ".").Path
$decompDir = Join-Path $repoRoot "tools/decomp.dev"
$configPath = Join-Path $decompDir "config.yml"
$patchPath = Join-Path $repoRoot "tools\\patches\\decomp_dev.patch"

if (-not (Test-Path $ConfigTemplate)) {
  throw "Missing config template: $ConfigTemplate"
}

if (-not (Test-Path $configPath)) {
  Copy-Item -Force $ConfigTemplate $configPath
  Write-Host "Created $configPath from $ConfigTemplate"
}

if ($env:DECOMP_DEV_GITHUB_TOKEN) {
  $content = Get-Content $configPath -Raw
  if ($content -match "ghp_REPLACE_ME") {
    $content = $content -replace "ghp_REPLACE_ME", $env:DECOMP_DEV_GITHUB_TOKEN
    Set-Content -Path $configPath -Value $content -NoNewline
    Write-Host "Injected DECOMP_DEV_GITHUB_TOKEN into config.yml"
  }
}

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
  cargo run -p decomp-dev-web
} finally {
  Pop-Location
}
