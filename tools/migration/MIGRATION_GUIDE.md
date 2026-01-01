# Repository Migration Guide

## Quick Start

Since `github_repo_downloader.py` is working correctly, use it to download all repositories:

### Step 1: Download All Repositories

```bash
# Run github_repo_downloader.py to download all repos
python github_repo_downloader.py \
    --account Victor-Dixon \
    --output-dir /home/dream/Development/projects/repositories/old-account
```

Or if you have it in a different location:

```bash
python /path/to/github_repo_downloader.py \
    --account Victor-Dixon \
    --output-dir /home/dream/Development/projects/repositories/old-account
```

### Step 2: Review Repositories

All repositories will be in:
```
/home/dream/Development/projects/repositories/old-account/
├── repo-name-1/
├── repo-name-2/
└── ...
```

### Step 3: Track Review Status (Optional)

Use the migration helper to track which repos you've reviewed:

```bash
# Initialize tracking
python tools/migration/repo_migration_helper.py \
    --review-dir /home/dream/Development/projects/repositories/old-account \
    --old-account Victor-Dixon

# Mark a repo as reviewed
python tools/migration/repo_migration_helper.py \
    --review-dir /home/dream/Development/projects/repositories/old-account \
    --mark-status "repo-name" "reviewing" "Checking for secrets"

# Mark as ready for publication
python tools/migration/repo_migration_helper.py \
    --review-dir /home/dream/Development/projects/repositories/old-account \
    --mark-ready "repo-name"

# See what's ready
python tools/migration/repo_migration_helper.py \
    --review-dir /home/dream/Development/projects/repositories/old-account \
    --ready
```

### Step 4: When Ready to Publish

```bash
# Generate publish script
python tools/migration/repo_migration_helper.py \
    --review-dir /home/dream/Development/projects/repositories/old-account \
    --generate-publish-script

# Review and edit publish_ready_repos.sh, then run
```

## Using the Wrapper Script

If `github_repo_downloader.py` is in this repository:

```bash
python tools/migration/migrate_with_downloader.py \
    --account Victor-Dixon \
    --target-dir /home/dream/Development/projects/repositories/old-account
```

If it's elsewhere:

```bash
python tools/migration/migrate_with_downloader.py \
    --account Victor-Dixon \
    --target-dir /home/dream/Development/projects/repositories/old-account \
    --downloader-path /path/to/github_repo_downloader.py
```

## What Happens

1. ✅ All repos are cloned locally (no push to new account)
2. ✅ Old remotes are removed (prevents accidental pushes)
3. ✅ Repos are ready for review
4. ✅ You control what gets published and when

## Notes

- All repositories stay local until you're ready
- Review each repo before marking as ready
- The publish script is generated but not executed automatically
- You have full control over the process


