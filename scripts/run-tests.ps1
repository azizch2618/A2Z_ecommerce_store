# A2Z Tools backend test runner — PostgreSQL (CI) or SQLite (fast local).
#
# Usage:
#   .\scripts\run-tests.ps1 smoke
#   .\scripts\run-tests.ps1 all
#   $env:TEST_DB = 'postgres'; .\scripts\run-tests.ps1 ci
param(
    [Parameter(Position = 0)]
    [ValidateSet('smoke', 'integration', 'regression', 'security', 'slow', 'all', 'ci')]
    [string]$Group = 'all'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Reports = Join-Path $Backend 'reports'

Set-Location $Backend
New-Item -ItemType Directory -Force -Path $Reports | Out-Null

$TestDb = if ($env:TEST_DB) { $env:TEST_DB } else { 'sqlite' }
$ReuseDbFlag = @()

if ($TestDb -eq 'postgres') {
    $env:USE_SQLITE_FOR_TESTS = '0'
    if (-not $env:POSTGRES_HOST) { $env:POSTGRES_HOST = 'localhost' }
    if (-not $env:POSTGRES_DB) { $env:POSTGRES_DB = 'a2z_tools_test' }
    if (-not $env:POSTGRES_USER) { $env:POSTGRES_USER = 'a2z' }
    if (-not $env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD = 'changeme' }
    if (-not $env:POSTGRES_TEST_DB) { $env:POSTGRES_TEST_DB = 'test_a2z_tools' }
    Write-Host "==> Waiting for PostgreSQL ($($env:POSTGRES_HOST))..."
    python scripts/wait_for_postgres.py
    $ReuseDbFlag = @('--reuse-db')
} else {
    $env:USE_SQLITE_FOR_TESTS = '1'
    Write-Host '==> SQLite in-memory mode (set `$env:TEST_DB = "postgres"` for PostgreSQL)'
}

$env:DJANGO_SETTINGS_MODULE = 'config.settings.test'

function Run-Group {
    param([string]$Marker, [string]$Junit)
    Write-Host ""
    Write-Host "==> Running $Marker tests..."
    pytest -m $Marker @ReuseDbFlag --junitxml=$Junit -q
}

function Run-Ci {
    Write-Host '==> Django system check'
    python manage.py check

    $coverageXml = Join-Path $Reports 'coverage.xml'
    $htmlCov = Join-Path $Reports 'htmlcov'
    $junitFull = Join-Path $Reports 'junit-full.xml'

    Run-Group 'smoke' (Join-Path $Reports 'junit-smoke.xml')
    Run-Group 'security' (Join-Path $Reports 'junit-security.xml')
    Run-Group 'regression' (Join-Path $Reports 'junit-regression.xml')
    Run-Group 'integration' (Join-Path $Reports 'junit-integration.xml')

    Write-Host ''
    Write-Host '==> Full suite with coverage (excluding slow)...'
    pytest -m 'not slow' @ReuseDbFlag `
        --cov=apps --cov=api --cov=config `
        --cov-report=term-missing:skip-covered `
        "--cov-report=xml:$coverageXml" `
        "--cov-report=html:$htmlCov" `
        "--junitxml=$junitFull" `
        -q

    Write-Host ''
    Write-Host "Reports: $Reports/"
}

switch ($Group) {
    { $_ -in @('smoke', 'integration', 'regression', 'security') } {
        Run-Group $Group (Join-Path $Reports "junit-$Group.xml")
    }
    'slow' {
        pytest -m slow @ReuseDbFlag --junitxml=(Join-Path $Reports 'junit-slow.xml') -q
    }
    'all' {
        $coverageXml = Join-Path $Reports 'coverage.xml'
        pytest -m 'not slow' @ReuseDbFlag `
            --cov=apps --cov=api --cov=config `
            --cov-report=term-missing:skip-covered `
            "--cov-report=xml:$coverageXml" `
            -q
    }
    'ci' {
        Run-Ci
    }
}
