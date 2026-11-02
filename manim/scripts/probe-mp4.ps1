#Requires -Version 5.1
<#
.SYNOPSIS
    Print (and optionally assert) the real spec of a rendered MP4.

.DESCRIPTION
    Renders lie; the file does not. Reads resolution, codec, frame rate and duration
    straight from the encoded MP4 with ffprobe, then checks them against the expected
    contract so "1920x1080 @60 h264" is verified, not assumed.

    Windows/PowerShell port of scripts/probe-mp4.sh from iart-ai/manim-skills.

.PARAMETER Path
    MP4 (or any ffprobe-readable file) to probe.

.PARAMETER ExpectedResolution
    Optional "WxH" contract, e.g. 1920x1080.

.PARAMETER ExpectedFps
    Optional frame-rate contract, e.g. 60 (tolerance +/- 0.5).

.EXAMPLE
    .\probe-mp4.ps1 .\media\videos\scene\1080p60\MyScene.mp4

.EXAMPLE
    .\probe-mp4.ps1 .\media\videos\scene\1080p60\MyScene.mp4 1920x1080 60
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Path,

    [Parameter(Position = 1)]
    [string] $ExpectedResolution,

    [Parameter(Position = 2)]
    [double] $ExpectedFps = 0
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Host "  x file not found: $Path" -ForegroundColor Red
    exit 2
}
$file = (Resolve-Path -LiteralPath $Path).Path

foreach ($tool in 'ffprobe', 'ffmpeg') {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "  x $tool not on PATH - install ffmpeg or add its bin folder to PATH" -ForegroundColor Red
        exit 2
    }
}

function Get-VideoField {
    param([string] $Entry, [string] $File)
    $value = & ffprobe -v error -select_streams v:0 -show_entries $Entry -of csv=p=0 -- $File 2>$null |
        Select-Object -First 1
    return ("$value").Trim()
}

$width  = Get-VideoField 'stream=width' $file
$height = Get-VideoField 'stream=height' $file
$codec  = Get-VideoField 'stream=codec_name' $file
$rate   = Get-VideoField 'stream=r_frame_rate' $file
$rawDur = (& ffprobe -v error -show_entries format=duration -of csv=p=0 -- $file 2>$null |
        Select-Object -First 1)
$duration = 0.0
[void][double]::TryParse(("$rawDur").Trim(), [ref] $duration)

$fps = 0.0
if ($rate -match '^(\d+)/(\d+)$') {
    $n = [double] $Matches[1]; $d = [double] $Matches[2]
    if ($d -ne 0) { $fps = $n / $d }
}
elseif ($rate -match '^\d+(\.\d+)?$') {
    $fps = [double] $rate
}

$name = Split-Path -Leaf $file
Write-Host ("  {0}: {1}x{2}  {3}  {4:0.###} fps  {5:0.00}s" -f
    $name, $width, $height, $codec, $fps, $duration)

$fail = 0
if ($ExpectedResolution) {
    $actual = "${width}x${height}"
    if ($actual -ne $ExpectedResolution) {
        Write-Host "  x resolution $actual != $ExpectedResolution" -ForegroundColor Red
        $fail = 1
    }
}
if ($ExpectedFps -gt 0 -and [math]::Abs($fps - $ExpectedFps) -gt 0.5) {
    Write-Host ("  x fps {0:0.###} != {1}" -f $fps, $ExpectedFps) -ForegroundColor Red
    $fail = 1
}
if ($codec -ne 'h264') {
    Write-Host "  ! codec $codec (not h264 - confirm player/platform compatibility)" -ForegroundColor Yellow
}
if ($duration -le 0) {
    Write-Host "  ! duration unreadable or zero - the encode may be broken" -ForegroundColor Yellow
    $fail = 1
}

if ($fail -eq 0) {
    Write-Host "  OK spec verified" -ForegroundColor Green
    exit 0
}
exit 1
