param(
    [string]$Project = ".",
    [string]$Out = "build\\objdiff-report.json",
    [string]$LogLevel = "info"
)

$ErrorActionPreference = "Stop"

$exe = Join-Path $env:USERPROFILE ".cargo\\bin\\objdiff-cli.exe"
if (!(Test-Path $exe)) {
    $exe = "objdiff-cli"
}

$args = @("report", "generate", "-p", $Project, "-o", $Out)

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.Arguments = ($args -join " ")
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false

$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$null = $proc.Start()

$start = Get-Date
while (-not $proc.HasExited) {
    $elapsed = (Get-Date) - $start
    $pct = [int](($elapsed.TotalSeconds % 60) / 60 * 100)
    Write-Progress -Activity "objdiff report generate" `
        -Status ("Elapsed {0:hh\:mm\:ss}" -f $elapsed) `
        -PercentComplete $pct
    Start-Sleep -Seconds 1
}

Write-Progress -Activity "objdiff report generate" -Completed -Status "Done"

$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()

if ($stdout) { Write-Output $stdout }
if ($stderr) { Write-Error $stderr }

exit $proc.ExitCode
