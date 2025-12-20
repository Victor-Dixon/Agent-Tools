# Website Manager MCP Server

MCP server for managing WordPress sites and website operations. Enables agents to create pages, deploy files, manage menus, create blog posts, and generate image prompts.

## Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "website-manager": {
      "command": "python",
      "args": [
        "D:/Agent_Cellphone_V2_Repository/mcp_servers/website_manager_server.py"
      ]
    }
  }
}
```

## Available Tools

### WordPress Management

#### 1. `create_wordpress_page`
Create a new WordPress page

**Parameters:**
- `site_key` (required): Site key (e.g., 'prismblossom', 'freerideinvestor')
- `page_name` (required): Page name/title
- `page_slug` (optional): Page slug (URL-friendly name)
- `template_name` (optional): Template name

**Example:**
```json
{
  "name": "create_wordpress_page",
  "arguments": {
    "site_key": "freerideinvestor",
    "page_name": "Trading Strategy Guide",
    "page_slug": "trading-strategy-guide"
  }
}
```

#### 2. `deploy_file_to_wordpress`
Deploy a file to WordPress site

**Parameters:**
- `site_key` (required): Site key
- `local_path` (required): Local file path
- `remote_path` (required): Remote file path on server
- `file_type` (optional): Type of file - "theme", "plugin", or "file" (default: "file")

**Example:**
```json
{
  "name": "deploy_file_to_wordpress",
  "arguments": {
    "site_key": "freerideinvestor",
    "local_path": "templates/page-template.php",
    "remote_path": "wp-content/themes/custom/page-template.php",
    "file_type": "theme"
  }
}
```

#### 3. `add_page_to_menu`
Add a page to WordPress menu

**Parameters:**
- `site_key` (required): Site key
- `page_slug` (required): Page slug to add to menu
- `menu_text` (optional): Menu text (defaults to page slug)

**Example:**
```json
{
  "name": "add_page_to_menu",
  "arguments": {
    "site_key": "freerideinvestor",
    "page_slug": "trading-strategy-guide",
    "menu_text": "Strategy Guide"
  }
}
```

#### 4. `list_wordpress_pages`
List all pages on WordPress site

**Parameters:**
- `site_key` (required): Site key

**Example:**
```json
{
  "name": "list_wordpress_pages",
  "arguments": {
    "site_key": "freerideinvestor"
  }
}
```

#### 5. `purge_wordpress_cache`
Purge WordPress cache

**Parameters:**
- `site_key` (required): Site key

**Example:**
```json
{
  "name": "purge_wordpress_cache",
  "arguments": {
    "site_key": "freerideinvestor"
  }
}
```

### Blog Automation

#### 6. `create_blog_post`
Create a blog post for a site

**Parameters:**
- `site_name` (required): Site name (e.g., 'freerideinvestor', 'tradingrobotplug.com')
- `strategy_name` (optional): Strategy name (e.g., 'tsla')

**Example:**
```json
{
  "name": "create_blog_post",
  "arguments": {
    "site_name": "freerideinvestor",
    "strategy_name": "tsla"
  }
}
```

#### 7. `create_report_page`
Create a report page for a site

**Parameters:**
- `site_name` (required): Site name
- `strategy_name` (optional): Strategy name
- `premium` (optional): Whether this is a premium report (default: false)

**Example:**
```json
{
  "name": "create_report_page",
  "arguments": {
    "site_name": "tradingrobotplug.com",
    "strategy_name": "tsla",
    "premium": true
  }
}
```

### Image Generation

#### 8. `generate_image_prompts`
Generate image prompts for website design

**Parameters:**
- `output_dir` (optional): Output directory for prompts

**Example:**
```json
{
  "name": "generate_image_prompts",
  "arguments": {
    "output_dir": "trading_robot/website_design/generated_images"
  }
}
```

## Integration with Agent Operating Cycle

### For Website Tasks

**CYCLE START:**
- Check if task involves website operations
- Review site requirements from DELEGATION_BOARD

**DURING CYCLE:**
- Use `create_wordpress_page` for new pages
- Use `deploy_file_to_wordpress` for file deployments
- Use `create_blog_post` for content creation

**CYCLE END:**
- Use `purge_wordpress_cache` after deployments
- Update MASTER_TASK_LOG with completion status

## Common Workflows

### Creating a New Page

1. Create page: `create_wordpress_page(site_key, page_name, page_slug)`
2. Add to menu: `add_page_to_menu(site_key, page_slug)`
3. Deploy template: `deploy_file_to_wordpress(site_key, local_path, remote_path, "theme")`
4. Purge cache: `purge_wordpress_cache(site_key)`

### Creating Blog Content

1. Generate blog post: `create_blog_post(site_name, strategy_name)`
2. Create report page: `create_report_page(site_name, strategy_name, premium)`
3. Update task log: Mark task complete in MASTER_TASK_LOG

### Website Design

1. Generate image prompts: `generate_image_prompts(output_dir)`
2. Use prompts with image generation tool
3. Deploy images: `deploy_file_to_wordpress(site_key, local_path, remote_path)`

## Site Keys Reference

Common site keys:
- `prismblossom` - Prism Blossom site
- `freerideinvestor` - FreeRide Investor site
- `crosbyultimateevents` - Crosby Ultimate Events
- `tradingrobotplug` - Trading Robot Plug
- `houston sipqueen` - Houston Sip Queen
- `weareswarm` - We Are Swarm sites

## Benefits

1. **Centralized Website Operations** - All WordPress operations in one place
2. **Agent Automation** - Agents can manage websites automatically
3. **Content Creation** - Automated blog post and report generation
4. **File Deployment** - Easy theme/plugin file deployment
5. **Cache Management** - Automatic cache purging after changes

## Related Documents

- `tools/wordpress_manager.py` - WordPress management tool source
- `tools/strategy_blog_automation.py` - Blog automation source
- `trading_robot/website_design/` - Website design assets
- `DELEGATION_BOARD.md` - Task ownership for website tasks
- `MASTER_TASK_LOG.md` - Task tracking

## Troubleshooting

### Connection Failed
- Check site credentials in `.deploy_credentials/`
- Verify site key is correct
- Check network connectivity

### File Not Found
- Verify local file path exists
- Check file permissions
- Ensure file is in correct format

### Blog Post Failed
- Check site configuration in `.deploy_credentials/blogging_api.json`
- Verify site name matches config
- Check WordPress API credentials

