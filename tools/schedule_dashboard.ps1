
# Schedule Dashboard Update (3:15 AM daily)
$action = New-ScheduledTaskAction -Execute 'C:\Users\USER\AppData\Local\Programs\Python\Python311\python.exe' -Argument '"D:\Agent_Cellphone_V2_Repository\tools\project_metrics_to_spreadsheet.py" --output dashboard.csv' -WorkingDirectory 'D:\Agent_Cellphone_V2_Repository'
$trigger = New-ScheduledTaskTrigger -Daily -At 3:15AM
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ProjectDashboardUpdate" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Generate daily project metrics dashboard (Debate + Cycle V2 tasks)"

Write-Host "✅ Scheduled task created:"
Write-Host "   - ProjectDashboardUpdate (3:15 AM daily)"
