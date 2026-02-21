param(
    [string]$BuildDir = "build",
    [string]$Target = "aarch64-none-elf"
)

$ErrorActionPreference = "Stop"

$llvmRoot = Join-Path $env:ProgramFiles "LLVM"
$clang = Join-Path $llvmRoot "bin\\clang.exe"
$ld = Join-Path $llvmRoot "bin\\ld.lld.exe"

if (!(Test-Path $clang)) {
    throw "clang not found at $clang. Install LLVM or update tools\\build.ps1."
}
if (!(Test-Path $ld)) {
    throw "ld.lld not found at $ld. Install LLVM or update tools\\build.ps1."
}

$srcRoot = Join-Path $PSScriptRoot "..\\src" | Resolve-Path
$buildRoot = Join-Path $PSScriptRoot "..\\$BuildDir"
$objRoot = Join-Path $buildRoot "obj"

New-Item -ItemType Directory -Force -Path $objRoot | Out-Null

$common = @(
    "--target=$Target",
    "-ffreestanding",
    "-fno-builtin",
    "-fno-exceptions",
    "-fno-rtti",
    "-fno-asynchronous-unwind-tables",
    "-fno-unwind-tables",
    "-O2",
    "-g0"
)

$srcFiles = Get-ChildItem $srcRoot -Recurse -File |
    Where-Object { $_.Extension -in ".c", ".cpp", ".cc", ".S", ".s" }

foreach ($file in $srcFiles) {
    $rel = $file.FullName.Substring($srcRoot.Path.Length + 1)
    $outDir = Join-Path $objRoot (Split-Path $rel -Parent)
    if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }
    $outObj = Join-Path $outDir ($file.BaseName + ".o")
    & $clang @common -c $file.FullName -o $outObj
}

$objs = @(
    Get-ChildItem $objRoot -Recurse -Filter *.o |
        ForEach-Object { $_.FullName }
)
if ($objs.Count -eq 0) {
    Write-Host "No objects built. Add .c/.cpp/.S files under src/."
    exit 0
}

$linkerScript = Join-Path $PSScriptRoot "..\\config\\link.ld"
$elfOut = Join-Path $buildRoot "main.elf"

& $ld `
    --nostdlib `
    --unresolved-symbols=ignore-all `
    -T $linkerScript `
    -o $elfOut `
    @objs
if ($LASTEXITCODE -ne 0) {
    throw "ld.lld failed to link."
}
Write-Host "Built $elfOut"
