param(
    [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
    [string[]]$MessageParts
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Set-Location -LiteralPath $RepoRoot

$env:PYTHONPATH = "."
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$message = ($MessageParts -join " ").Trim()
if ([string]::IsNullOrWhiteSpace($message)) {
    throw "Debes pasar un mensaje. Ejemplo: .\\scripts\\run_conversa_local.ps1 `"vendo mucho pero no sé si gano plata`""
}

python conversa-engine/main.py "$message"
