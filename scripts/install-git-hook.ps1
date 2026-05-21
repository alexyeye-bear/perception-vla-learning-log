$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$hookPath = Join-Path $repoRoot ".git/hooks/pre-commit"
$templatePath = Join-Path $repoRoot "scripts/pre-commit-update-topics.sh"

if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    throw "This script must be run inside a Git repository."
}

Copy-Item $templatePath $hookPath -Force
Write-Host "Installed pre-commit hook: $hookPath"
