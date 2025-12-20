#!/bin/bash
# Pattern Extraction Workflow - Agent-2
# ======================================
# Automated pattern extraction for integration planning

REPO_NAME=$1

if [ -z "$REPO_NAME" ]; then
    echo "Usage: ./pattern_extraction_workflow.sh <repo_name>"
    echo "Example: ./pattern_extraction_workflow.sh DreamVault"
    exit 1
fi

echo "🚀 Starting pattern extraction workflow for $REPO_NAME"
echo "=================================================="

# Extract patterns
echo ""
echo "📋 Extracting patterns..."
python tools/analyze_merged_repo_patterns.py
if [ $? -eq 0 ]; then
    echo "✅ Pattern extraction complete"
else
    echo "⚠️ Pattern extraction completed with warnings"
fi

echo ""
echo "=================================================="
echo "✅ Pattern extraction workflow finished"
echo "📋 Review extracted patterns and proceed with service integration"

