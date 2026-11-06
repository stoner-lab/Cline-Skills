<#
.SYNOPSIS
    Quét prompt injection cục bộ, offline (không gọi mạng, không gửi dữ liệu đi đâu).

.DESCRIPTION
    Chạy TRƯỚC khi đưa nội dung từ nguồn không tin (file tải về, docx->txt, output lệnh,
    trang web đã lưu) vào context của agent.

    Đây là lớp phòng thủ MỀM: nó không chặn được agent nếu agent không gọi nó.
    Nó KHÔNG thay thế sandbox / approval / quyền OS.

    Exit code:  0 = CLEAN   1 = REVIEW   2 = QUARANTINE
    Output:     text (mặc định) hoặc JSON (-Json)
    Log:        JSONL append vào -LogPath (mặc định ~\.cline\data\logs\injection-scan.jsonl)

.PARAMETER Path
    Một hoặc nhiều file / thư mục. Thư mục chỉ được quét khi có -Recurse.

.EXAMPLE
    .\scan_injection.ps1 -Path 'E:\Private\_inbox\bai-giang.md'

.EXAMPLE
    Get-Content .\output.log -Raw | .\scan_injection.ps1 -Text
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0, ValueFromPipeline, ValueFromPipelineByPropertyName)]
    [string[]] $Path,

    [Parameter()]
    [string] $Text,

    [switch] $Recurse,

    [switch] $Json,

    [string] $LogPath = (Join-Path $env:USERPROFILE '.cline\data\logs\injection-scan.jsonl'),

    [int] $MaxBytes = 4000000
)

begin {
    $ErrorActionPreference = 'Stop'
    $script:Hits = New-Object System.Collections.ArrayList

    # ---- Bộ luật (offline, không phụ thuộc dịch vụ ngoài) -------------------
    $script:Rules = @(
        # ra lệnh cho model bỏ qua chỉ dẫn cũ
        @{ Id = 'II-001'; Cat = 'instruction_injection'; W = 0.60; Re = '(?i)\b(ignore|disregard|forget)\s+(all\s+|any\s+)?(of\s+)?(the\s+|your\s+)?(previous|prior|above|earlier)\s+(instruction|prompt|rule|message|context|direction)s?' }
        @{ Id = 'II-002'; Cat = 'instruction_injection'; W = 0.60; Re = '(?i)\b(new|updated|real)\s+(system\s+)?(instruction|prompt|rule)s?\s*[:=]' }
        @{ Id = 'II-003'; Cat = 'instruction_injection'; W = 0.55; Re = '(?i)\bfrom\s+now\s+on\s+you\s+(will|must|are)' }
        @{ Id = 'II-004'; Cat = 'instruction_injection'; W = 0.50; Re = '(?i)\b(ai|assistant|agent|llm|claude|cline|model)\s*[:,-]\s*(do|run|execute|write|delete)\b' }

        # giả mạo system prompt / token đặc biệt của chat template
        @{ Id = 'SO-001'; Cat = 'system_override'; W = 0.80; Re = '<\|(im_start|im_end|system|user|assistant|endoftext)\|>' }
        @{ Id = 'SO-002'; Cat = 'system_override'; W = 0.75; Re = '\[/?INST\]|<<SYS>>|<</SYS>>|<\|start_header_id\|>' }
        @{ Id = 'SO-003'; Cat = 'system_override'; W = 0.70; Re = '(?i)<\s*system\s*>|</\s*system\s*>' }
        @{ Id = 'SO-004'; Cat = 'system_override'; W = 0.60; Re = '(?i)begin\s+(system|admin)\s+(prompt|message|mode)' }

        # đổi vai / jailbreak
        @{ Id = 'RH-001'; Cat = 'role_hijack'; W = 0.55; Re = '(?i)\byou\s+are\s+now\s+(a|an|the|my)\b' }
        @{ Id = 'RH-002'; Cat = 'role_hijack'; W = 0.50; Re = '(?i)\bdeveloper\s+mode\b|\bDAN\b|\bjailbreak' }
        @{ Id = 'RH-003'; Cat = 'jailbreak_classic'; W = 0.50; Re = '(?i)\b(no|without)\s+(any\s+)?(restriction|limit|filter|guardrail|ethical)s?\b' }
        @{ Id = 'RH-004'; Cat = 'jailbreak_classic'; W = 0.55; Re = '(?i)\bbypass\s+(your\s+)?(safety|guardrail|rule|restriction|approval)' }

        # đưa dữ liệu ra ngoài
        @{ Id = 'EX-001'; Cat = 'exfiltration'; W = 0.75; Re = '!\[[^\]]{0,120}\]\(\s*https?://[^)\s]{0,200}' }
        @{ Id = 'EX-002'; Cat = 'exfiltration'; W = 0.65; Re = '(?i)\b(curl|wget|iwr|Invoke-WebRequest|Invoke-RestMethod|nc|ncat)\b[^\r\n]{0,120}(https?://|\$\()' }
        @{ Id = 'EX-003'; Cat = 'exfiltration'; W = 0.70; Re = '(?i)\b(send|post|upload|exfiltrat\w*|forward)\b[^\r\n]{0,60}\b(this|the|all|every)\s+(file|files|data|content|contents|key|keys|token|tokens|credential)\b' }
        @{ Id = 'EX-004'; Cat = 'exfiltration'; W = 0.60; Re = '(?i)\b(cat|type|Get-Content)\b[^\r\n]{0,80}(\.ssh|\.aws|\.env|credentials|secrets?\.json|auth\.json|Login Data|moodle-state)' }

        # giả lập lời gọi tool trong nội dung
        @{ Id = 'TA-001'; Cat = 'tool_abuse'; W = 0.70; Re = '(?i)<\s*(function_call|tool_call|tool_use)\b' }
        @{ Id = 'TA-002'; Cat = 'tool_abuse'; W = 0.65; Re = '(?i)"(name|tool)"\s*:\s*"(run_commands|bash|shell|editor|write_file|read_files|execute_command)"' }
        @{ Id = 'TA-003'; Cat = 'tool_abuse'; W = 0.60; Re = '(?i)\b(run|execute|call)\s+the\s+(tool|command|function)\s+(run_commands|bash|shell|editor)\b' }
        @{ Id = 'TA-004'; Cat = 'tool_abuse'; W = 0.50; Re = '(?i)\bapprove\s+(all|every|this)\s+(tool|command|action)s?\b' }

        # kỹ thuật smuggling
        @{ Id = 'SA-001'; Cat = 'schema_attack'; W = 0.60; Re = '(?i)\bopenclaw\b' }
        @{ Id = 'SA-002'; Cat = 'schema_attack'; W = 0.45; Re = '(?i)\bschema\s+(ref|reference|version)\b[^\r\n]{0,40}(tool|call|function)' }
    )

    # ký tự vô hình / tag Unicode (dùng để giấu chỉ thị)
    $script:InvisibleRe = '[\u200B-\u200F\u202A-\u202E\u2060-\u2064\uFEFF]|\uDB40[\uDC00-\uDFFF]'

    $script:BadExt = @('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', '.pdf', '.zip', '.7z', '.rar',
        '.gz', '.exe', '.dll', '.so', '.bin', '.mp3', '.mp4', '.mkv', '.docx', '.xlsx', '.pptx', '.pyc')

    # ---- Hàm phụ -----------------------------------------------------------
    function Add-Hit {
        param([string] $Source, [string] $Id, [string] $Cat, [double] $W, [string] $Evidence, [int] $Line = 0)
        [void] $script:Hits.Add([pscustomobject]@{
                Source = $Source; Rule = $Id; Category = $Cat
                Weight = $W; Line = $Line; Evidence = $Evidence
            })
    }

    function Get-SafeSnippet {
        param([string] $Value, [int] $Max = 90)
        $v = $Value -replace '\s+', ' '
        if ($v.Length -gt $Max) { $v = $v.Substring(0, $Max) + '...' }
        return [regex]::Replace($v, '[A-Za-z0-9+/=]{24,}', '<redacted-b64>')
    }

    function Get-LineOf {
        param([string] $Content, [int] $Index)
        if ($Index -le 0) { return 0 }
        return ([regex]::Matches($Content.Substring(0, $Index), "`n")).Count + 1
    }

    function Test-Text {
        param([string] $Content, [string] $Source)

        foreach ($rule in $script:Rules) {
            foreach ($m in [regex]::Matches($Content, $rule.Re)) {
                Add-Hit -Source $Source -Id $rule.Id -Cat $rule.Cat -W $rule.W `
                    -Evidence (Get-SafeSnippet $m.Value) -Line (Get-LineOf $Content $m.Index)
            }
        }

        $inv = [regex]::Matches($Content, $script:InvisibleRe)
        if ($inv.Count -gt 0) {
            Add-Hit -Source $Source -Id 'INV-001' -Cat 'invisible_text' `
                -W ([math]::Min(0.9, 0.35 + 0.05 * $inv.Count)) `
                -Evidence ("$($inv.Count) ky tu vo hinh/bidi/tag Unicode") `
                -Line (Get-LineOf $Content $inv[0].Index)
        }

        foreach ($b64 in [regex]::Matches($Content, '[A-Za-z0-9+/]{60,}={0,2}')) {
            try {
                $bytes = [Convert]::FromBase64String($b64.Value)
                $decoded = [System.Text.Encoding]::UTF8.GetString($bytes)
            }
            catch { continue }

            if ($decoded -match '[\x20-\x7E]{20,}') {
                foreach ($rule in $script:Rules) {
                    if ($rule.Cat -in @('instruction_injection', 'system_override', 'role_hijack', 'tool_abuse', 'exfiltration') -and
                        $decoded -match $rule.Re) {
                        Add-Hit -Source $Source -Id 'ENC-001' -Cat 'encoding_smuggle' -W 0.70 `
                            -Evidence ('base64 giai ma chua: ' + (Get-SafeSnippet ([regex]::Match($decoded, $rule.Re).Value))) `
                            -Line (Get-LineOf $Content $b64.Index)
                        break
                    }
                }
            }
        }
    }

    function Scan-File {
        param([string] $File)
        $ext = [System.IO.Path]::GetExtension($File).ToLowerInvariant()
        if ($script:BadExt -contains $ext) {
            Add-Hit -Source $File -Id 'SKIP-001' -Cat 'skipped' -W 0.0 -Evidence 'dinh dang nhi phan - hay chuyen sang text truoc khi quet'
            return
        }
        $len = (Get-Item -LiteralPath $File).Length
        if ($len -gt $MaxBytes) {
            Add-Hit -Source $File -Id 'SKIP-002' -Cat 'skipped' -W 0.0 -Evidence ("file qua lon ({0} bytes) - can quet tung phan" -f $len)
            return
        }
        $content = [System.IO.File]::ReadAllText($File)
        if ($content.IndexOf([char]0) -ge 0) {
            Add-Hit -Source $File -Id 'SKIP-001' -Cat 'skipped' -W 0.0 -Evidence 'co byte NUL - coi la nhi phan'
            return
        }
        Test-Text -Content $content -Source $File
    }

    function Get-Verdict {
        param([double] $Score, [bool] $HasCritical)
        if ($HasCritical -or $Score -ge 0.60) { return 'QUARANTINE' }
        if ($Score -ge 0.30) { return 'REVIEW' }
        return 'CLEAN'
    }

    function Show-Report {
        param([string] $Source, [string] $Verdict, [double] $Score, [string[]] $Cats)

        if ($Json) {
            [pscustomobject]@{
                source     = $Source
                verdict    = $Verdict
                score      = [math]::Round($Score, 2)
                categories = $Cats
                hits       = @($script:Hits | Select-Object rule, category, weight, line, evidence)
                ts         = (Get-Date).ToString('o')
            } | ConvertTo-Json -Depth 6 -Compress | Write-Host
            return
        }

        $label = switch ($Verdict) {
            'QUARANTINE' { 'CAN CHAN ' }
            'REVIEW' { 'CAN XEM  ' }
            'SKIP' { 'CHUA QUET' }
            default { 'SACH     ' }
        }
        Write-Host ("[{0}] score={1,-4}  {2}" -f $label, [math]::Round($Score, 2), $Source)
        if ($Cats.Count -gt 0) { Write-Host ("           nhom: {0}" -f ($Cats -join ', ')) }
        if ($Verdict -eq 'SKIP') {
            foreach ($h in ($script:Hits | Where-Object { $_.Category -eq 'skipped' })) {
                Write-Host ("           ! {0}  {1}" -f $h.Rule, $h.Evidence)
            }
        }
        foreach ($h in ($script:Hits | Where-Object { $_.Category -ne 'skipped' } |
                Sort-Object Weight -Descending | Select-Object -First 8)) {
            Write-Host ("           - L{0,-4} {1,-20} {2}  {3}" -f $h.Line, $h.Category, $h.Rule, $h.Evidence)
        }
    }

    function Invoke-Scan {
        param([string[]] $Files, [string] $Inline)

        $targets = @()
        foreach ($f in @($Files)) {
            if (-not $f) { continue }
            if (-not (Test-Path -LiteralPath $f)) { Write-Warning "khong thay: $f"; continue }
            $item = Get-Item -LiteralPath $f
            if ($item.PSIsContainer) {
                if ($Recurse) { $targets += @(Get-ChildItem -LiteralPath $f -Recurse -File | ForEach-Object { $_.FullName }) }
                else { Write-Warning "thu muc can -Recurse: $f" }
            }
            else { $targets += $item.FullName }
        }

        $worst = 0
        $pending = @()
        if ($Inline) { $pending += , @('<inline>', $Inline) }
        foreach ($t in $targets) { $pending += , @($t, $null) }

        if ($pending.Count -eq 0) { Write-Warning 'khong co gi de quet'; return 0 }

        foreach ($item in $pending) {
            $script:Hits = New-Object System.Collections.ArrayList
            if ($item[1] -ne $null) { Test-Text -Content $item[1] -Source $item[0] }
            else { Scan-File -File $item[0] }

            $real = @($script:Hits | Where-Object { $_.Category -ne 'skipped' })
            $score = ($real | Measure-Object -Property Weight -Sum).Sum
            if (-not $score) { $score = 0 }
            $categories = @($real | Select-Object -ExpandProperty Category -Unique)
            $critical = @($real | Where-Object { $_.Weight -ge 0.75 }).Count -gt 0
            $verdict = Get-Verdict -Score $score -HasCritical $critical

            $hasSkip = @($script:Hits | Where-Object { $_.Category -eq 'skipped' }).Count -gt 0
            if ($verdict -eq 'CLEAN' -and $hasSkip) {
                $verdict = 'SKIP'
                if ($worst -lt 1) { $worst = 1 }
            }
            $cats = $categories

            if ($verdict -eq 'QUARANTINE') { $worst = [math]::Max($worst, 2) }
            elseif ($verdict -eq 'REVIEW' -and $worst -lt 2) { $worst = 1 }

            Show-Report -Source $item[0] -Verdict $verdict -Score $score -Cats $cats

            try {
                $dir = Split-Path -Parent $LogPath
                if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
                ([pscustomobject]@{
                        ts = (Get-Date).ToString('o'); source = $item[0]; verdict = $verdict
                        score = [math]::Round($score, 2); cats = $cats
                        rules = @($real | Select-Object -ExpandProperty Rule -Unique)
                    } | ConvertTo-Json -Compress) | Add-Content -LiteralPath $LogPath -Encoding UTF8
            }
            catch { Write-Verbose "khong ghi duoc log: $($_.Exception.Message)" }
        }

        return $worst
    }
}

end {
    if ($Text) { $code = Invoke-Scan -Files @() -Inline $Text }
    else { $code = Invoke-Scan -Files $Path -Inline $null }
    exit ([int] $code)
}
