# Unified Website Management Tool

**Single tool for all website updates** - Consolidates WordPress management, page setup, deployment, and content updates.

## 🎯 Purpose

Instead of using multiple tools (`wordpress_manager.py`, `wordpress_page_setup.py`, `deploy_ariajet.py`, etc.), agents now have **one unified tool** for all website operations.

## 📋 Features

- ✅ **Page Template Updates** - Update colors, text, styles
- ✅ **Placeholder Entries** - Add sample entries (guestbook, testimonials)
- ✅ **Interactive Features** - Add buttons, galleries, mini-games
- ✅ **Template Creation** - Create new page templates
- ✅ **Batch Operations** - Update multiple pages at once
- ✅ **Deployment** - Deploy files (Hostinger File Manager or SFTP)

## 🚀 Quick Start

### Update Colors (Black & Gold Theme)

```bash
python tools/website_manager.py --site prismblossom --update-colors page-invitation.php "#ff00ff:#000000"
python tools/website_manager.py --site prismblossom --update-colors page-invitation.php "#ffffff:#FFD700"
```

### Batch Updates (Recommended)

Create a JSON file with all updates:

```json
{
  "updates": [
    {
      "action": "update_colors",
      "template": "page-invitation.php",
      "colors": {
        "#ff00ff": "#000000",
        "#ffffff": "#FFD700"
      }
    },
    {
      "action": "add_placeholders",
      "template": "page-guestbook.php",
      "entries": [
        {
          "name": "Sarah M.",
          "date": "Jan 25, 2025",
          "message": "Happy Birthday Carmyn! 🎉"
        },
        {
          "name": "Mike T.",
          "date": "Jan 24, 2025",
          "message": "Have a fantastic birthday! 🎵"
        }
      ]
    },
    {
      "action": "add_features",
      "template": "page-birthday-fun.php",
      "features": [
        {
          "type": "button_group",
          "title": "🎮 Mini Games",
          "buttons": [
            {
              "id": "confetti-burst",
              "text": "🎉 Confetti Burst",
              "action": "createConfetti();"
            },
            {
              "id": "golden-sparkles",
              "text": "✨ Golden Sparkles",
              "action": "createSparkles();"
            }
          ]
        },
        {
          "type": "gallery",
          "title": "📸 Birthday Memories",
          "items": [
            {"text": "[Birthday Image 1]"},
            {"text": "[Birthday Image 2]"},
            {"text": "[Birthday Image 3]"}
          ]
        }
      ]
    }
  ]
}
```

Run batch update:
```bash
python tools/website_manager.py --site prismblossom --batch updates.json
```

## 📝 Usage Examples

### Example 1: Birthday Website Updates (4 Steps)

**Step 1: Update Invitation Page Colors**
```python
from tools.website_manager import WebsiteManager

manager = WebsiteManager("prismblossom")
manager.update_colors("page-invitation.php", {
    "#ff00ff": "#000000",  # Pink → Black
    "#ffffff": "#FFD700"   # White → Gold
})
```

**Step 2: Add Guestbook Placeholders**
```python
manager.add_placeholder_entries("page-guestbook.php", [
    {"name": "Sarah M.", "date": "Jan 25, 2025", "message": "Happy Birthday! 🎉"},
    {"name": "Mike T.", "date": "Jan 24, 2025", "message": "Have a great day! 🎵"}
])
```

**Step 3: Add Interactive Features**
```python
manager.add_interactive_features("page-birthday-fun.php", [
    {
        "type": "button_group",
        "title": "🎮 Mini Games",
        "buttons": [
            {"id": "confetti-burst", "text": "🎉 Confetti Burst"},
            {"id": "golden-sparkles", "text": "✨ Golden Sparkles"}
        ]
    }
])
```

**Step 4: Deploy**
```python
manager.deploy_file("page-invitation.php", use_hostinger_file_manager=True)
```

### Example 2: Create New Page Template

```python
template_content = """<?php
/**
 * Template Name: Birthday Blog Post
 * @package PrismBlossom
 */
get_header();
?>
<section class="birthday-blog-section">
    <div class="container">
        <h1>🎂 Celebrating Carmyn's Birthday!</h1>
        <p>Content here...</p>
    </div>
</section>
<?php get_footer(); ?>"""

manager.create_page_template("Birthday Blog Post", template_content, "page-birthday-blog.php")
```

## 🔧 Supported Sites

- `prismblossom` / `prismblossom.online`
- `southwestsecret`
- `ariajet` (static site)

## 📦 Integration with Existing Tools

The unified tool **wraps** existing functionality:
- Uses `wordpress_manager.py` for deployment (if SFTP credentials available)
- Compatible with `wordpress_page_setup.py` patterns
- Works with `auto_deploy_hook.py` for git-based deployments

## 🎨 Common Update Patterns

### Pattern 1: Color Theme Update
```python
# Change entire site to black & gold
color_scheme = {
    "#ff00ff": "#000000",  # Pink → Black
    "#ffffff": "#FFD700",  # White → Gold
    "#00ffff": "#FFD700"   # Cyan → Gold
}
manager.update_colors("page-invitation.php", color_scheme)
```

### Pattern 2: Add Placeholder Content
```python
# Add sample entries before real data exists
entries = [
    {"name": "User 1", "date": "Today", "message": "Sample message"},
    {"name": "User 2", "date": "Yesterday", "message": "Another message"}
]
manager.add_placeholder_entries("page-guestbook.php", entries)
```

### Pattern 3: Add Interactive Elements
```python
# Add buttons, galleries, games
features = [
    {
        "type": "button_group",
        "buttons": [
            {"id": "btn1", "text": "Click Me", "action": "doSomething();"}
        ]
    },
    {
        "type": "gallery",
        "items": [{"text": "[Image 1]"}, {"text": "[Image 2]"}]
    }
]
manager.add_interactive_features("page-fun.php", features)
```

## 🚀 Deployment Options

### Option 1: Hostinger File Manager (Recommended)
```python
manager.deploy_file("page-invitation.php", use_hostinger_file_manager=True)
# Prints instructions for manual upload
```

### Option 2: SFTP (If credentials configured)
```python
manager.deploy_file("page-invitation.php", use_hostinger_file_manager=False)
# Uses wordpress_manager.py for SFTP deployment
```

## 📊 Batch Operations

For complex updates (like birthday website), use batch operations:

```python
updates = [
    {
        "action": "update_colors",
        "template": "page-invitation.php",
        "colors": {"#ff00ff": "#000000", "#ffffff": "#FFD700"}
    },
    {
        "action": "add_placeholders",
        "template": "page-guestbook.php",
        "entries": [...]
    },
    {
        "action": "add_features",
        "template": "page-birthday-fun.php",
        "features": [...]
    }
]

results = manager.batch_update(updates)
# Returns: {"page-invitation.php": True, "page-guestbook.php": True, ...}
```

## ✅ Benefits

1. **Single Interface** - One tool instead of 4+ separate tools
2. **Consistent Pattern** - Same workflow for all website updates
3. **Batch Operations** - Update multiple pages at once
4. **Easy to Use** - Simple Python API or CLI
5. **Flexible Deployment** - Hostinger File Manager or SFTP

## 🔄 Migration from Old Tools

**Old way:**
```bash
python tools/wordpress_page_setup.py --site prismblossom --create "Birthday Page"
python tools/wordpress_manager.py --site prismblossom --deploy
```

**New way:**
```bash
python tools/website_manager.py --site prismblossom --create "Birthday Page"
python tools/website_manager.py --site prismblossom --deploy page-birthday.php
```

Or use Python API:
```python
from tools.website_manager import WebsiteManager
manager = WebsiteManager("prismblossom")
manager.create_page_template("Birthday Page", content)
manager.deploy_file("page-birthday.php")
```

---

**Created by**: Agent-7 (Web Development Specialist)  
**Pattern**: Based on birthday website update workflow  
**Status**: ✅ Ready for use







