#!/bin/bash
# Rollback Script
# ===============
#
# Rollback mods to the most recent rollback point

GAME_PATH="${GAME_PATH:-/app}"
ROLLBACK_DIR="$GAME_PATH/rollback_points"

log() {
    echo "[ROLLBACK $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

find_latest_rollback() {
    if [ -d "$ROLLBACK_DIR" ]; then
        ls -t "$ROLLBACK_DIR" | head -1
    fi
}

rollback_to() {
    local rollback_id="$1"
    local rollback_path="$ROLLBACK_DIR/$rollback_id"
    
    if [ ! -d "$rollback_path" ]; then
        log "ERROR: Rollback point not found: $rollback_id"
        return 1
    fi
    
    log "Rolling back to: $rollback_id"
    
    # Backup current state first
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local pre_rollback_backup="$ROLLBACK_DIR/pre_rollback_$timestamp"
    
    if [ -d "$GAME_PATH/BepInEx/plugins" ]; then
        log "Creating pre-rollback backup..."
        cp -r "$GAME_PATH/BepInEx/plugins" "$pre_rollback_backup"
    fi
    
    # Restore plugins
    if [ -d "$rollback_path/plugins" ]; then
        log "Restoring plugins..."
        rm -rf "$GAME_PATH/BepInEx/plugins"
        cp -r "$rollback_path/plugins" "$GAME_PATH/BepInEx/plugins"
    fi
    
    # Restore config
    if [ -d "$rollback_path/config" ]; then
        log "Restoring config..."
        rm -rf "$GAME_PATH/BepInEx/config"
        cp -r "$rollback_path/config" "$GAME_PATH/BepInEx/config"
    fi
    
    log "Rollback complete"
    return 0
}

main() {
    local rollback_id="${1:-}"
    
    if [ -z "$rollback_id" ]; then
        rollback_id=$(find_latest_rollback)
        if [ -z "$rollback_id" ]; then
            log "ERROR: No rollback points available"
            exit 1
        fi
        log "Using latest rollback point: $rollback_id"
    fi
    
    rollback_to "$rollback_id"
}

main "$@"
