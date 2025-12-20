# Start Message Queue and Discord Bot in Background
# ===================================================

$projectRoot = Get-Location

Write-Host "Starting Message Queue Processor and Discord Bot in background..." -ForegroundColor Green

# Start Message Queue Processor
Write-Host ""
Write-Host "Starting Message Queue Processor..." -ForegroundColor Cyan
$mqJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    python tools/start_message_queue_processor.py
} -Name "MessageQueueProcessor"

Write-Host "   Message Queue Processor started (Job ID: $($mqJob.Id))" -ForegroundColor Green

# Start Discord Bot
Write-Host ""
Write-Host "Starting Discord Bot..." -ForegroundColor Cyan
$discordJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    python tools/run_unified_discord_bot_with_restart.py
} -Name "DiscordBot"

Write-Host "   Discord Bot started (Job ID: $($discordJob.Id))" -ForegroundColor Green

Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Yellow
Write-Host "Both services started in background!" -ForegroundColor Green
Write-Host ""
Write-Host "To check status:" -ForegroundColor Yellow
Write-Host "   Get-Job" -ForegroundColor White
Write-Host ""
Write-Host "To view output:" -ForegroundColor Yellow
Write-Host "   Receive-Job -Name MessageQueueProcessor" -ForegroundColor White
Write-Host "   Receive-Job -Name DiscordBot" -ForegroundColor White
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "   Stop-Job -Name MessageQueueProcessor" -ForegroundColor White
Write-Host "   Stop-Job -Name DiscordBot" -ForegroundColor White
Write-Host "   Remove-Job -Name MessageQueueProcessor,DiscordBot" -ForegroundColor White
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Yellow

# Show initial status
Start-Sleep -Seconds 2
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
Get-Job | Format-Table Id, Name, State, HasMoreData

