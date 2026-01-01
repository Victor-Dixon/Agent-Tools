#!/bin/bash
# Deploy Mod Script
# =================
#
# Deploys a mod with rollback point creation

GAME_PATH="${GAME_PATH:-/app}"
ROLLBACK_DIR="$GAME_PATH/rollback_points"

log() {
    echo "[DEPLOY $(date '+%Y-%m-%d %H:%M:%S')] $1"
}

create_rollback_point() {
    local description="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local rollback_id="rollback_$timestamp"
    local rollback_path="$ROLLBACK_DIR/$rollback_id"
    
    mkdir -p "$rollback_path"
    
    if [ -d "$GAME_PATH/BepInEx/plugins" ]; then
        cp -r "$GAME_PATH/BepInEx/plugins" "$rollback_path/plugins"
    fi
    
    if [ -d "$GAME_PATH/BepInEx/config" ]; then
        cp -r "$GAME_PATH/BepInEx/config" "$rollback_path/config"
    fi
    
    echo "$description" > "$rollback_path/description.txt"
    
    log "Created rollback point: $rollback_id"
    echo "$rollback_id"
}

deploy_mod() {
    local mod_path="$1"
    local mod_name=$(basename "$mod_path" .zip)
    
    if [ ! -f "$mod_path" ]; then
        log "ERROR: Mod file not found: $mod_path"
        return 1
    fi
    
    log "Deploying mod: $mod_name"
    
    # Create rollback point
    create_rollback_point "Before installing $mod_name"
    
    # Install mod
    local target_dir="$GAME_PATH/BepInEx/plugins/$mod_name"
    mkdir -p "$target_dir"
    
    unzip -o "$mod_path" -d "$target_dir" 2>/dev/null
    
    log "Mod deployed: $mod_name"
    return 0
}

main() {
    if [ -z "$1" ]; then
        echo "Usage: $0 <mod_zip_path>"
        exit 1
    fi
    
    deploy_mod "$1"
}

main "$@"
