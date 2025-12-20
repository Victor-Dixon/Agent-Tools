#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-conservative}"  # conservative|moderate|aggressive
DRY="${DRY_RUN:-0}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_ROOT="${BACKUP_ROOT:-backups/cleanup}"
BACKUP_DIR="$BACKUP_ROOT/$STAMP"
MANIFEST="$BACKUP_DIR/manifest.json"
mkdir -p "$BACKUP_DIR"
MANIFEST_ARR=()

move_safe() {
  local src="$1"; [ -e "$src" ] || return 0
  local dst="$BACKUP_DIR/$src"; mkdir -p "$(dirname "$dst")"
  if [ "$DRY" = "1" ]; then echo "[DRY] MOVE $src -> $dst"
  else mv -f "$src" "$dst"; fi
  MANIFEST_ARR+=("{\"action\":\"move\",\"src\":\"$src\",\"dst\":\"$dst\"}")
}
rm_safe() {
  local src="$1"; [ -e "$src" ] || return 0
  if [ "$DRY" = "1" ]; then echo "[DRY] DELETE $src"
  else rm -rf "$src"; fi
  MANIFEST_ARR+=("{\"action\":\"delete\",\"src\":\"$src\"}")
}

# 1) Debug/Temp
rm_safe "debug_imports.py"
rm_safe "fix_manager_results.py"

# 2) Agent inbox messages → move
while IFS= read -r -d '' inbox; do
  while IFS= read -r -d '' f; do move_safe "$f"; done < <(find "$inbox" -mindepth 1 -maxdepth 1 -print0)
done < <(find agent_workspaces agents -type d -name inbox -print0 2>/dev/null || true)

# 3) Old system logs
rm_safe "logs/messaging_20250903.log"
rm_safe "logs/messaging_coordination_20250903.log"

# 4) Runtime reports (moderate+)
if [[ "$MODE" == "moderate" || "$MODE" == "aggressive" ]]; then
  ls -t runtime/reports/cleanup_* 2>/dev/null | tail -n +4 | while read -r f; do move_safe "$f"; done || true
fi

# 5) Archive dir (aggressive)
if [[ "$MODE" == "aggressive" && -d "archive" ]]; then
  mkdir -p "devlogs/archive"
  shopt -s dotglob nullglob
  for f in archive/*; do move_safe "$f"; done
  [ "$DRY" = "1" ] || rmdir archive || true
fi

# 6) Devlogs older than 14d (aggressive)
if [[ "$MODE" == "aggressive" ]]; then
  mkdir -p "devlogs/archive/old_logs_$STAMP"
  find devlogs -name "*.md" -type f -mtime +14 -print0 2>/dev/null | while IFS= read -r -d '' f; do move_safe "$f"; done
fi

# Manifest
printf '[\n%s\n]\n' "$(IFS=,; echo "${MANIFEST_ARR[*]:-}")" > "$MANIFEST"
echo "✅ Cleanup ($Mode) complete. Backup: $BACKUP_DIR"
echo "📄 Manifest: $MANIFEST"
[ "$DRY" = "1" ] && echo "ℹ️ DRY-RUN only — no changes were made."
