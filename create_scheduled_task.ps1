$ErrorActionPreference = "Stop"

# Task configuration
$taskName = "slocator Hourly Sync"
$taskDescription = "Syncs s_locator folder from F: to Google Drive every hour - Silent Mode"
$scriptPath = "F:\git\s_locator\sync.ps1"
$vbsPath = "F:\git\s_locator\run_sync_silent.vbs"

Write-Host "Creating silent scheduled task: $taskName" -ForegroundColor Green
Write-Host "PowerShell script: $scriptPath" -ForegroundColor Yellow
Write-Host "VBScript wrapper: $vbsPath" -ForegroundColor Yellow

try {
    # Check if the sync script exists
    if (!(Test-Path $scriptPath)) {
        throw "Sync script not found at: $scriptPath"
    }

    # Create the VBScript wrapper for silent execution
    $vbsContent = @"
' Silent PowerShell Script Runner for s_locator sync
' Runs the sync script without any visible windows

Dim objShell
Set objShell = CreateObject("WScript.Shell")

' Run PowerShell script completely hidden
objShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""$scriptPath""", 0, False

Set objShell = Nothing
"@

    Write-Host "Creating VBScript wrapper..." -ForegroundColor Green
    Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII

    # Check if task already exists and remove it
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    # Calculate start time (2 minutes from now)
    $startTime = (Get-Date).AddMinutes(2).ToString("yyyy-MM-ddTHH:mm:ss")

    # Create the task XML to run VBScript instead of PowerShell directly
    $taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>$taskDescription</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT1H</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>$startTime</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$env:USERNAME</UserId>
      <LogonType>S4U</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RestartOnFailure>
      <Interval>PT10M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"$vbsPath"</Arguments>
      <WorkingDirectory>F:\git\s_locator</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

    # Register the task using the XML
    Register-ScheduledTask -TaskName $taskName -Xml $taskXml -Force

    Write-Host "`nScheduled task created successfully!" -ForegroundColor Green
    Write-Host "Task details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName"
    Write-Host "  Mode: SILENT (no windows will appear)"
    Write-Host "  First run: $((Get-Date).AddMinutes(2).ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Host "  Frequency: Every 1 hour"
    Write-Host "  PowerShell script: $scriptPath"
    Write-Host "  VBScript wrapper: $vbsPath"

    # Show the task info
    Start-Sleep -Seconds 2  # Give it a moment to register
    $taskInfo = Get-ScheduledTask -TaskName $taskName | Get-ScheduledTaskInfo
    Write-Host "`nTask Status: $($taskInfo.TaskState)" -ForegroundColor Yellow

    Write-Host "`nYou can manage this task using:" -ForegroundColor Cyan
    Write-Host "  Task Scheduler GUI: taskschd.msc"
    Write-Host "  PowerShell commands:"
    Write-Host "    Get-ScheduledTask -TaskName '$taskName'"
    Write-Host "    Start-ScheduledTask -TaskName '$taskName'"
    Write-Host "    Stop-ScheduledTask -TaskName '$taskName'"
    Write-Host "    Disable-ScheduledTask -TaskName '$taskName'"
    Write-Host "    Enable-ScheduledTask -TaskName '$taskName'"
    Write-Host "    Unregister-ScheduledTask -TaskName '$taskName'"

    Write-Host "`nTo test silent execution:" -ForegroundColor Cyan
    Write-Host "  Double-click: $vbsPath"
    Write-Host "  (Should run with no visible windows)"

} catch {
    Write-Host "`nError creating scheduled task:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nMake sure you're running PowerShell as Administrator!" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nSilent scheduled task setup complete!" -ForegroundColor Green
Write-Host "The task will now run completely invisibly every hour." -ForegroundColor Green