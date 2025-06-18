# Set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

# Start the monitor script
while ($true) {
    Write-Host "`nStarting Crypto Analysis Monitor..."
    Write-Host "Press Ctrl+C to stop`n"
    
    try {
        # Run the monitor
        python -m scripts.continuous_monitor
    }
    catch {
        Write-Host "Error: $_"
    }
    
    Write-Host "`nMonitor stopped or crashed. Restarting in 5 minutes..."
    Start-Sleep -Seconds 300
} 