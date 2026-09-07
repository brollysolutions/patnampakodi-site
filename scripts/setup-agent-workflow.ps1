# Run from any directory; never stage, commit, push, or overwrite local notes.
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it using https://docs.astral.sh/uv/getting-started/installation/ and reopen the terminal."
}
& uv --cache-dir (Join-Path $repoRoot ".uv-cache") run --no-project python (Join-Path $PSScriptRoot "setup_workflow.py")
exit $LASTEXITCODE
