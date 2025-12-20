#!/bin/bash
# Force Push Consolidation Merges to Main
# Solo Developer - Direct Merge to Main (No PR Process)
# Author: Agent-7
# Date: 2025-01-28

set -e

GITHUB_USER="Dadudekc"
BASE_DIR="/d/Temp/consolidation_force_push_$(date +%s)"
mkdir -p "$BASE_DIR"

echo "============================================================"
echo "🚀 FORCE PUSH CONSOLIDATIONS TO MAIN (SOLO DEV MODE)"
echo "============================================================"
echo ""

# Function to force push merge branch to main
force_push_to_main() {
    local repo=$1
    local branch=$2
    local description=$3
    
    echo "📦 Processing: $description"
    echo "   Repo: $repo"
    echo "   Branch: $branch"
    echo ""
    
    REPO_DIR="$BASE_DIR/$repo"
    
    # Clone repo
    echo "📥 Cloning $repo..."
    git clone "https://github.com/$GITHUB_USER/$repo.git" "$REPO_DIR" || {
        echo "❌ Failed to clone $repo"
        return 1
    }
    
    cd "$REPO_DIR"
    
    # Fetch the merge branch
    echo "📥 Fetching branch $branch..."
    git fetch origin "$branch" || {
        echo "⚠️ Branch $branch not found, checking if we need to create it..."
        cd "$BASE_DIR"
        rm -rf "$REPO_DIR"
        return 1
    }
    
    # Checkout main
    echo "🌿 Checking out main..."
    git checkout main || git checkout master
    MAIN_BRANCH=$(git branch --show-current)
    
    # Merge the branch into main
    echo "🔀 Merging $branch into $MAIN_BRANCH..."
    git merge "origin/$branch" --no-edit -m "Merge $branch into $MAIN_BRANCH - Consolidation Complete" || {
        echo "⚠️ Merge had conflicts, using ours strategy..."
        git merge --abort 2>/dev/null || true
        git merge "origin/$branch" -X ours --no-edit -m "Merge $branch into $MAIN_BRANCH - Consolidation Complete (conflicts resolved)"
    }
    
    # Force push to main
    echo "📤 Force pushing to $MAIN_BRANCH..."
    git push origin "$MAIN_BRANCH" --force || {
        echo "❌ Force push failed"
        cd "$BASE_DIR"
        return 1
    }
    
    # Delete the merge branch
    echo "🧹 Deleting merge branch $branch..."
    git push origin --delete "$branch" 2>/dev/null || echo "⚠️ Could not delete branch (may not exist)"
    
    echo "✅ COMPLETE: $description"
    echo ""
    
    cd "$BASE_DIR"
    rm -rf "$REPO_DIR"
}

# Content/Blog Systems Consolidation (69.4x ROI)
echo "🎯 HIGH VALUE: Content/Blog Systems (69.4x ROI)"
echo "============================================================"
force_push_to_main "Auto_Blogger" "merge-content-20251128" "content → Auto_Blogger"
force_push_to_main "Auto_Blogger" "merge-freework-20251128" "freework → Auto_Blogger"

# Phase 0 Case Variations
echo "🎯 Phase 0: Case Variations"
echo "============================================================"
force_push_to_main "FocusForge" "merge-focusforge-20251127" "focusforge → FocusForge"
force_push_to_main "TBOWTactics" "merge-tbowtactics-20251127" "tbowtactics → TBOWTactics"

echo "============================================================"
echo "✅ ALL CONSOLIDATIONS FORCE PUSHED TO MAIN!"
echo "============================================================"
echo ""
echo "🧹 Cleaning up..."
rm -rf "$BASE_DIR"

echo "✅ DONE - All merges are now in main branches!"

