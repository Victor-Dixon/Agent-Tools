#!/bin/bash
# Health Check Script
# ===================
#
# Checks game server health for Docker healthcheck
# Returns 0 if healthy, 1 if unhealthy

GAME_PATH="${GAME_PATH:-/app}"
SERVER_PORT="${SERVER_PORT:-7777}"

# Check if BepInEx is loaded (via log file)
check_bepinex() {
    local log_file="$GAME_PATH/BepInEx/LogOutput.log"
    
    if [ ! -f "$log_file" ]; then
        return 1
    fi
    
    # Check for successful initialization
    if grep -q "Chainloader ready" "$log_file" 2>/dev/null; then
        return 0
    fi
    
    # Check for fatal errors
    if grep -q "FATAL\|Exception" "$log_file" 2>/dev/null; then
        return 1
    fi
    
    return 0
}

# Check if server port is listening
check_port() {
    if command -v nc &> /dev/null; then
        nc -z localhost "$SERVER_PORT" 2>/dev/null
        return $?
    elif command -v ss &> /dev/null; then
        ss -tuln | grep -q ":$SERVER_PORT " 2>/dev/null
        return $?
    else
        # Assume healthy if can't check
        return 0
    fi
}

# Check disk space
check_disk() {
    local min_mb=500
    local available=$(df "$GAME_PATH" | tail -1 | awk '{print $4}')
    
    if [ "$available" -lt $((min_mb * 1024)) ]; then
        return 1
    fi
    
    return 0
}

# Main health check
main() {
    local checks_passed=0
    local checks_failed=0
    
    # BepInEx check
    if check_bepinex; then
        ((checks_passed++))
    else
        ((checks_failed++))
        echo "WARN: BepInEx check failed"
    fi
    
    # Port check (only if server should be running)
    if [ "${ENABLE_PORT_CHECK:-true}" = "true" ]; then
        if check_port; then
            ((checks_passed++))
        else
            ((checks_failed++))
            echo "WARN: Port $SERVER_PORT not responding"
        fi
    fi
    
    # Disk check
    if check_disk; then
        ((checks_passed++))
    else
        ((checks_failed++))
        echo "WARN: Low disk space"
    fi
    
    # Determine overall health
    if [ $checks_failed -eq 0 ]; then
        echo "HEALTHY: $checks_passed checks passed"
        exit 0
    elif [ $checks_failed -lt $checks_passed ]; then
        echo "DEGRADED: $checks_passed passed, $checks_failed failed"
        exit 0
    else
        echo "UNHEALTHY: $checks_passed passed, $checks_failed failed"
        exit 1
    fi
}

main
