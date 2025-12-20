# WordPress Page Setup Tool

## Overview

The `wordpress_page_setup.py` tool allows agents to automatically create and set up WordPress pages without manual intervention.

## Usage

### List Existing Pages
```bash
python wordpress_page_setup.py --list --site southwestsecret
```

### Create a New Page
```bash
python wordpress_page_setup.py --create "My New Page" --site southwestsecret
```

### Create Page with Custom Slug
```bash
python wordpress_page_setup.py --create "Birthday Party" --slug "birthday-party" --site southwestsecret
```

### Create Page with Custom Template
```bash
python wordpress_page_setup.py --create "Custom Page" --template "path/to/template.php" --site southwestsecret
```

## Features

- ✅ **Automatic Template Creation**: Creates `page-{slug}.php` template files
- ✅ **Functions.php Integration**: Automatically adds page creation functions
- ✅ **Theme Activation Hook**: Pages are created automatically when theme is activated
- ✅ **Site Mapping**: Supports multiple WordPress sites
- ✅ **Agent-Friendly**: Simple CLI interface for agents to use

## Supported Sites

- `southwestsecret` - SouthWest Secret website
- `carmyn` - Carmyn's page (same site)
- `aria` - Aria's page (same site)

## How Agents Use It

Agents can call this tool to:
1. Create new WordPress pages programmatically
2. Set up page templates automatically
3. Add pages to WordPress without manual steps
4. List existing pages to see what's available

## Example Agent Workflow

```python
from tools.wordpress_page_setup import WordPressPageSetup

# Agent creates a new page
setup = WordPressPageSetup("southwestsecret")
setup.setup_page(
    page_name="Guestbook",
    page_slug="guestbook",
    template_content="...custom template..."
)
```

## Integration with WordPress

The tool:
1. Creates the page template file in the theme directory
2. Adds a function to `functions.php` that creates the page on theme activation
3. Uses WordPress hooks (`after_switch_theme`) for automatic page creation

## Notes

- Pages are created when the theme is activated/re-activated
- Templates follow WordPress naming conventions (`page-{slug}.php`)
- All changes are made to local files (deployment handled separately)

