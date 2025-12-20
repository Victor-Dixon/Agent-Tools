# Unified WordPress Management Tool

## Overview

All WordPress tools have been unified into a single comprehensive tool: `wordpress_manager.py`

## What Was Unified

### Before (Multiple Tools):
1. `wordpress_deployment_manager.py` - File deployment only
2. `wordpress_page_setup.py` - Page creation only
3. `deploy_prismblossom.py` - Site-specific deployment
4. `deploy_prismblossom_now.py` - Duplicate deployment script

### After (One Tool):
- `wordpress_manager.py` - **Unified tool with all features**

## Features

### ✅ Page Management
- Create pages with templates
- Auto-generate functions.php code
- List existing pages
- Update page content

### ✅ Deployment
- Deploy single files
- Deploy entire theme directories
- SFTP/SSH connection management
- Auto-deploy on git commit

### ✅ Database Operations
- Create database tables
- Generate WordPress table creation code
- Auto-add to functions.php

### ✅ Menu Management
- Add pages to navigation menus
- Auto-generate menu code
- Support for multiple menu locations

### ✅ WP-CLI Integration
- Execute WP-CLI commands via SSH
- Run WordPress commands remotely

### ✅ Utilities
- Verify WordPress setup
- List pages and templates
- Check theme structure

## Usage

### Create a Page
```bash
python tools/wordpress_manager.py --site prismblossom --create-page "My Page"
```

### Deploy Files
```bash
python tools/wordpress_manager.py --site prismblossom --deploy
```

### List Pages
```bash
python tools/wordpress_manager.py --site prismblossom --list
```

### Verify Setup
```bash
python tools/wordpress_manager.py --site prismblossom --verify
```

### Add to Menu
```bash
python tools/wordpress_manager.py --site prismblossom --add-menu "my-page"
```

## Backward Compatibility

The old `WordPressDeploymentManager` still works for existing code:
- Old imports continue to work
- Compatibility wrapper provides old method names
- Gradual migration path available

## Migration Guide

### Old Code:
```python
from wordpress_deployment_manager import WordPressDeploymentManager
manager = WordPressDeploymentManager("prismblossom")
manager.deploy_theme_file(local_path, remote_subpath)
```

### New Code:
```python
from wordpress_manager import WordPressManager
manager = WordPressManager("prismblossom")
manager.deploy_file(local_path)
# OR
manager.deploy_theme()  # Deploy all theme files
```

## Supported Sites

- `prismblossom` / `prismblossom.online`
- `southwestsecret`
- More sites can be added to SITE_CONFIGS

## Benefits

1. **Single Source of Truth** - One tool for all WordPress operations
2. **No Duplication** - Eliminated redundant code
3. **Easier Maintenance** - One codebase to maintain
4. **Better Features** - All capabilities in one place
5. **Backward Compatible** - Existing code still works

## Next Steps

1. ✅ Unified tool created
2. ✅ Backward compatibility maintained
3. ✅ Duplicate tools removed
4. ✅ Auto-deploy hook updated
5. 🔄 Migrate remaining code to use unified tool (optional)

---

*Unified by Agent-7 (Web Development Specialist)*

