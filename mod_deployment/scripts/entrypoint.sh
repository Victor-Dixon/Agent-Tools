#!/bin/bash
# Game Server Entrypoint Script
# ==============================
#
# Handles server startup, mod loading, and graceful shutdown

set -e

GAME_PATH="${GAME_PATH:-/app}"
SERVER_PORT="${SERVER_PORT:-7777}"
ENABLE_HEALTH_CHECK="${ENABLE_HEALTH_CHECK:-true}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Ensure BepInEx structure exists
ensure_bepinex() {
    log "Ensuring BepInEx directory structure..."
    mkdir -p "$GAME_PATH/BepInEx/plugins"
    mkdir -p "$GAME_PATH/BepInEx/patchers"
    mkdir -p "$GAME_PATH/BepInEx/config"
    mkdir -p "$GAME_PATH/BepInEx/core"
    mkdir -p "$GAME_PATH/mod_backups"
    mkdir -p "$GAME_PATH/rollback_points"
}

# Download and install BepInEx if not present
install_bepinex() {
    if [ ! -f "$GAME_PATH/BepInEx/core/BepInEx.dll" ]; then
        log "Installing BepInEx..."
        BEPINEX_VERSION="${BEPINEX_VERSION:-5.4.22}"
        BEPINEX_URL="https://github.com/BepInEx/BepInEx/releases/download/v${BEPINEX_VERSION}/BepInEx_x64_${BEPINEX_VERSION}.zip"
        
        cd /tmp
        wget -q "$BEPINEX_URL" -O bepinex.zip || {
            log "ERROR: Failed to download BepInEx"
            return 1
        }
        
        unzip -o bepinex.zip -d "$GAME_PATH"
        rm bepinex.zip
        log "BepInEx installed successfully"
    else
        log "BepInEx already installed"
    fi
}

# Install game server via SteamCMD (if configured)
install_game() {
    if [ -n "$STEAM_APP_ID" ]; then
        log "Installing/updating game via SteamCMD (App ID: $STEAM_APP_ID)..."
        
        STEAM_AUTH=""
        if [ -n "$STEAM_USERNAME" ] && [ -n "$STEAM_PASSWORD" ]; then
            STEAM_AUTH="+login $STEAM_USERNAME $STEAM_PASSWORD"
        else
            STEAM_AUTH="+login anonymous"
        fi
        
        /steamcmd/steamcmd.sh \
            $STEAM_AUTH \
            +force_install_dir "$GAME_PATH" \
            +app_update "$STEAM_APP_ID" validate \
            +quit
        
        log "Game installation complete"
    fi
}

# Load mods from staging if in staging mode
load_staging_mods() {
    if [ "$STAGING_MODE" = "true" ] && [ -d "/mods/staging" ]; then
        log "Loading staging mods..."
        for mod_zip in /mods/staging/*.zip; do
            if [ -f "$mod_zip" ]; then
                mod_name=$(basename "$mod_zip" .zip)
                log "Installing mod: $mod_name"
                unzip -o "$mod_zip" -d "$GAME_PATH/BepInEx/plugins/$mod_name" 2>/dev/null || true
            fi
        done
    fi
}

# Start health check daemon
start_health_daemon() {
    if [ "$ENABLE_HEALTH_CHECK" = "true" ]; then
        log "Starting health check daemon..."
        /app/scripts/health_daemon.sh &
    fi
}

# Graceful shutdown handler
shutdown_handler() {
    log "Received shutdown signal, stopping server..."
    
    # Kill game server process
    if [ -n "$SERVER_PID" ]; then
        kill -TERM "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    
    log "Server stopped"
    exit 0
}

# Main execution
main() {
    trap shutdown_handler SIGTERM SIGINT SIGQUIT
    
    case "${1:-start}" in
        start)
            log "Starting game server..."
            ensure_bepinex
            install_bepinex
            install_game
            load_staging_mods
            start_health_daemon
            
            # Find and run the game server executable
            if [ -f "$GAME_PATH/start_server.sh" ]; then
                log "Starting server via start_server.sh..."
                cd "$GAME_PATH"
                ./start_server.sh &
                SERVER_PID=$!
            elif [ -f "$GAME_PATH/server.x86_64" ]; then
                log "Starting Unity server..."
                cd "$GAME_PATH"
                ./server.x86_64 -batchmode -nographics &
                SERVER_PID=$!
            else
                log "No server executable found, running in maintenance mode..."
                # Keep container running for manual operations
                tail -f /dev/null &
                SERVER_PID=$!
            fi
            
            wait "$SERVER_PID"
            ;;
        
        shell)
            log "Starting shell..."
            exec /bin/bash
            ;;
        
        install-mod)
            log "Installing mod: $2"
            python3 -c "
import sys
sys.path.insert(0, '/app')
from core.mod_manager import ModManager
manager = ModManager(game_path='$GAME_PATH', game='${GAME:-lethal-company}')
result = manager.install('$2')
print(result.to_dict())
"
            ;;
        
        update-mods)
            log "Checking for mod updates..."
            python3 -c "
import sys
sys.path.insert(0, '/app')
from core.mod_manager import ModManager
manager = ModManager(game_path='$GAME_PATH', game='${GAME:-lethal-company}')
results = manager.update()
for r in results:
    print(r.to_dict())
"
            ;;
        
        *)
            log "Unknown command: $1"
            echo "Usage: $0 {start|shell|install-mod|update-mods}"
            exit 1
            ;;
    esac
}

main "$@"
