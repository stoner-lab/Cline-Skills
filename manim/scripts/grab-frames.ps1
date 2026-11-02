#Requires -Version 5.1
<#
.SYNOPSIS
    Render a low-quality preview of a Manim scene and grab stills at chosen points.

.DESCRIPTION
    Manim's `-s` saves the *final* frame and silently ignores `-n`, so the upstream
    "manim -sql scene.py Scene -n 0,3" recipe yields the end frame every time.
    This helper renders the clip cheaply (-ql) and then lets ffmpeg pull real frames
    at the requested percentages of the timeline, which is what the verify loop needs.

    Part of the Cline/Windows port of iart-ai/manim-skills.

.PARAMETER Script
    Python file with the Scene, relative to the current location (e.g. scene.py).

.PARAMETER Scene
    Scene class name to render.

.PARAMETER Percent
    Points along the timeline to capture, in percent. Default 5,50,95.

.PARAMETER OutDir
    Folder for the PNGs. Default: current folder. Files are named f-<percent>.png.

.PARAMETER SkipRender
    Reuse an existing preview render instead of re-rendering.

.EXAMPLE
    .\grab-frames.ps1 scene.py Proof                 # f-5.png f-50.png f-95.png

.EXAMPLE
    .\grab-frames.ps1 scene.py Proof -Percent 0,30,100 -OutDir frames
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Script,

    [Parameter(Mandatory = $true, Position = 1)]
    [string] $Scene,

    [double[]] $Percent = @(5, 50, 95),

    [string] $OutDir = '.',

    [switch] $SkipRender
)

$ErrorActionPreference = 'Stop'
$invariant = [System.Globalization.CultureInfo]::InvariantCulture

foreach ($tool in 'python', 'ffmpeg', 'ffprobe') {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "  x $tool not on PATH (run scripts\manim-env-check.ps1)" -ForegroundColor Red
        exit 2
    }
}
if (-not (Test-Path -LiteralPath $Script)) {
    Write-Host "  x script not found: $Script" -ForegroundColor Red
    exit 2
}

$outPath = if ([System.IO.Path]::IsPathRooted($OutDir)) { $OutDir } else { Join-Path $PWD.ProviderPath $OutDir }
if (-not (Test-Path -LiteralPath $outPath)) { New-Item -ItemType Directory -Force -Path $outPath | Out-Null }

$previewName = "${Scene}_preview"
if (-not $SkipRender) {
    Write-Host "  rendering $Script :: $Scene at -ql ..." -ForegroundColor Cyan
    & python -m manim -ql $Script $Scene -o $previewName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  x render failed (exit $LASTEXITCODE) - read the Manim log above" -ForegroundColor Red
        exit 1
    }
}

$mp4 = Get-ChildItem -LiteralPath . -Recurse -File -Filter "$previewName.mp4" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime | Select-Object -Last 1
if (-not $mp4) {
    Write-Host "  x preview not found: no $previewName.mp4 under .\media (run without -SkipRender)" -ForegroundColor Red
    exit 2
}

$rawDur = & ffprobe -v error -show_entries format=duration -of csv=p=0 -- $mp4.FullName 2>$null | Select-Object -First 1
$duration = 0.0
[void][double]::TryParse(("$rawDur").Trim(), [ref] $duration)
if ($duration -le 0) {
    Write-Host "  x could not read the duration of $($mp4.FullName)" -ForegroundColor Red
    exit 1
}
Write-Host ("  preview: {0}  {1:0.00}s" -f $mp4.Name, $duration)

$made = @()
foreach ($p in $Percent) {
    $clamped = [math]::Min([math]::Max($p, 0), 100)
    $t = $duration * $clamped / 100
    $tArg = [string]::Format($invariant, '{0:0.###}', $t)
    $out = Join-Path $outPath ("f-{0}.png" -f [int] $clamped)

    & ffmpeg -y -loglevel error -ss $tArg -i $mp4.FullName -frames:v 1 -update 1 $out
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $out)) {
        Write-Host "  x ffmpeg could not grab a frame at $tArg s" -ForegroundColor Red
        exit 1
    }
    $made += $out
    Write-Host ("  OK   {0}  (t={1}s)" -f $out, $tArg) -ForegroundColor Green
}

Write-Host ''
Write-Host "  Inspect these with read_files, then tile them:" -ForegroundColor Cyan
Write-Host ("  contact-sheet.ps1 sheet.png " + (($made | ForEach-Object { "'$_'" }) -join ' '))
