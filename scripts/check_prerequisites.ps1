$ErrorActionPreference = 'Continue'

Write-Host 'Travel Operations Analytics Lab - local prerequisite check' -ForegroundColor Cyan

$commands = @('git', 'python', 'dbt', 'node')
foreach ($name in $commands) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        Write-Host "[MISSING] $name" -ForegroundColor Yellow
        continue
    }

    try {
        $version = & $name --version 2>&1 | Select-Object -First 1
        Write-Host "[OK] $name : $version" -ForegroundColor Green
    }
    catch {
        Write-Host "[FOUND] $name (version command did not succeed)" -ForegroundColor Yellow
    }
}

if (-not (Test-Path '.venv')) {
    Write-Host '[NEXT] Create a project virtual environment after installing a supported Python version.' -ForegroundColor Yellow
}
else {
    Write-Host '[OK] .venv exists' -ForegroundColor Green
}

Write-Host 'Manual prerequisites: Snowflake trial account; ThoughtSpot trial or Developer Edition; VS Code recommended.' -ForegroundColor Cyan
