<#
.SYNOPSIS
    Cắt ảnh PNG để chỉ còn phần cần thiết (dùng cho ảnh chèn vào báo cáo otchet).

.DESCRIPTION
    Ba chế độ:
      -Crop "x,y,w,h"          cắt theo pixel tuyệt đối
      -CropPercent "x,y,w,h"   cắt theo tỉ lệ 0..1 của ảnh
      -AutoTrim                tự tìm vùng có nội dung (bỏ viền đồng màu: trắng/đen/xám)
    Có thể kết hợp -AutoTrim với -CropPercent: auto-trim trước, rồi cắt theo tỉ lệ.
    Không gọi mạng. Ghi đè -Out nếu đã có.

.PARAMETER Path
    File PNG nguồn.

.PARAMETER Out
    File PNG kết quả. Mặc định: cùng thư mục, hậu tố `_crop`.

.PARAMETER Crop
    "x,y,w,h" theo pixel.

.PARAMETER CropPercent
    "x,y,w,h" theo tỉ lệ 0..1 của ảnh (sau auto-trim nếu có).

.PARAMETER AutoTrim
    Tự cắt viền đồng màu.

.PARAMETER Padding
    Số pixel chừa lại quanh vùng nội dung khi AutoTrim. Mặc định 8.

.PARAMETER Tolerance
    Ngưỡng khác màu (tổng |dR|+|dG|+|dB|) để coi là "có nội dung". Mặc định 24.

.EXAMPLE
    .\crop_image.ps1 -Path .\images\01_raw.png -CropPercent "0.02,0.08,0.70,0.40" -Out .\images\01_run.png

.EXAMPLE
    .\crop_image.ps1 -Path .\images\02_raw.png -AutoTrim -Out .\images\02_plot.png
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Path,

    [string] $Out,

    [string] $Crop,

    [string] $CropPercent,

    [switch] $AutoTrim,

    [int] $Padding = 8,

    [int] $Tolerance = 24
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing
# Windows PowerShell 5.1 exposes System.Drawing; PowerShell 7 needs System.Drawing.Common
# plus System.Drawing.Primitives (Rectangle lives there).
$drawingRef = if ($PSVersionTable.PSEdition -eq 'Core') { @('System.Drawing.Common', 'System.Drawing.Primitives') } else { @('System.Drawing') }
Add-Type -ReferencedAssemblies $drawingRef @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public class OtchetTrim {
    public static int[] ContentBounds(Bitmap bmp, int tolerance) {
        int w = bmp.Width, h = bmp.Height;
        BitmapData data = bmp.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
        int stride = data.Stride;
        byte[] buf = new byte[stride * h];
        Marshal.Copy(data.Scan0, buf, 0, buf.Length);
        bmp.UnlockBits(data);

        int[] xs = { 0, w - 1 };
        int[] ys = { 0, h - 1 };
        int rr = 0, gg = 0, bb = 0;
        foreach (int yy in ys) {
            foreach (int xx in xs) {
                int o = yy * stride + xx * 4;
                bb += buf[o]; gg += buf[o + 1]; rr += buf[o + 2];
            }
        }
        rr /= 4; gg /= 4; bb /= 4;

        int minX = w, minY = h, maxX = -1, maxY = -1;
        for (int y = 0; y < h; y++) {
            int row = y * stride;
            for (int x = 0; x < w; x++) {
                int o = row + x * 4;
                int d = Math.Abs(buf[o + 2] - rr) + Math.Abs(buf[o + 1] - gg) + Math.Abs(buf[o] - bb);
                if (d > tolerance) {
                    if (x < minX) minX = x;
                    if (x > maxX) maxX = x;
                    if (y < minY) minY = y;
                    if (y > maxY) maxY = y;
                }
            }
        }
        if (maxX < 0) return new int[] { 0, 0, w, h };
        return new int[] { minX, minY, maxX - minX + 1, maxY - minY + 1 };
    }
}
'@

$srcPath = [System.IO.Path]::GetFullPath($Path)
if (-not (Test-Path -LiteralPath $srcPath)) {
    [Console]::Error.WriteLine("khong thay file: $srcPath")
    exit 2
}

if (-not $Out) {
    $dir = [System.IO.Path]::GetDirectoryName($srcPath)
    $base = [System.IO.Path]::GetFileNameWithoutExtension($srcPath)
    $Out = Join-Path $dir ($base + '_crop.png')
}
$outPath = [System.IO.Path]::GetFullPath($Out)
$outDir = [System.IO.Path]::GetDirectoryName($outPath)
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

function Resolve-Rect {
    param([int] $Width, [int] $Height, [string] $Pixels, [string] $Percent)

    if ($Pixels) {
        $p = @($Pixels -split ',' | ForEach-Object { [int]$_.Trim() })
        if ($p.Count -ne 4) { throw 'Crop phai co dang "x,y,w,h"' }
        return New-Object System.Drawing.Rectangle $p[0], $p[1], $p[2], $p[3]
    }

    $f = @($Percent -split ',' | ForEach-Object { [double]$_.Trim() })
    if ($f.Count -ne 4) { throw 'CropPercent phai co dang "x,y,w,h" (0..1)' }
    $rx = [int][math]::Round($f[0] * $Width)
    $ry = [int][math]::Round($f[1] * $Height)
    $rw = [int][math]::Round($f[2] * $Width)
    $rh = [int][math]::Round($f[3] * $Height)
    return New-Object System.Drawing.Rectangle $rx, $ry, $rw, $rh
}

$bmp = [System.Drawing.Bitmap]::FromFile($srcPath)
try {
    $origW = $bmp.Width
    $origH = $bmp.Height

    if ($AutoTrim) {
        $b = [OtchetTrim]::ContentBounds($bmp, $Tolerance)
        $tx = [math]::Max(0, $b[0] - $Padding)
        $ty = [math]::Max(0, $b[1] - $Padding)
        $tw = [math]::Min($bmp.Width - $tx, $b[2] + 2 * $Padding)
        $th = [math]::Min($bmp.Height - $ty, $b[3] + 2 * $Padding)
        $trim = New-Object System.Drawing.Rectangle $tx, $ty, $tw, $th
        $tmp = $bmp.Clone($trim, $bmp.PixelFormat)
        $bmp.Dispose()
        $bmp = $tmp
    }

    $rect = $null
    if ($Crop -or $CropPercent) {
        try {
            $rect = Resolve-Rect -Width $bmp.Width -Height $bmp.Height -Pixels $Crop -Percent $CropPercent
        }
        catch {
            [Console]::Error.WriteLine($_.Exception.Message)
            exit 2
        }

        if ($rect.X -lt 0 -or $rect.Y -lt 0 -or $rect.Width -lt 1 -or $rect.Height -lt 1 -or
            ($rect.X + $rect.Width) -gt $bmp.Width -or ($rect.Y + $rect.Height) -gt $bmp.Height) {
            [Console]::Error.WriteLine(("vung cat {0}x{1}+{2}+{3} nam ngoai anh {4}x{5}" -f `
                        $rect.Width, $rect.Height, $rect.X, $rect.Y, $bmp.Width, $bmp.Height))
            exit 2
        }

        $cut = $bmp.Clone($rect, $bmp.PixelFormat)
        $bmp.Dispose()
        $bmp = $cut
    }

    if (-not $AutoTrim -and -not $rect) {
        [Console]::Error.WriteLine('khong co thao tac nao: dung -AutoTrim / -Crop / -CropPercent')
        exit 2
    }

    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $finalW = $bmp.Width
    $finalH = $bmp.Height
}
finally {
    $bmp.Dispose()
}

$kb = [math]::Round((Get-Item -LiteralPath $outPath).Length / 1KB, 1)
Write-Output ("{0}  {1}x{2} -> {3}x{4}  {5} KB" -f $outPath, $origW, $origH, $finalW, $finalH, $kb)
exit 0
