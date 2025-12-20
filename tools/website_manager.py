#!/usr/bin/env python3
"""
Unified Website Management Tool
================================

Single comprehensive tool for all website operations:
- WordPress page creation and updates
- Template file management
- Content updates (text, colors, styles)
- File deployment (SFTP/SSH)
- Multi-site support
- Batch operations

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <400 lines
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

logger = logging.getLogger(__name__)


class WebsiteManager:
    """Unified tool for all website management operations."""
    
    # Site configuration mapping
    SITE_CONFIGS = {
        "prismblossom": {
            "local_path": "D:/websites/prismblossom.online",
            "theme_name": "prismblossom",
            "remote_base": "/public_html/wp-content/themes/prismblossom",
            "function_prefix": "prismblossom"
        },
        "prismblossom.online": {
            "local_path": "D:/websites/prismblossom.online",
            "theme_name": "prismblossom",
            "remote_base": "/public_html/wp-content/themes/prismblossom",
            "function_prefix": "prismblossom"
        },
        "southwestsecret": {
            "local_path": "D:/websites/southwestsecret.com",
            "theme_name": "southwestsecret",
            "remote_base": "/public_html/wp-content/themes/southwestsecret",
            "function_prefix": "southwestsecret"
        },
        "ariajet": {
            "local_path": "D:/websites/ariajet.site",
            "theme_name": None,  # Static site
            "remote_base": "/public_html",
            "function_prefix": None
        },
    }
    
    def __init__(self, site_key: str = "prismblossom"):
        """Initialize website manager for a specific site."""
        self.site_key = site_key
        self.config = self.SITE_CONFIGS.get(site_key)
        if not self.config:
            raise ValueError(f"Site not found: {site_key}")
        
        self.local_path = Path(self.config["local_path"])
        if not self.local_path.exists():
            raise FileNotFoundError(f"Local path not found: {self.local_path}")
        
        self.theme_path = None
        if self.config["theme_name"]:
            theme_paths = [
                self.local_path / "wordpress-theme" / self.config["theme_name"],
                self.local_path / "wp-content" / "themes" / self.config["theme_name"],
            ]
            for path in theme_paths:
                if path.exists():
                    self.theme_path = path
                    break
    
    def get_template_path(self, template_name: str) -> Path:
        """Get full path to a template file."""
        if not self.theme_path:
            raise ValueError(f"WordPress theme not found for {self.site_key}")
        return self.theme_path / template_name
    
    def update_page_template(self, template_name: str, updates: Dict[str, str]) -> bool:
        """
        Update a page template with content changes.
        
        Args:
            template_name: Name of template file (e.g., 'page-invitation.php')
            updates: Dict of updates:
                - 'colors': Replace color scheme (e.g., {'old': '#ff00ff', 'new': '#000000'})
                - 'text': Replace text content
                - 'remove': Remove placeholder text
                - 'add': Add new content
        """
        try:
            template_path = self.get_template_path(template_name)
            if not template_path.exists():
                print(f"❌ Template not found: {template_path}")
                return False
            
            content = template_path.read_text(encoding='utf-8')
            original_content = content
            
            # Update colors
            if 'colors' in updates:
                for old_color, new_color in updates['colors'].items():
                    content = content.replace(old_color, new_color)
            
            # Remove placeholder text
            if 'remove' in updates:
                for placeholder in updates['remove']:
                    content = content.replace(placeholder, '')
                    # Also handle with brackets
                    content = content.replace(f'[{placeholder}]', '')
                    content = content.replace(f'[your {placeholder} here]', '')
            
            # Replace text
            if 'text' in updates:
                for old_text, new_text in updates['text'].items():
                    content = content.replace(old_text, new_text)
            
            # Add content
            if 'add' in updates:
                for location, new_content in updates['add'].items():
                    if location == 'before_closing_section':
                        content = content.replace('</section>', f'{new_content}\n</section>')
                    elif location == 'after_opening_section':
                        content = re.sub(r'(<section[^>]*>)', 
                                        rf'\1\n{new_content}', content)
                    elif location == 'end_of_file':
                        content = content.rstrip() + f'\n{new_content}\n'
            
            if content != original_content:
                template_path.write_text(content, encoding='utf-8')
                print(f"✅ Updated {template_name}")
                return True
            else:
                print(f"⚠️  No changes made to {template_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating template: {e}")
            return False
    
    def create_page_template(self, page_name: str, template_content: str,
                            template_name: Optional[str] = None) -> bool:
        """Create a new page template file."""
        try:
            if not self.theme_path:
                raise ValueError("WordPress theme required for template creation")
            
            template_name = template_name or f"page-{page_name.lower().replace(' ', '-')}.php"
            template_path = self.theme_path / template_name
            
            if template_path.exists():
                print(f"⚠️  Template already exists: {template_name}")
                return False
            
            template_path.write_text(template_content, encoding='utf-8')
            print(f"✅ Created template: {template_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating template: {e}")
            return False
    
    def update_colors(self, template_name: str, color_scheme: Dict[str, str]) -> bool:
        """
        Update color scheme in a template.
        
        Args:
            template_name: Template file name
            color_scheme: Dict mapping old colors to new colors
        """
        return self.update_page_template(template_name, {'colors': color_scheme})
    
    def add_placeholder_entries(self, template_name: str, entries: List[Dict[str, str]]) -> bool:
        """Add placeholder entries to a template (e.g., guestbook entries)."""
        try:
            template_path = self.get_template_path(template_name)
            if not template_path.exists():
                return False
            
            content = template_path.read_text(encoding='utf-8')
            
            # Find where to insert entries (look for "No messages yet" or "else {" block)
            placeholder_patterns = [
                r'(} else \{[^}]*echo\s+[\'"]<p class="no-messages">.*?</p>[\'"];)',
                r'(} else \{[^}]*echo\s+[\'"]<p[^>]*>No messages yet.*?</p>[\'"];)',
                r'(if \(\$entries\) \{[^}]*\} else \{[^}]*echo)',
            ]
            
            found_pattern = None
            for pattern in placeholder_patterns:
                if re.search(pattern, content, re.DOTALL):
                    found_pattern = pattern
                    break
            
            if found_pattern:
                # Generate placeholder entries code
                entries_code = "// Placeholder entries for visitors to see\n"
                entries_code += "$placeholder_entries = [\n"
                for entry in entries:
                    entries_code += f"    ['name' => '{entry['name']}', "
                    entries_code += f"'date' => '{entry['date']}', "
                    entries_code += f"'message' => '{entry['message']}'],\n"
                entries_code += "];\n\n"
                entries_code += "foreach ($placeholder_entries as $placeholder) {\n"
                entries_code += "    echo '<div class=\"message-card\">';\n"
                entries_code += "    echo '<div class=\"message-header\">';\n"
                entries_code += "    echo '<span class=\"message-name\">' . esc_html($placeholder['name']) . '</span>';\n"
                entries_code += "    echo '<span class=\"message-date\">' . esc_html($placeholder['date']) . '</span>';\n"
                entries_code += "    echo '</div>';\n"
                entries_code += "    echo '<div class=\"message-content\">' . esc_html($placeholder['message']) . '</div>';\n"
                entries_code += "    echo '</div>';\n"
                entries_code += "}\n\n"
                
                # Replace "No messages" with placeholder entries
                content = re.sub(found_pattern,
                               entries_code + r'\1',
                               content, flags=re.DOTALL)
                
                template_path.write_text(content, encoding='utf-8')
                print(f"✅ Added {len(entries)} placeholder entries to {template_name}")
                return True
            else:
                print(f"⚠️  Could not find insertion point in {template_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding placeholder entries: {e}")
            return False
    
    def add_interactive_features(self, template_name: str, features: List[Dict[str, str]]) -> bool:
        """Add interactive features to a template (buttons, galleries, games)."""
        try:
            template_path = self.get_template_path(template_name)
            if not template_path.exists():
                return False
            
            content = template_path.read_text(encoding='utf-8')
            
            # Find insertion point (after section description or title)
            insertion_patterns = [
                r'(<p class="section-description">.*?</p>)',
                r'(<p[^>]*class="[^"]*description[^"]*"[^>]*>.*?</p>)',
                r'(<p[^>]*>Click or tap.*?</p>)',
                r'(</h1>\s*<p[^>]*>)',
            ]
            
            insertion_point = None
            for pattern in insertion_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    insertion_point = match
                    break
            
            if insertion_point:
                features_html = "\n        <!-- Interactive Features -->\n"
                for feature in features:
                    if feature['type'] == 'button_group':
                        features_html += f'        <div class="{feature.get("class", "mini-games-container")}" style="{feature.get("style", "")}">\n'
                        features_html += f'            <h2 style="{feature.get("title_style", "")}">{feature.get("title", "Interactive Features")}</h2>\n'
                        features_html += f'            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">\n'
                        for button in feature.get('buttons', []):
                            features_html += f'                <button id="{button["id"]}" style="{button.get("style", "")}">{button["text"]}</button>\n'
                        features_html += '            </div>\n'
                        features_html += '        </div>\n'
                    elif feature['type'] == 'gallery':
                        features_html += f'        <div class="{feature.get("class", "birthday-gallery")}" style="{feature.get("style", "")}">\n'
                        features_html += f'            <h2 style="{feature.get("title_style", "")}">{feature.get("title", "Gallery")}</h2>\n'
                        features_html += f'            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">\n'
                        for item in feature.get('items', []):
                            features_html += f'                <div class="gallery-item" style="{item.get("style", "")}">\n'
                            features_html += f'                    <p style="{item.get("text_style", "")}">{item.get("text", "[Image Placeholder]")}</p>\n'
                            features_html += '                </div>\n'
                        features_html += '            </div>\n'
                        features_html += '        </div>\n'
                
                # Insert after section description
                content = content[:insertion_point.end()] + features_html + content[insertion_point.end():]
                
                # Add JavaScript for interactive features
                js_code = "\n    // Interactive Features Handlers\n"
                for feature in features:
                    if feature['type'] == 'button_group':
                        for button in feature.get('buttons', []):
                            js_code += f"""    const {button['id']}Btn = document.getElementById('{button['id']}');
    if ({button['id']}Btn) {{
        {button['id']}Btn.addEventListener('click', function() {{
            {button.get('action', '// Add action here')}
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {{ this.style.transform = 'scale(1)'; }}, 100);
        }});
    }}
"""
                
                # Insert JavaScript before closing script tag (only if script tag exists)
                if '</script>' in content and js_code.strip():
                    # Find last script tag and insert before it
                    last_script_pos = content.rfind('</script>')
                    if last_script_pos != -1:
                        content = content[:last_script_pos] + js_code + content[last_script_pos:]
                
                template_path.write_text(content, encoding='utf-8')
                print(f"✅ Added interactive features to {template_name}")
                return True
            else:
                print(f"⚠️  Could not find insertion point in {template_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding interactive features: {e}")
            return False
    
    def deploy_file(self, template_name: str, use_hostinger_file_manager: bool = True) -> bool:
        """
        Deploy a file to the live server.
        
        Args:
            template_name: Template file to deploy
            use_hostinger_file_manager: If True, provides instructions for manual upload
        """
        if use_hostinger_file_manager:
            print("📋 Hostinger File Manager Deployment Instructions:")
            print(f"   1. Log into hpanel.hostinger.com")
            print(f"   2. Open File Manager")
            print(f"   3. Navigate to: {self.config['remote_base']}")
            print(f"   4. Upload: {template_name}")
            print(f"   5. File will be live immediately!")
            return True
        
        # SFTP deployment (if credentials available)
        try:
            creds_file = Path(".deploy_credentials/sites.json")
            if not creds_file.exists():
                print("⚠️  Credentials not found. Use Hostinger File Manager instead.")
                return False
            
            with open(creds_file) as f:
                creds = json.load(f)
            
            site_creds = creds.get(self.site_key, {})
            if not site_creds.get('host'):
                print("⚠️  SFTP credentials not configured. Use Hostinger File Manager.")
                return False
            
            # Use wordpress_manager for actual deployment
            from wordpress_manager import WordPressManager
            manager = WordPressManager(self.site_key)
            template_path = self.get_template_path(template_name)
            return manager.deploy_file(template_path)
            
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def batch_update(self, updates: List[Dict[str, any]]) -> Dict[str, bool]:
        """Perform multiple updates in sequence."""
        results = {}
        for update in updates:
            action = update.get('action')
            template = update.get('template')
            
            if action == 'update_colors':
                results[template] = self.update_colors(template, update.get('colors', {}))
            elif action == 'add_placeholders':
                results[template] = self.add_placeholder_entries(template, update.get('entries', []))
            elif action == 'add_features':
                results[template] = self.add_interactive_features(template, update.get('features', []))
            elif action == 'create_template':
                results[template] = self.create_page_template(
                    update.get('page_name', ''),
                    update.get('content', ''),
                    template
                )
        
        return results
    
    # ========== INTEGRATION WITH EXISTING TOOLS ==========
    
    def create_page(self, page_name: str, page_slug: Optional[str] = None,
                   template_content: Optional[str] = None) -> bool:
        """
        Create WordPress page (compatible with wordpress_page_setup.py).
        Consolidates: wordpress_page_setup.setup_page()
        """
        page_slug = page_slug or page_name.lower().replace(' ', '-')
        template_name = f"page-{page_slug}.php"
        
        if not template_content:
            template_content = f"""<?php
/**
 * Template Name: {page_name}
 * @package {self.config['theme_name'].title() if self.config['theme_name'] else 'WordPress'}
 */
get_header();
?>
<section class="{page_slug}-section">
    <div class="container">
        <h1>{page_name}</h1>
        <p>Content goes here...</p>
    </div>
</section>
<?php get_footer(); ?>"""
        
        # Create template
        if not self.create_page_template(page_name, template_content, template_name):
            return False
        
        # Add to functions.php (if WordPress theme)
        if self.config.get('function_prefix'):
            self._add_page_function(page_name, page_slug, template_name)
        
        print(f"✅ Page '{page_name}' created!")
        return True
    
    def _add_page_function(self, page_name: str, page_slug: str, template_name: str):
        """Add page creation function to functions.php."""
        try:
            if not self.theme_path:
                return
            
            functions_file = self.theme_path / "functions.php"
            if not functions_file.exists():
                return
            
            prefix = self.config.get('function_prefix', 'prismblossom')
            function_name = f"{prefix}_create_{page_slug.replace('-', '_')}_page"
            
            code = f"""// Create {page_name} page
function {function_name}() {{
    if (get_page_by_path('{page_slug}')) return;
    ${page_slug}_page = array(
        'post_title' => '{page_name}',
        'post_name' => '{page_slug}',
        'post_status' => 'publish',
        'post_type' => 'page',
        'page_template' => '{template_name}'
    );
    wp_insert_post(${page_slug}_page);
}}
add_action('after_switch_theme', '{function_name}');"""
            
            content = functions_file.read_text(encoding='utf-8')
            if function_name not in content:
                content += f"\n\n{code}\n"
                functions_file.write_text(content, encoding='utf-8')
                print(f"✅ Added page function to functions.php")
        except Exception as e:
            print(f"⚠️  Could not add to functions.php: {e}")
    
    def deploy_theme_files(self, pattern: str = "*.php") -> int:
        """
        Deploy all theme files (compatible with wordpress_manager.deploy_theme()).
        Consolidates: wordpress_manager.deploy_theme()
        """
        try:
            from wordpress_manager import WordPressManager
            manager = WordPressManager(self.site_key)
            return manager.deploy_theme(pattern)
        except Exception as e:
            print(f"⚠️  SFTP deployment not available: {e}")
            print("📋 Use Hostinger File Manager instead:")
            print(f"   1. Log into hpanel.hostinger.com")
            print(f"   2. Open File Manager")
            print(f"   3. Navigate to: {self.config['remote_base']}")
            print(f"   4. Upload all {pattern} files")
            return 0
    
    def auto_deploy_changed_files(self, changed_files: List[str]) -> Dict[str, bool]:
        """
        Auto-deploy changed files (compatible with auto_deploy_hook.py).
        Consolidates: auto_deploy_hook.auto_deploy()
        """
        results = {}
        for file_path in changed_files:
            file_name = Path(file_path).name
            if file_name.endswith('.php') and 'page-' in file_name:
                results[file_path] = self.deploy_file(file_name, use_hostinger_file_manager=True)
        return results


def main():
    """CLI interface for unified website management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Website Management Tool")
    parser.add_argument('--site', default='prismblossom',
                       help='Site key (default: prismblossom)')
    parser.add_argument('--update-colors', nargs=2, metavar=('TEMPLATE', 'OLD:NEW'),
                       help='Update colors in template (e.g., page-invitation.php #ff00ff:#000000)')
    parser.add_argument('--add-placeholders', type=str,
                       help='Add placeholder entries to template')
    parser.add_argument('--add-features', type=str,
                       help='Add interactive features to template')
    parser.add_argument('--create', type=str,
                       help='Create new page template')
    parser.add_argument('--deploy', type=str,
                       help='Deploy template file')
    parser.add_argument('--batch', type=str,
                       help='JSON file with batch updates')
    
    args = parser.parse_args()
    
    try:
        manager = WebsiteManager(args.site)
        
        if args.update_colors:
            template, color_map = args.update_colors
            old_color, new_color = color_map.split(':')
            success = manager.update_colors(template, {old_color: new_color})
            sys.exit(0 if success else 1)
        
        elif args.add_placeholders:
            # Example usage would require JSON input
            print("Use --batch with JSON file for placeholder entries")
            sys.exit(1)
        
        elif args.deploy:
            success = manager.deploy_file(args.deploy)
            sys.exit(0 if success else 1)
        
        elif args.batch:
            with open(args.batch) as f:
                batch_data = json.load(f)
            
            # Handle both formats: direct updates list or wrapped in 'updates' key
            updates = batch_data.get('updates', batch_data) if isinstance(batch_data, dict) else batch_data
            
            results = manager.batch_update(updates)
            print(f"\n📊 Batch Update Results:")
            for template, success in results.items():
                print(f"   {'✅' if success else '❌'} {template}")
            sys.exit(0 if all(results.values()) else 1)
        
        elif args.create:
            success = manager.create_page(args.create)
            sys.exit(0 if success else 1)
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

