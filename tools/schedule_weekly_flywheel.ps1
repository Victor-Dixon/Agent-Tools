
# Schedule Weekly Flywheel Report
$action = New-ScheduledTaskAction -Execute 'C:\Users\USER\AppData\Local\Programs\Python\Python311\python.exe' -Argument '"D:\Agent_Cellphone_V2_Repository\tools\run_weekly_dashboard_and_report.py" --agent Agent-4' -WorkingDirectory 'D:\Agent_Cellphone_V2_Repository'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 3:30AM
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "WeeklyFlywheelReport" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Weekly dashboard + metrics + report + cycle planner"

Write-Host "✅ Scheduled task created:"
Write-Host "   - WeeklyFlywheelReport (Sunday at 3:30AM)"
