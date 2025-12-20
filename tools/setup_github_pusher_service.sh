#!/bin/bash
# GitHub Pusher Agent - Background Service Setup (Linux/Mac)
# ===========================================================
# Sets up the GitHub Pusher Agent to run as a cron job

set -e

echo "🚀 Setting up GitHub Pusher Agent as background service..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PUSHER_SCRIPT="$SCRIPT_DIR/github_pusher_agent.py"
PYTHON_EXE=$(which python3 || which python)

# Verify script exists
if [ ! -f "$PUSHER_SCRIPT" ]; then
    echo "❌ Error: github_pusher_agent.py not found at $PUSHER_SCRIPT"
    exit 1
fi

echo "✅ Found pusher script: $PUSHER_SCRIPT"
echo "✅ Python executable: $PYTHON_EXE"

# Create log directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/github_pusher_agent.log"

# Cron job configuration (every 5 minutes)
CRON_SCHEDULE="*/5 * * * *"
CRON_COMMAND="cd $PROJECT_ROOT && $PYTHON_EXE -u $PUSHER_SCRIPT --once --max-items 10 >> $LOG_FILE 2>&1"

# Create temporary cron file
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null | grep -v "github_pusher_agent.py" > "$TEMP_CRON" || true

# Add new cron job
echo "$CRON_SCHEDULE $CRON_COMMAND # GitHub Pusher Agent" >> "$TEMP_CRON"

# Install cron job
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Cron job installed!"
echo ""
echo "📊 Cron Job Information:"
echo "   Schedule: Every 5 minutes"
echo "   Script: $PUSHER_SCRIPT"
echo "   Log: $LOG_FILE"
echo ""
echo "📝 Useful commands:"
echo "   View cron jobs: crontab -l"
echo "   Edit cron jobs: crontab -e"
echo "   View logs: tail -f $LOG_FILE"
echo "   Remove cron job: crontab -l | grep -v 'github_pusher_agent.py' | crontab -"

# GitHub Pusher Agent - Background Service Setup (Linux/Mac)
# ===========================================================
# Sets up the GitHub Pusher Agent to run as a cron job

set -e

echo "🚀 Setting up GitHub Pusher Agent as background service..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PUSHER_SCRIPT="$SCRIPT_DIR/github_pusher_agent.py"
PYTHON_EXE=$(which python3 || which python)

# Verify script exists
if [ ! -f "$PUSHER_SCRIPT" ]; then
    echo "❌ Error: github_pusher_agent.py not found at $PUSHER_SCRIPT"
    exit 1
fi

echo "✅ Found pusher script: $PUSHER_SCRIPT"
echo "✅ Python executable: $PYTHON_EXE"

# Create log directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/github_pusher_agent.log"

# Cron job configuration (every 5 minutes)
CRON_SCHEDULE="*/5 * * * *"
CRON_COMMAND="cd $PROJECT_ROOT && $PYTHON_EXE -u $PUSHER_SCRIPT --once --max-items 10 >> $LOG_FILE 2>&1"

# Create temporary cron file
TEMP_CRON=$(mktemp)
crontab -l 2>/dev/null | grep -v "github_pusher_agent.py" > "$TEMP_CRON" || true

# Add new cron job
echo "$CRON_SCHEDULE $CRON_COMMAND # GitHub Pusher Agent" >> "$TEMP_CRON"

# Install cron job
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Cron job installed!"
echo ""
echo "📊 Cron Job Information:"
echo "   Schedule: Every 5 minutes"
echo "   Script: $PUSHER_SCRIPT"
echo "   Log: $LOG_FILE"
echo ""
echo "📝 Useful commands:"
echo "   View cron jobs: crontab -l"
echo "   Edit cron jobs: crontab -e"
echo "   View logs: tail -f $LOG_FILE"
echo "   Remove cron job: crontab -l | grep -v 'github_pusher_agent.py' | crontab -"

