# PowerShell entry point for the same gate used by Bash and CI.
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
& uv --cache-dir (Join-Path $repoRoot ".uv-cache") run --no-project python (Join-Path $PSScriptRoot "verify_workflow.py") @args
exit $LASTEXITCODE
