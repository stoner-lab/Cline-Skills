#Requires -Version 5.1
<#
.SYNOPSIS
    Tile rendered frames side-by-side into one contact sheet for one-glance review.

.DESCRIPTION
    The verify loop wants start | mid | end seen together: is the hook readable, is
    nothing clipped, do the labels line up? One image beats flipping between three.

    Windows/PowerShell port of scripts/contact-sheet.sh from iart-ai/manim-skills.
    All inputs must share the same height (frames from the same render do).

.PARAMETER Out
    Output PNG path.

.PARAMETER Frames
    Frame images to tile, left to right.

.EXAMPLE
    .\contact-sheet.ps1 sheet.png frame-start.png frame-mid.png frame-end.png
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Out,

    [Parameter(Mandatory = $true, Position = 1, ValueFromRemainingArguments = $true)]
    [string[]] $Frames
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "  x ffmpeg not on PATH - install it or add its bin folder to PATH" -ForegroundColor Red
    exit 2
}
if ($Frames.Count -lt 1) {
    Write-Host "  x need at least one frame" -ForegroundColor Red
    exit 2
}

foreach ($f in $Frames) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Host "  x frame not found: $f" -ForegroundColor Red
        exit 2
    }
}

$outFull = if ([System.IO.Path]::IsPathRooted($Out)) { $Out } else { Join-Path $PWD.ProviderPath $Out }
$outFull = [System.IO.Path]::GetFullPath($outFull)
$outDir = Split-Path -Parent $outFull
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

if ($Frames.Count -eq 1) {
    Copy-Item -LiteralPath (Resolve-Path -LiteralPath $Frames[0]).Path -Destination $outFull -Force
    Write-Host "  OK contact sheet (1 frame, copied) -> $outFull" -ForegroundColor Green
    exit 0
}

$args = @('-y', '-hide_banner', '-loglevel', 'error')
foreach ($f in $Frames) {
    # Resolve through the provider so relative paths follow Push-Location, not the
    # process working directory (they differ inside a PowerShell script).
    $args += @('-i', (Resolve-Path -LiteralPath $f).Path)
}
$args += @('-filter_complex', "hstack=inputs=$($Frames.Count)", $outFull)

& ffmpeg @args
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $outFull)) {
    Write-Host "  x ffmpeg failed - check that the frames exist and share the same height" -ForegroundColor Red
    exit 1
}

Write-Host "  OK contact sheet ($($Frames.Count) frames) -> $outFull" -ForegroundColor Green
