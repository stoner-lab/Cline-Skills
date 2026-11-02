#Requires -Version 5.1
<#
.SYNOPSIS
    Verify that the Manim toolchain is usable from Cline (PowerShell on Windows).

.DESCRIPTION
    Checks python, the manim module, the manim.exe shim, ffmpeg/ffprobe and a LaTeX
    engine, then reports one PASS/FAIL line per item. Run this before blaming the
    scene code when a render fails.

    Part of the Cline/Windows port of iart-ai/manim-skills.

.EXAMPLE
    .\manim-env-check.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$fails = 0

function Write-Item {
    param([string] $Label, [bool] $Ok, [string] $Detail, [bool] $Optional = $false)
    if ($Ok) {
        Write-Host ("  OK   {0,-10} {1}" -f $Label, $Detail) -ForegroundColor Green
    }
    elseif ($Optional) {
        Write-Host ("  WARN {0,-10} {1}" -f $Label, $Detail) -ForegroundColor Yellow
    }
    else {
        Write-Host ("  FAIL {0,-10} {1}" -f $Label, $Detail) -ForegroundColor Red
        $script:fails++
    }
}

Write-Host "Manim environment (Cline / Windows)" -ForegroundColor Cyan

# Python
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    $ver = (& python --version 2>&1) -join ' '
    Write-Item 'python' $true "$ver ($($py.Source))"
}
else {
    Write-Item 'python' $false 'not found on PATH'
}

# Manim module + version
$manimVersion = (& python -c "import manim; print(manim.__version__)" 2>&1) -join ' '
if ($LASTEXITCODE -eq 0 -and $manimVersion -match '^\d') {
    Write-Item 'manim' $true "Manim Community v$manimVersion  (call it as: python -m manim)"
}
else {
    Write-Item 'manim' $false "not importable - run: python -m pip install manim"
}

# manim.exe shim (convenience only)
$shim = Get-Command manim -ErrorAction SilentlyContinue
if ($shim) { Write-Item 'manim.exe' $true $shim.Source }
else { Write-Item 'manim.exe' $false 'not on PATH - harmless, use python -m manim' $true }

# ffmpeg / ffprobe
foreach ($tool in 'ffmpeg', 'ffprobe') {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if ($cmd) { Write-Item $tool $true $cmd.Source }
    else { Write-Item $tool $false 'not on PATH - install ffmpeg and add its bin folder' }
}

# LaTeX engine (only needed for Tex / MathTex)
$tex = Get-Command latex -ErrorAction SilentlyContinue
if (-not $tex) { $tex = Get-Command pdflatex -ErrorAction SilentlyContinue }
if ($tex) {
    $texVersion = (& $tex.Source --version 2>&1 | Select-Object -First 1) -join ''
    Write-Item 'latex' $true $texVersion
}
else {
    Write-Item 'latex' $false 'no latex/pdflatex - Tex and MathTex will fail (Text still works)'
}

# dvisvgm is what Manim uses to turn dvi into svg
$dvisvgm = Get-Command dvisvgm -ErrorAction SilentlyContinue
if ($dvisvgm) { Write-Item 'dvisvgm' $true $dvisvgm.Source }
else { Write-Item 'dvisvgm' $false 'missing - MathTex cannot render' }

Write-Host ''
if ($fails -eq 0) {
    Write-Host "  All required tools present - you can render." -ForegroundColor Green
    exit 0
}
Write-Host "  $fails required item(s) missing - fix those before rendering." -ForegroundColor Red
exit 1
