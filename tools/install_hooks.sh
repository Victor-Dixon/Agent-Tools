#!/usr/bin/env bash
set -euo pipefail
HOOK=".git/hooks/pre-commit"
mkdir -p "$(dirname "$HOOK")"
cat > "$HOOK" <<'SH'
#!/usr/bin/env bash
echo "[pre-commit] Running cleanup auditor..."
python tools/audit_cleanup.py
RC=$?
if [ $RC -ne 0 ]; then
  echo "[pre-commit] Auditor blocked the commit (exit $RC). Use 'python tools/audit_cleanup.py --force' and commit consciously if intended."
  exit $RC
fi
exit 0
SH
chmod +x "$HOOK"
echo "Installed pre-commit hook at $HOOK"
