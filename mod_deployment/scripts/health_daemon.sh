#!/bin/bash
# Health Daemon Script
# ====================
#
# Background process that monitors server health
# and can trigger auto-rollback if issues detected

GAME_PATH="${GAME_PATH:-/app}"
CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-60}"
MAX_FAILURES="${MAX_HEALTH_FAILURES:-3}"
AUTO_ROLLBACK="${AUTO_ROLLBACK_ON_FAILURE:-false}"

log() {
    echo "[HEALTH-DAEMON $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

consecutive_failures=0

monitor_health() {
    while true; do
        if /app/scripts/health_check.sh > /dev/null 2>&1; then
            consecutive_failures=0
        else
            ((consecutive_failures++))
            log "Health check failed (consecutive: $consecutive_failures)"
            
            if [ $consecutive_failures -ge $MAX_FAILURES ]; then
                log "Max failures reached!"
                
                if [ "$AUTO_ROLLBACK" = "true" ]; then
                    log "Triggering auto-rollback..."
                    /app/scripts/rollback.sh
                    consecutive_failures=0
                fi
            fi
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

log "Starting health daemon (interval: ${CHECK_INTERVAL}s, max_failures: $MAX_FAILURES)"
monitor_health
