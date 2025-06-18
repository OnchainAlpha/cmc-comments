# Run this script as administrator
$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\start_monitor.ps1`"" `
    -WorkingDirectory "$PSScriptRoot"

$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -RestartInterval (New-TimeSpan -Minutes 5) `
    -RestartCount 3 -StartWhenAvailable -AllowStartIfOnBatteries

$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "CryptoAnalysisMonitor" `
    -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force 