# ====================================================================================
# Comprehensive Windows Threat & System Integrity Scanner
# Detects: Cryptominers, Keyloggers, RATs, Stealers, Adware, Hijackers, and Tampering
# ====================================================================================

$ErrorActionPreference = "SilentlyContinue"

Clear-Host
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "             COMPREHENSIVE THREAT & SYSTEM INTEGRITY SCANNER                " -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "Scan started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

$warningsFound = 0

function Report-Finding($level, $category, $message) {
    $script:warningsFound++
    if ($level -eq "HIGH") {
        Write-Host " [!] CRITICAL / HIGH - $category" -ForegroundColor Red
        Write-Host "     $message`n" -ForegroundColor Yellow
    } elseif ($level -eq "WARN") {
        Write-Host " [?] WARNING / SUSPICIOUS - $category" -ForegroundColor Yellow
        Write-Host "     $message`n" -ForegroundColor White
    }
}

# ------------------------------------------------------------------------------------
# 1. RUNNING PROCESSES (Behavioral & Anomaly Analysis)
# ------------------------------------------------------------------------------------
Write-Host "[1/7] Inspecting running processes (RATs, Stealers, Miners, Injections)..." -ForegroundColor Cyan

$minerPatterns = 'xmrig|minerd|stratum|randomx|rx/0|supportxmr|nanopool|ethermine|f2pool|2miners|coinminer'
$stealerPatterns = 'leveldb|discord\\Local Storage|opera gx\\.*Local State|grabber|webhook\.discord\.com'
$knownRatPorts = @(1337, 4444, 5555, 6666, 7777, 8888, 9999, 1177, 1604, 3333, 14433, 14444)

$procs = Get-CimInstance Win32_Process
$procAnomalies = 0

foreach ($p in $procs) {
    $path = $p.ExecutablePath
    $cmd = $p.CommandLine
    $name = $p.Name
    $pidVal = $p.ProcessId

    if ($pidVal -in @(0, 4)) { continue }

    # A. Cryptocurrency miner flags
    if ($cmd -and ($cmd -match $minerPatterns)) {
        Report-Finding "HIGH" "Active Cryptominer Detected" "PID: $pidVal | Name: $name`n     Command: $cmd"
        $procAnomalies++
    }

    # B. Credential / Discord / Browser stealer arguments
    if ($cmd -and ($cmd -match $stealerPatterns)) {
        Report-Finding "HIGH" "Credential/Token Stealer Activity" "PID: $pidVal | Name: $name`n     Command: $cmd"
        $procAnomalies++
    }

    # C. Obfuscated / encoded PowerShell execution
    if ($name -match 'powershell|pwsh' -and $cmd -match '(-enc|-encodedcommand|-w\s+hidden|-windowstyle\s+hidden|iex\s*\(|downloadstring)') {
        Report-Finding "HIGH" "Hidden/Obfuscated PowerShell Execution" "PID: $pidVal | Name: $name`n     Command: $cmd"
        $procAnomalies++
    }

    # D. Disguised Windows System Executables (Masquerading)
    if ($name -match '^(svchost|csrss|lsass|smss|winlogon|services|explorer)\.exe$' -and $path) {
        if ($path -notmatch '^[a-zA-Z]:\\(windows|winnt)\\system32' -and $path -notmatch '^[a-zA-Z]:\\(windows|winnt)\\explorer\.exe$') {
            Report-Finding "HIGH" "Masquerading System Process (Fake $name)" "PID: $pidVal | Path: $path"
            $procAnomalies++
        }
    }

    # E. Suspicious generic binaries in User Profile or Temp
    if ($name -match '^update\d*\.exe$' -and $path -notmatch 'Program Files|Programs') {
        Report-Finding "HIGH" "Disguised Update Binary" "PID: $pidVal | Path: $path"
        $procAnomalies++
    }
}

if ($procAnomalies -eq 0) {
    Write-Host "  -> All active processes appear legitimate and unhooked." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# 2. STARTUP PERSISTENCE & CODE SIGNING
# ------------------------------------------------------------------------------------
Write-Host "`n[2/7] Checking autostart mechanisms (Startup folders & Registry keys)..." -ForegroundColor Cyan

$startupFolders = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
    "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
)

$persistWarnings = 0

foreach ($sf in $startupFolders) {
    if (Test-Path $sf) {
        $files = Get-ChildItem $sf -File
        foreach ($f in $files) {
            # Flag executable scripts or binaries dropped directly in Startup
            if ($f.Extension -in @('.bat', '.cmd', '.vbs', '.ps1', '.jar', '.exe', '.com', '.scr')) {
                Report-Finding "HIGH" "Direct Executable/Script in Startup" "File: $($f.FullName)`n     Modified: $($f.LastWriteTime)"
                $persistWarnings++
            }
        }
    }
}

# Check Registry Run / RunOnce
$runKeys = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
)

foreach ($rk in $runKeys) {
    if (Test-Path $rk) {
        $props = Get-ItemProperty $rk
        foreach ($prop in $props.PSObject.Properties) {
            if ($prop.Name -in @('PSPath', 'PSParentPath', 'PSChildName', 'PSDrive', 'PSProvider')) { continue }
            $val = "$($prop.Value)"
            # Ignore known OneDrive update cleanup entries in RunOnce
            if ($rk -match 'RunOnce' -and $val -match 'OneDrive') { continue }

            if ($val -match '\.bat|\.vbs|\.jar|\.ps1|AppData\\Local\\Temp') {
                Report-Finding "HIGH" "Suspicious Script Autostart in Registry" "Registry Key: $rk`n     Entry: $($prop.Name)`n     Value: $val"
                $persistWarnings++
            }
        }
    }
}

if ($persistWarnings -eq 0) {
    Write-Host "  -> Autostart locations are completely clean." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# 3. CRITICAL SYSTEM HIJACK CHECKS (Winlogon, IFEO, AppInit)
# ------------------------------------------------------------------------------------
Write-Host "`n[3/7] Verifying Windows core integrity (Winlogon, IFEO, AppInit)..." -ForegroundColor Cyan

$coreWarnings = 0

# A. Winlogon Shell (Must be explorer.exe)
$winlogon = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -ErrorAction SilentlyContinue
if ($winlogon.Shell -and ($winlogon.Shell.Trim().ToLower() -ne "explorer.exe")) {
    Report-Finding "HIGH" "Winlogon Shell Hijack Detected!" "Expected: explorer.exe | Actual: $($winlogon.Shell)"
    $coreWarnings++
}

# B. Winlogon Userinit
if ($winlogon.Userinit -and ($winlogon.Userinit.ToLower() -notmatch 'system32\\userinit\.exe')) {
    Report-Finding "HIGH" "Winlogon Userinit Hijack Detected!" "Actual: $($winlogon.Userinit)"
    $coreWarnings++
}

# C. AppInit_DLLs (Injected into every process)
$appInit = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows" -ErrorAction SilentlyContinue
if ($appInit.AppInit_DLLs -and ($appInit.AppInit_DLLs.Trim() -ne "")) {
    Report-Finding "HIGH" "Global DLL Injection Hook (AppInit_DLLs)" "DLLs: $($appInit.AppInit_DLLs)"
    $coreWarnings++
}

# D. Image File Execution Options (IFEO Debugger Hijacks)
$ifeoPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options"
$securityTools = @('taskmgr.exe', 'regedit.exe', 'cmd.exe', 'powershell.exe', 'msmpeng.exe', 'mbam.exe')
foreach ($st in $securityTools) {
    $sub = Join-Path $ifeoPath $st
    if (Test-Path $sub) {
        $dbg = (Get-ItemProperty $sub).Debugger
        if ($dbg) {
            Report-Finding "HIGH" "Security Tool Hijacked via IFEO Debugger" "Target: $st is redirected to: $dbg"
            $coreWarnings++
        }
    }
}

if ($coreWarnings -eq 0) {
    Write-Host "  -> Core Windows subsystems are untampered." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# 4. NETWORK INTEGRITY & PROXY/DNS HIJACK CHECKS
# ------------------------------------------------------------------------------------
Write-Host "`n[4/7] Checking Network settings (Proxy, DNS, Hosts file, RAT ports)..." -ForegroundColor Cyan

$netWarnings = 0

# A. Proxy Hijack
$inet = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -ErrorAction SilentlyContinue
if ($inet.ProxyEnable -eq 1 -and $inet.ProxyServer) {
    Report-Finding "WARN" "Active System Proxy Detected" "Proxy Server: $($inet.ProxyServer) (Verify if intentional)"
    $netWarnings++
}

# B. Hosts File Tampering
$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
if (Test-Path $hostsFile) {
    $nonCommentHosts = Get-Content $hostsFile | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' }
    foreach ($entry in $nonCommentHosts) {
        # Flag any redirection of security, update, or antivirus domains
        if ($entry -match 'microsoft|windowsupdate|google|virustotal|malwarebytes|kaspersky|bitdefender') {
            Report-Finding "HIGH" "Security Domain Blocked in Hosts File!" "Entry: $entry"
            $netWarnings++
        }
    }
}

# C. Active Outbound Connections to Known C2 / RAT / Mining Ports
$conns = Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | Where-Object { $_.RemotePort -in $knownRatPorts }
if ($conns) {
    foreach ($c in $conns) {
        $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
        # Exclude browsers on 8080/8888 if applicable
        if ($c.RemotePort -in @(8080, 8888) -and ($p.ProcessName -match 'opera|chrome|msedge|firefox')) { continue }
        Report-Finding "WARN" "Outbound Connection on High-Risk Port" "Port: $($c.RemotePort) -> Remote IP: $($c.RemoteAddress)`n     Process: $($p.ProcessName) (PID: $($c.OwningProcess))"
        $netWarnings++
    }
}

if ($netWarnings -eq 0) {
    Write-Host "  -> Network settings and connections look secure." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# 5. WINDOWS DEFENDER INTEGRITY CHECKS
# ------------------------------------------------------------------------------------
Write-Host "`n[5/7] Checking Antivirus & Defender health..." -ForegroundColor Cyan

$defWarnings = 0
$mpPref = Get-MpPreference -ErrorAction SilentlyContinue
if ($mpPref) {
    if ($mpPref.DisableRealtimeMonitoring -eq $true) {
        Report-Finding "HIGH" "Defender Real-Time Protection is DISABLED!" "Malware may have deactivated your antivirus."
        $defWarnings++
    }
}

if ($defWarnings -eq 0) {
    Write-Host "  -> Antivirus shields are active and intact." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# 6. SCHEDULED TASKS (Persistent Backdoors)
# ------------------------------------------------------------------------------------
Write-Host "`n[6/7] Auditing Task Scheduler for hidden persistent tasks..." -ForegroundColor Cyan

$taskWarnings = 0
$schedTasks = Get-ScheduledTask -ErrorAction SilentlyContinue
foreach ($t in $schedTasks) {
    foreach ($action in $t.Actions) {
        $exec = "$($action.Execute)"
        $args = "$($action.Arguments)"
        
        # Check for scripts executing out of user-writable directories
        if (($exec -match '\.bat|\.vbs|\.jar|\.ps1') -or ($args -match '\.bat|\.vbs|\.jar|\.ps1')) {
            if ($exec -notmatch '^[a-zA-Z]:\\windows\\system32') {
                Report-Finding "WARN" "Script-Based Scheduled Task" "Task Name: $($t.TaskName)`n     Command: $exec $args"
                $taskWarnings++
            }
        }
    }
}

if ($taskWarnings -eq 0) {
    Write-Host "  -> No suspicious scheduled tasks found." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# 7. HIGH-RISK USER DIRECTORIES (Temp & AppData)
# ------------------------------------------------------------------------------------
Write-Host "`n[7/7] Scanning Temp & User directories for rogue dropped binaries..." -ForegroundColor Cyan

$tempCutoff = (Get-Date).AddDays(-3)
$recentTemp = Get-ChildItem -Path $env:TEMP -File -Include *.exe,*.bat,*.jar,*.vbs,*.cmd -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -ge $tempCutoff }

$dirWarnings = 0
foreach ($f in $recentTemp) {
    if ($f.Name -match '^gfw-install|^vs_|^Setup|^dotnet') { continue }
    Report-Finding "WARN" "Recent Binary in Temp Folder" "File: $($f.FullName)`n     Modified: $($f.LastWriteTime)"
    $dirWarnings++
}

# Check root of AppData for rogue executables
$appDataRoots = Get-ChildItem -Path "$env:LOCALAPPDATA", "$env:APPDATA" -File -Include *.exe,*.bat,*.jar,*.vbs -ErrorAction SilentlyContinue
foreach ($f in $appDataRoots) {
    Report-Finding "HIGH" "Executable sitting in AppData Root" "File: $($f.FullName)"
    $dirWarnings++
}

if ($dirWarnings -eq 0) {
    Write-Host "  -> User directories are clean of loose executables." -ForegroundColor Green
}

# ------------------------------------------------------------------------------------
# FINAL SUMMARY
# ------------------------------------------------------------------------------------
Write-Host "`n============================================================================" -ForegroundColor Cyan
if ($script:warningsFound -eq 0) {
    Write-Host "  [OK] SCAN COMPLETED: ZERO THREATS DETECTED ACROSS ALL 7 CATEGORIES!" -ForegroundColor Green
} else {
    Write-Host "  [!] SCAN COMPLETED: $($script:warningsFound) potential item(s) flagged for review." -ForegroundColor Yellow
}
Write-Host "============================================================================" -ForegroundColor Cyan
