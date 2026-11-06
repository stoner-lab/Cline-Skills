<#
.SYNOPSIS
    Chụp ảnh một cửa sổ ứng dụng (hoặc toàn màn hình) ra PNG, dùng cho báo cáo otchet.

.DESCRIPTION
    Mặc định: tìm cửa sổ của tiến trình, đưa lên trước, chụp đúng phần cửa sổ đó
    (không chụp cả màn hình), lưu PNG. Không gửi dữ liệu đi đâu, không phụ thuộc MCP.

.PARAMETER ProcessName
    Tên tiến trình, không cần .exe: Arduino, octave-gui, rstudio, cline-app, WindowsTerminal...

.PARAMETER TitleMatch
    Lọc thêm theo chuỗi con trong tiêu đề cửa sổ (không phân biệt hoa/thường).

.PARAMETER Out
    Đường dẫn file PNG. Thư mục sẽ được tạo nếu chưa có.

.PARAMETER DelayMs
    Chờ bao nhiêu ms sau khi đưa cửa sổ lên trước, trước khi chụp. Mặc định 600.

.PARAMETER NoActivate
    Không đưa cửa sổ lên trước (chụp nguyên trạng thái hiện tại).

.PARAMETER FullScreen
    Chụp toàn bộ màn hình chính thay vì một cửa sổ.

.PARAMETER Crop
    Vùng cắt theo pixel, dạng "x,y,w,h" (toạ độ tính từ góc trên-trái của ảnh vừa chụp).

.PARAMETER CropPercent
    Vùng cắt theo tỉ lệ 0..1 của ảnh vừa chụp, dạng "x,y,w,h" — ví dụ "0.02,0.10,0.60,0.35".
    Dùng khi chưa biết pixel chính xác; "phần cần thiết" luôn phải cắt, không chèn ảnh
    nguyên cửa sổ có desktop/taskbar/thanh công cụ thừa.

.EXAMPLE
    .\capture_window.ps1 -ProcessName Arduino -Out .\images\01_compile.png

.EXAMPLE
    .\capture_window.ps1 -ProcessName cline-app -TitleMatch "octave" -Out .\images\02.png

.EXAMPLE
    .\capture_window.ps1 -FullScreen -Out .\images\03_screen.png
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string] $ProcessName,

    [string] $TitleMatch,

    [Parameter(Mandatory = $true)]
    [string] $Out,

    [int] $DelayMs = 600,

    [switch] $NoActivate,

    [switch] $FullScreen,

    [string] $Crop,

    [string] $CropPercent
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class OtchetWin {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    public struct RECT { public int Left, Top, Right, Bottom; }
}
'@

[void][OtchetWin]::SetProcessDPIAware()

$outPath = [System.IO.Path]::GetFullPath($Out)
$outDir = [System.IO.Path]::GetDirectoryName($outPath)
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

$rect = New-Object OtchetWin+RECT

if ($FullScreen) {
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $rect.Left = $bounds.Left
    $rect.Top = $bounds.Top
    $rect.Right = $bounds.Right
    $rect.Bottom = $bounds.Bottom
}
else {
    if (-not $ProcessName) {
        [Console]::Error.WriteLine('can -ProcessName (hoac dung -FullScreen)')
        exit 2
    }

    $name = $ProcessName -replace '\.exe$', ''
    $candidates = @(Get-Process -Name $name -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowHandle -ne 0 })

    if ($TitleMatch) {
        $candidates = @($candidates | Where-Object { $_.MainWindowTitle -like "*$TitleMatch*" })
    }
    if ($candidates.Count -eq 0) {
        $hint = if ($TitleMatch) { " (tieu de chua '$TitleMatch')" } else { '' }
        [Console]::Error.WriteLine(("khong tim thay cua so cho '{0}'{1}. Mo ung dung truoc khi chup." -f $name, $hint))
        exit 2
    }

    $proc = $candidates[0]
    $h = $proc.MainWindowHandle

    if (-not $NoActivate) {
        [void][OtchetWin]::ShowWindow($h, 9)
        [void][OtchetWin]::SetForegroundWindow($h)
        Start-Sleep -Milliseconds $DelayMs
    }

    if (-not [OtchetWin]::GetWindowRect($h, [ref]$rect)) {
        [Console]::Error.WriteLine('GetWindowRect that bai')
        exit 2
    }
}

$w = $rect.Right - $rect.Left
$ht = $rect.Bottom - $rect.Top
if ($w -le 0 -or $ht -le 0) {
    [Console]::Error.WriteLine(("kich thuoc cua so khong hop le: {0}x{1}" -f $w, $ht))
    exit 2
}

function Resolve-CropRect {
    param([int] $Width, [int] $Height, [string] $Pixels, [string] $Percent)

    if ($Pixels) {
        $p = @($Pixels -split ',' | ForEach-Object { [int]$_.Trim() })
        if ($p.Count -ne 4) { throw 'Crop phai co dang "x,y,w,h"' }
        return New-Object System.Drawing.Rectangle $p[0], $p[1], $p[2], $p[3]
    }

    $f = @($Percent -split ',' | ForEach-Object { [double]$_.Trim() })
    if ($f.Count -ne 4) { throw 'CropPercent phai co dang "x,y,w,h" (0..1)' }
    $cx = [int][math]::Round($f[0] * $Width)
    $cy = [int][math]::Round($f[1] * $Height)
    $cw = [int][math]::Round($f[2] * $Width)
    $ch = [int][math]::Round($f[3] * $Height)
    return New-Object System.Drawing.Rectangle $cx, $cy, $cw, $ch
}

$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bmp.Size)
$g.Dispose()

if ($Crop -or $CropPercent) {
    try {
        $cr = Resolve-CropRect -Width $bmp.Width -Height $bmp.Height -Pixels $Crop -Percent $CropPercent
    }
    catch {
        $bmp.Dispose()
        [Console]::Error.WriteLine($_.Exception.Message)
        exit 2
    }

    if ($cr.X -lt 0 -or $cr.Y -lt 0 -or $cr.Width -lt 1 -or $cr.Height -lt 1 -or
        ($cr.X + $cr.Width) -gt $bmp.Width -or ($cr.Y + $cr.Height) -gt $bmp.Height) {
        $bw = $bmp.Width
        $bh = $bmp.Height
        $bmp.Dispose()
        [Console]::Error.WriteLine(("vung cat {0}x{1}+{2}+{3} nam ngoai anh {4}x{5}" -f `
                    $cr.Width, $cr.Height, $cr.X, $cr.Y, $bw, $bh))
        exit 2
    }

    $cropped = $bmp.Clone($cr, $bmp.PixelFormat)
    $bmp.Dispose()
    $bmp = $cropped
}

$w = $bmp.Width
$ht = $bmp.Height
$bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

$size = [math]::Round((Get-Item -LiteralPath $outPath).Length / 1KB, 1)
if ($ProcessName -and -not $FullScreen) {
    Write-Output ("{0}  {1}x{2}  {3} KB  (cua so: {4})" -f $outPath, $w, $ht, $size, $proc.MainWindowTitle)
}
else {
    Write-Output ("{0}  {1}x{2}  {3} KB  (toan man hinh)" -f $outPath, $w, $ht, $size)
}
exit 0
