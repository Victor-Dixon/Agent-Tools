# Repository Migration Helper

Tools for migrating repositories from an old GitHub account to local storage for review before publishing.

## Workflow

1. **Clone Locally** - Get all repos off the old account (no push to new account)
2. **Review** - Review each repo, mark status, add notes
3. **Mark Ready** - Mark repos as ready for publication when they're production-ready
4. **Publish** - Generate and run publish script when ready

## Usage

### 1. Create a repository list

Create a file `repos.txt` with one repository per line:

```
repo-name-1
repo-name-2
https://github.com/old-account/repo-name-3.git
```

### 2. Clone all repositories locally

```bash
python tools/migration/repo_migration_helper.py \
    --clone-list repos.txt \
    --old-account your-old-account \
    --review-dir ~/repo_review
```

### 3. Review repositories

Check status:
```bash
python tools/migration/repo_migration_helper.py --status
```

Update review status:
```bash
# Mark as reviewing
python tools/migration/repo_migration_helper.py \
    --mark-status "repo-name" "reviewing" "Checking for sensitive data"

# Mark as needs work
python tools/migration/repo_migration_helper.py \
    --mark-status "repo-name" "needs-work" "Needs README update"

# Mark as ready
python tools/migration/repo_migration_helper.py \
    --mark-ready "repo-name"
```

### 4. List ready repositories

```bash
python tools/migration/repo_migration_helper.py --ready
```

### 5. Generate publish script

```bash
python tools/migration/repo_migration_helper.py --generate-publish-script
```

This creates `publish_ready_repos.sh` that you can review and run when ready.

## Review Status Values

- `pending` - Not yet reviewed
- `reviewing` - Currently being reviewed
- `needs-work` - Needs updates before publication
- `ready` - Ready for publication
- `archived` - Not publishing (keep local only)

## Directory Structure

```
~/repo_review/
├── migration_status.json    # Tracks review status
├── repo-name-1/            # Cloned repository
├── repo-name-2/
└── ...
```

## Example Workflow

```bash
# 1. Clone everything
python tools/migration/repo_migration_helper.py \
    --clone-list my_repos.txt \
    --old-account old-account

# 2. Review each repo manually
cd ~/repo_review/repo-name-1
# ... review code, check for secrets, update README, etc.

# 3. Mark as ready when done
python tools/migration/repo_migration_helper.py \
    --mark-ready "repo-name-1"

# 4. When you have repos ready, generate publish script
python tools/migration/repo_migration_helper.py --generate-publish-script

# 5. Review and edit publish_ready_repos.sh, then run when ready
```

## Notes

- All repositories are cloned locally only - nothing is pushed to new account
- Review status is tracked in `migration_status.json`
- Publish script is generated but not executed automatically
- You have full control over what gets published and when


