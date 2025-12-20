# GitHub Pusher Agent - Background Service Setup
# ===============================================
# Sets up the GitHub Pusher Agent to run as a background service
# on Windows using Task Scheduler

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up GitHub Pusher Agent as background service..." -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$pusherScript = Join-Path $scriptDir "github_pusher_agent.py"
$pythonExe = (Get-Command python).Source

# Verify script exists
if (-not (Test-Path $pusherScript)) {
    Write-Host "❌ Error: github_pusher_agent.py not found at $pusherScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found pusher script: $pusherScript" -ForegroundColor Green
Write-Host "✅ Python executable: $pythonExe" -ForegroundColor Green

# Task Scheduler configuration
$taskName = "GitHubPusherAgent"
$taskDescription = "Processes deferred GitHub push queue every 5 minutes"
$intervalMinutes = 5

# Remove existing task if it exists
Write-Host "`n🧹 Removing existing task (if any)..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ Removed existing task" -ForegroundColor Green
}

# Create task action
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "-u `"$pusherScript`"" -WorkingDirectory $projectRoot

# Create trigger (every 5 minutes, starting now)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $intervalMinutes) -RepetitionDuration (New-TimeSpan -Days 365)

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Register task
Write-Host "`n📋 Creating scheduled task..." -ForegroundColor Yellow
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription | Out-Null
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creating task: $_" -ForegroundColor Red
    exit 1
}

# Start task
Write-Host "`n🚀 Starting task..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName $taskName
    Write-Host "✅ Task started!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Could not start task automatically. Start manually with:" -ForegroundColor Yellow
    Write-Host "   Start-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
}

# Display task info
Write-Host "`n📊 Task Information:" -ForegroundColor Cyan
$task = Get-ScheduledTask -TaskName $taskName
Write-Host "   Name: $($task.TaskName)" -ForegroundColor White
Write-Host "   State: $($task.State)" -ForegroundColor White
Write-Host "   Interval: Every $intervalMinutes minutes" -ForegroundColor White
Write-Host "   Script: $pusherScript" -ForegroundColor White

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`n📝 Useful commands:" -ForegroundColor Cyan
Write-Host "   View task: Get-ScheduledTask -TaskName $taskName" -ForegroundColor White
Write-Host "   Start task: Start-ScheduledTask -TaskName $taskName" -ForegroundColor White
Write-Host "   Stop task: Stop-ScheduledTask -TaskName $taskName" -ForegroundColor White
Write-Host "   Remove task: Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false" -ForegroundColor White
Write-Host "   View task history: Get-WinEvent -LogName Microsoft-Windows-TaskScheduler/Operational | Where-Object {`$_.Message -like `"*$taskName*`"}" -ForegroundColor White

# ===============================================
# Sets up the GitHub Pusher Agent to run as a background service
# on Windows using Task Scheduler

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up GitHub Pusher Agent as background service..." -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$pusherScript = Join-Path $scriptDir "github_pusher_agent.py"
$pythonExe = (Get-Command python).Source

# Verify script exists
if (-not (Test-Path $pusherScript)) {
    Write-Host "❌ Error: github_pusher_agent.py not found at $pusherScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found pusher script: $pusherScript" -ForegroundColor Green
Write-Host "✅ Python executable: $pythonExe" -ForegroundColor Green

# Task Scheduler configuration
$taskName = "GitHubPusherAgent"
$taskDescription = "Processes deferred GitHub push queue every 5 minutes"
$intervalMinutes = 5

# Remove existing task if it exists
Write-Host "`n🧹 Removing existing task (if any)..." -ForegroundColor Yellow
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "✅ Removed existing task" -ForegroundColor Green
}

# Create task action
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "-u `"$pusherScript`"" -WorkingDirectory $projectRoot

# Create trigger (every 5 minutes, starting now)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $intervalMinutes) -RepetitionDuration (New-TimeSpan -Days 365)

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Register task
Write-Host "`n📋 Creating scheduled task..." -ForegroundColor Yellow
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription | Out-Null
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creating task: $_" -ForegroundColor Red
    exit 1
}

# Start task
Write-Host "`n🚀 Starting task..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName $taskName
    Write-Host "✅ Task started!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Could not start task automatically. Start manually with:" -ForegroundColor Yellow
    Write-Host "   Start-ScheduledTask -TaskName $taskName" -ForegroundColor Yellow
}

# Display task info
Write-Host "`n📊 Task Information:" -ForegroundColor Cyan
$task = Get-ScheduledTask -TaskName $taskName
Write-Host "   Name: $($task.TaskName)" -ForegroundColor White
Write-Host "   State: $($task.State)" -ForegroundColor White
Write-Host "   Interval: Every $intervalMinutes minutes" -ForegroundColor White
Write-Host "   Script: $pusherScript" -ForegroundColor White

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`n📝 Useful commands:" -ForegroundColor Cyan
Write-Host "   View task: Get-ScheduledTask -TaskName $taskName" -ForegroundColor White
Write-Host "   Start task: Start-ScheduledTask -TaskName $taskName" -ForegroundColor White
Write-Host "   Stop task: Stop-ScheduledTask -TaskName $taskName" -ForegroundColor White
Write-Host "   Remove task: Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false" -ForegroundColor White
Write-Host "   View task history: Get-WinEvent -LogName Microsoft-Windows-TaskScheduler/Operational | Where-Object {`$_.Message -like `"*$taskName*`"}" -ForegroundColor White

