param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude")]
    [string]$AgentName
)

# Thin shim from the agent harness to the workflow engine (PowerShell twin of
# agent-hook.sh). Contract: always exit 0 and print exactly one JSON decision on stdout.
# A shim that cannot find a runtime fails open with `{}` plus a stderr note.
$ErrorActionPreference = "Continue"

function Emit([string]$Text) { [Console]::Out.WriteLine($Text) }

function Allow([string]$Reason) {
    if ($Reason) { [Console]::Error.WriteLine("agent-hook: $Reason; allowing") }
    Emit "{}"
    exit 0
}

# Self-locate so the hook does not depend on the caller's working directory.
$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $repoRoot "scripts/agent_workflow.py"))) {
    $repoRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($repoRoot) { $repoRoot = "$repoRoot".Trim() }
}
if (-not $repoRoot) { Allow "not inside a Git repository" }
$engine = Join-Path $repoRoot "scripts/agent_workflow.py"
if (-not (Test-Path $engine)) { Allow "workflow engine not found" }

# Hook payloads are UTF-8 JSON. Force UTF-8 on both sides of the pipe so Python never
# decodes stdin with the ANSI code page and PowerShell never re-encodes the payload.
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = $utf8
[Console]::InputEncoding = $utf8
[Console]::OutputEncoding = $utf8

# Buffer the payload so a failed first attempt can be retried with another runtime.
$payload = [Console]::In.ReadToEnd()

function Rest([string[]]$Items) {
    if ($Items.Length -gt 1) { return $Items[1..($Items.Length - 1)] }
    return @()
}

function Invoke-Engine([string[]]$Runtime) {
    $args = @(Rest $Runtime) + @($engine, "hook", "--agent", $AgentName)
    $result = $payload | & $Runtime[0] @args
    if ($LASTEXITCODE -eq 0) {
        Emit (($result | ForEach-Object { "$_" }) -join "`n")
        return $true
    }
    return $false
}

# uv first: PATH, then the installer's default location.
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) {
    $candidate = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
    if (Test-Path $candidate) { $uv = $candidate }
}
if ($uv) {
    if (Invoke-Engine @($uv, "--cache-dir", (Join-Path $repoRoot ".uv-cache"), "run", "--no-project", "python")) { exit 0 }
    [Console]::Error.WriteLine("agent-hook: uv failed; trying a system Python")
}

# The engine requires Python 3.11+ for tomllib. `py -3` avoids the
# Windows Store stub that sits on PATH as python.exe and only prints an install prompt.
foreach ($runtime in @(@("py", "-3"), @("python3"), @("python"))) {
    if (-not (Get-Command $runtime[0] -ErrorAction SilentlyContinue)) { continue }
    $check = @(Rest $runtime) + @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)")
    & $runtime[0] @check 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { continue }
    if (Invoke-Engine $runtime) { exit 0 }
}

Allow "no working Python runtime found"
