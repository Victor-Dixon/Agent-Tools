# Wishlist Tool: WP SFTP One-Shot with Dependency Check

## Problem
Manual WordPress theme deployments fail when host dependencies (e.g., `pysftp/paramiko`) are missing, or when SFTP connectivity/paths aren’t validated before upload. Cache flush remains manual, and there’s no structured receipt.

## Desired capabilities
- **Dependency guard**: verify/install `pysftp` (or paramiko) before running.
- **Connectivity probe**: test SFTP auth and target path writability.
- **One-shot upload**: zip theme folder, upload, and unpack with checksum verification.
- **Backup & receipt**: auto-backup existing theme and emit JSON receipt (files, checksums, timestamps).
- **Cache flush hook**: optional HTTP call to trigger WP permalink save or cache purge endpoint.
- **Post-verify**: fetch home page, diff critical selectors (hero, menu, key strings) to confirm new assets served.

## Minimal interface (CLI)
```
python -m wp_sftp_deploy \
  --host HOST --user USER --password PASS --remote-path /path/to/theme \
  --theme-dir ./FreeRideInvestor_V2 \
  --flush-url https://freerideinvestor.com/wp-admin/options-permalink.php \
  --receipt ./receipts/freerideinvestor.json
```

## Deliverables
- Python module + CLI wrapper
- Structured logs + receipt JSON
- Optional Discord webhook notifier for success/failure

