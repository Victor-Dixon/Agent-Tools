#!/bin/bash
# Complete Cleanup Workflow - Agent-2
# ====================================
# Automated cleanup workflow for integration preparation

REPO_NAME=$1
REPO_PATH=$2

if [ -z "$REPO_NAME" ]; then
    echo "Usage: ./complete_cleanup_workflow.sh <repo_name> [repo_path]"
    echo "Example: ./complete_cleanup_workflow.sh DreamVault"
    exit 1
fi

if [ -z "$REPO_PATH" ]; then
    REPO_PATH="."
fi

echo "🚀 Starting complete cleanup workflow for $REPO_NAME"
echo "=================================================="

# Step 1: Detect venv files
echo ""
echo "📋 Step 1: Detecting venv files..."
python tools/detect_venv_files.py "$REPO_PATH"
if [ $? -eq 0 ]; then
    echo "✅ Venv detection complete"
else
    echo "⚠️ Venv detection completed with warnings"
fi

# Step 2: Detect duplicates
echo ""
echo "📋 Step 2: Detecting duplicates..."
python tools/enhanced_duplicate_detector.py "$REPO_NAME"
if [ $? -eq 0 ]; then
    echo "✅ Duplicate detection complete"
else
    echo "⚠️ Duplicate detection completed with warnings"
fi

# Step 3: Check integration issues
echo ""
echo "📋 Step 3: Checking integration issues..."
python tools/check_integration_issues.py "$REPO_PATH"
if [ $? -eq 0 ]; then
    echo "✅ Integration issues check complete"
else
    echo "⚠️ Integration issues check completed with warnings"
fi

echo ""
echo "=================================================="
echo "✅ Complete cleanup workflow finished"
echo "📋 Review outputs above and proceed with integration"

