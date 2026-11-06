<#
.SYNOPSIS
    Quet prompt injection trong tai lieu nhi phan (docx/xlsx/pptx/pdf/zip):
    trich text -> quet bang scan_injection.ps1. Offline, khong gui du lieu ra ngoai.

.DESCRIPTION
    Wrapper: khong tu chua luat, chi lo buoc "chuyen sang text" roi goi scanner.
    Text thuong (.md/.txt/...) duoc chuyen thang cho scanner, khong qua python.

    Exit code: 0 = sach, 1 = can xem / khong trich duoc, 2 = chan
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [string[]] $Path,

    [switch] $Recurse,

    [switch] $KeepExtracted,

    [string] $Scanner,

    [string] $Extractor,

    [int] $MaxChars = 2000000
)

$ErrorActionPreference = 'Stop'

# $PSScriptRoot khong dung duoc trong default cua param (PS 5.1) -> resolve o day
if (-not $Scanner) { $Scanner = Join-Path $PSScriptRoot 'scan_injection.ps1' }
if (-not $Extractor) { $Extractor = Join-Path $PSScriptRoot 'extract_text.py' }

if (-not (Test-Path -LiteralPath $Scanner)) { throw "khong thay scanner: $Scanner" }
if (-not (Test-Path -LiteralPath $Extractor)) { throw "khong thay extractor: $Extractor" }

$NeedsExtract = @('.docx', '.docm', '.xlsx', '.xlsm', '.pptx', '.pptm', '.pdf', '.zip')

$tempDir = Join-Path $env:TEMP 'cline-scan'
if (-not (Test-Path -LiteralPath $tempDir)) { New-Item -ItemType Directory -Force -Path $tempDir | Out-Null }

function Invoke-Scanner {
    param([string] $File)
    # Out-Host: day output cua scanner ra console, khong de lot vao return value
    & powershell -NoProfile -ExecutionPolicy Bypass -File $Scanner -Path $File | Out-Host
    return [int] $LASTEXITCODE
}

$targets = @()
foreach ($p in $Path) {
    if (-not (Test-Path -LiteralPath $p)) { Write-Warning "khong thay: $p"; continue }
    $item = Get-Item -LiteralPath $p
    if ($item.PSIsContainer) {
        if ($Recurse) { $targets += @(Get-ChildItem -LiteralPath $p -Recurse -File | ForEach-Object { $_.FullName }) }
        else { Write-Warning "thu muc can -Recurse: $p" }
    }
    else { $targets += $item.FullName }
}

if ($targets.Count -eq 0) { Write-Warning 'khong co gi de quet'; exit 0 }

$worst = 0
foreach ($file in $targets) {
    $ext = [System.IO.Path]::GetExtension($file).ToLowerInvariant()
    Write-Host ''
    Write-Host ("### {0}" -f $file)

    if ($NeedsExtract -notcontains $ext) {
        $c = Invoke-Scanner -File $file
        if ($c -gt $worst) { $worst = $c }
        continue
    }

    $text = $null
    $prevPref = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $text = & python $Extractor $file 2>$null
        $rc = $LASTEXITCODE
    }
    catch {
        $text = $null
        $rc = 1
    }
    finally {
        $ErrorActionPreference = $prevPref
    }

    if ($rc -ne 0 -or -not $text) {
        Write-Host ("[CHUA QUET] khong trich duoc text tu {0} (kiem tra python / thu vien doc)" -f $ext)
        if ($worst -lt 1) { $worst = 1 }
        continue
    }

    $leaf = [System.IO.Path]::GetFileName($file)
    $tmp = Join-Path $tempDir ($leaf + '.' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.txt')
    [System.IO.File]::WriteAllText($tmp, ($text -join "`n"), (New-Object System.Text.UTF8Encoding($false)))

    Write-Host ("           (text trich tu: {0})" -f $leaf)
    $c = Invoke-Scanner -File $tmp
    if ($c -gt $worst) { $worst = $c }

    if ($KeepExtracted) { Write-Host ("           (text trich: {0})" -f $tmp) }
    else { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
}

exit $worst
