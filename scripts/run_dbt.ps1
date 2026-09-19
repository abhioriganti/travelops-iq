# Run one dbt operation with local .env settings loaded only in this process.
[CmdletBinding()]
param(
    [ValidateSet('build', 'debug', 'run', 'test')]
    [string]$Operation = 'build',
    [string]$Select
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot '.env'
$dbtExe = Join-Path $projectRoot '.venv\Scripts\dbt.exe'
$profilesDir = Join-Path $env:USERPROFILE '.dbt'
$profileFile = Join-Path $profilesDir 'profiles.yml'

if (-not (Test-Path $envFile)) { throw 'Missing .env. Copy .env.example and configure your local Snowflake values.' }
if (-not (Test-Path $dbtExe)) { throw 'Missing .venv dbt executable. Run pip install -r requirements.txt.' }
if (-not (Test-Path $profileFile)) { throw "Missing $profileFile. Copy dbt\\profiles.yml.example to this location." }

Get-Content -LiteralPath $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line.Length -eq 0 -or $line.StartsWith('#')) { return }
    $pair = $line -split '=', 2
    if ($pair.Count -ne 2 -or [string]::IsNullOrWhiteSpace($pair[0])) {
        throw 'Invalid .env entry. Use NAME=value.'
    }
    Set-Item -Path ("Env:" + $pair[0].Trim()) -Value $pair[1]
}

$dbtArguments = @(
    $Operation,
    '--project-dir', (Join-Path $projectRoot 'dbt'),
    '--profiles-dir', $profilesDir
)
if ($Select) {
    $dbtArguments += @('--select', $Select)
}

Write-Host "Running dbt $Operation. Credential values are not displayed." -ForegroundColor Cyan
& $dbtExe @dbtArguments
exit $LASTEXITCODE
