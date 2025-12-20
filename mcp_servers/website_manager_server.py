#!/usr/bin/env python3
"""
MCP Server for Website Management
Exposes WordPress and website management capabilities via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

try:
    from tools.wordpress_manager import WordPressManager
    HAS_WORDPRESS = True
except ImportError:
    HAS_WORDPRESS = False
    WordPressManager = None

try:
    from tools.strategy_blog_automation import (
        create_blog_post,
        create_report_page,
        generate_strategy_analysis,
    )
    HAS_BLOG = True
except ImportError:
    HAS_BLOG = False

try:
    from trading_robot.website_design.thea_image_generation_script import TheaImageGenerator
    HAS_IMAGE_GEN = True
except ImportError:
    HAS_IMAGE_GEN = False


def create_wordpress_page(
    site_key: str, page_name: str, page_slug: Optional[str] = None, template_name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a WordPress page."""
    if not HAS_WORDPRESS:
        return {"success": False, "error": "WordPress tools not available"}

    try:
        manager = WordPressManager(site_key=site_key, dry_run=False)
        if not manager.connect():
            return {"success": False, "error": "Failed to connect to WordPress"}

        success = manager.create_page(
            page_name=page_name,
            page_slug=page_slug,
            template_name=template_name,
        )

        manager.disconnect()

        return {
            "success": success,
            "site": site_key,
            "page_name": page_name,
            "page_slug": page_slug or page_name.lower().replace(" ", "-"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def deploy_file_to_wordpress(
    site_key: str, local_path: str, remote_path: str, file_type: str = "theme"
) -> Dict[str, Any]:
    """Deploy a file to WordPress site."""
    if not HAS_WORDPRESS:
        return {"success": False, "error": "WordPress tools not available"}

    try:
        manager = WordPressManager(site_key=site_key, dry_run=False)
        if not manager.connect():
            return {"success": False, "error": "Failed to connect to WordPress"}

        local_file = Path(local_path)
        if not local_file.exists():
            return {"success": False, "error": f"Local file not found: {local_path}"}

        if file_type == "theme":
            success = manager.deploy_theme(
                local_path=local_file, remote_path=remote_path)
        elif file_type == "plugin":
            success = manager.deploy_plugin_file(
                local_path=local_file, remote_path=remote_path)
        else:
            success = manager.deploy_file(
                local_path=local_file, remote_path=remote_path)

        manager.disconnect()

        return {
            "success": success,
            "site": site_key,
            "local_path": str(local_path),
            "remote_path": remote_path,
            "file_type": file_type,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_page_to_menu(
    site_key: str, page_slug: str, menu_text: Optional[str] = None
) -> Dict[str, Any]:
    """Add a page to WordPress menu."""
    if not HAS_WORDPRESS:
        return {"success": False, "error": "WordPress tools not available"}

    try:
        manager = WordPressManager(site_key=site_key, dry_run=False)
        if not manager.connect():
            return {"success": False, "error": "Failed to connect to WordPress"}

        success = manager.add_to_menu(page_slug=page_slug, menu_text=menu_text)

        manager.disconnect()

        return {
            "success": success,
            "site": site_key,
            "page_slug": page_slug,
            "menu_text": menu_text or page_slug,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_wordpress_pages(site_key: str) -> Dict[str, Any]:
    """List all pages on WordPress site."""
    if not HAS_WORDPRESS:
        return {"success": False, "error": "WordPress tools not available"}

    try:
        manager = WordPressManager(site_key=site_key, dry_run=False)
        if not manager.connect():
            return {"success": False, "error": "Failed to connect to WordPress"}

        pages = manager.list_pages()

        manager.disconnect()

        return {
            "success": True,
            "site": site_key,
            "pages": pages,
            "count": len(pages),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_blog_post_for_site(
    site_name: str, strategy_name: Optional[str] = None
) -> Dict[str, Any]:
    """Create a blog post for a site."""
    if not HAS_BLOG:
        return {"success": False, "error": "Blog automation tools not available"}

    try:
        if strategy_name:
            # Generate strategy-specific analysis
            analysis = generate_strategy_analysis()
        else:
            analysis = None

        success = create_blog_post(site_name=site_name, analysis=analysis)

        return {
            "success": success,
            "site": site_name,
            "strategy": strategy_name,
            "post_type": "strategy_analysis" if strategy_name else "general",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_report_page_for_site(
    site_name: str, strategy_name: Optional[str] = None, premium: bool = False
) -> Dict[str, Any]:
    """Create a report page for a site."""
    if not HAS_BLOG:
        return {"success": False, "error": "Blog automation tools not available"}

    try:
        if strategy_name:
            analysis = generate_strategy_analysis()
        else:
            analysis = None

        success = create_report_page(
            site_name=site_name, analysis=analysis, premium=premium
        )

        return {
            "success": success,
            "site": site_name,
            "strategy": strategy_name,
            "premium": premium,
            "page_type": "premium_report" if premium else "free_report",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_image_prompts(output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Generate image prompts for website design."""
    if not HAS_IMAGE_GEN:
        return {"success": False, "error": "Image generation tools not available"}

    try:
        if output_dir:
            generator = TheaImageGenerator(output_dir=output_dir)
        else:
            generator = TheaImageGenerator()

        prompts = generator.generate_image_prompts()
        json_file = generator.save_prompts()
        md_file = generator.create_thea_prompt_file()

        return {
            "success": True,
            "prompts_count": len(prompts),
            "json_file": str(json_file),
            "markdown_file": str(md_file),
            "prompts": prompts,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def purge_wordpress_cache(site_key: str) -> Dict[str, Any]:
    """Purge WordPress cache."""
    if not HAS_WORDPRESS:
        return {"success": False, "error": "WordPress tools not available"}

    try:
        manager = WordPressManager(site_key=site_key, dry_run=False)
        if not manager.connect():
            return {"success": False, "error": "Failed to connect to WordPress"}

        success = manager.purge_caches(use_comprehensive_flush=True)

        manager.disconnect()

        return {
            "success": success,
            "site": site_key,
            "cache_flushed": success,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# MCP Server Protocol
def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "create_wordpress_page": {
                                "description": "Create a new WordPress page",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_key": {
                                            "type": "string",
                                            "description": "Site key (e.g., 'prismblossom', 'freerideinvestor')",
                                        },
                                        "page_name": {
                                            "type": "string",
                                            "description": "Page name/title",
                                        },
                                        "page_slug": {
                                            "type": "string",
                                            "description": "Optional: Page slug (URL-friendly name)",
                                        },
                                        "template_name": {
                                            "type": "string",
                                            "description": "Optional: Template name",
                                        },
                                    },
                                    "required": ["site_key", "page_name"],
                                },
                            },
                            "deploy_file_to_wordpress": {
                                "description": "Deploy a file to WordPress site",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_key": {
                                            "type": "string",
                                            "description": "Site key",
                                        },
                                        "local_path": {
                                            "type": "string",
                                            "description": "Local file path",
                                        },
                                        "remote_path": {
                                            "type": "string",
                                            "description": "Remote file path on server",
                                        },
                                        "file_type": {
                                            "type": "string",
                                            "enum": ["theme", "plugin", "file"],
                                            "default": "file",
                                            "description": "Type of file to deploy",
                                        },
                                    },
                                    "required": ["site_key", "local_path", "remote_path"],
                                },
                            },
                            "add_page_to_menu": {
                                "description": "Add a page to WordPress menu",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_key": {
                                            "type": "string",
                                            "description": "Site key",
                                        },
                                        "page_slug": {
                                            "type": "string",
                                            "description": "Page slug to add to menu",
                                        },
                                        "menu_text": {
                                            "type": "string",
                                            "description": "Optional: Menu text (defaults to page slug)",
                                        },
                                    },
                                    "required": ["site_key", "page_slug"],
                                },
                            },
                            "list_wordpress_pages": {
                                "description": "List all pages on WordPress site",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_key": {
                                            "type": "string",
                                            "description": "Site key",
                                        },
                                    },
                                    "required": ["site_key"],
                                },
                            },
                            "create_blog_post": {
                                "description": "Create a blog post for a site",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_name": {
                                            "type": "string",
                                            "description": "Site name (e.g., 'freerideinvestor', 'tradingrobotplug.com')",
                                        },
                                        "strategy_name": {
                                            "type": "string",
                                            "description": "Optional: Strategy name (e.g., 'tsla')",
                                        },
                                    },
                                    "required": ["site_name"],
                                },
                            },
                            "create_report_page": {
                                "description": "Create a report page for a site",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_name": {
                                            "type": "string",
                                            "description": "Site name",
                                        },
                                        "strategy_name": {
                                            "type": "string",
                                            "description": "Optional: Strategy name",
                                        },
                                        "premium": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Whether this is a premium report",
                                        },
                                    },
                                    "required": ["site_name"],
                                },
                            },
                            "generate_image_prompts": {
                                "description": "Generate image prompts for website design",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "output_dir": {
                                            "type": "string",
                                            "description": "Optional: Output directory for prompts",
                                        },
                                    },
                                },
                            },
                            "purge_wordpress_cache": {
                                "description": "Purge WordPress cache",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "site_key": {
                                            "type": "string",
                                            "description": "Site key",
                                        },
                                    },
                                    "required": ["site_key"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "website-manager-server", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "create_wordpress_page":
                    result = create_wordpress_page(**arguments)
                elif tool_name == "deploy_file_to_wordpress":
                    result = deploy_file_to_wordpress(**arguments)
                elif tool_name == "add_page_to_menu":
                    result = add_page_to_menu(**arguments)
                elif tool_name == "list_wordpress_pages":
                    result = list_wordpress_pages(**arguments)
                elif tool_name == "create_blog_post":
                    result = create_blog_post_for_site(**arguments)
                elif tool_name == "create_report_page":
                    result = create_report_page_for_site(**arguments)
                elif tool_name == "generate_image_prompts":
                    result = generate_image_prompts(**arguments)
                elif tool_name == "purge_wordpress_cache":
                    result = purge_wordpress_cache(**arguments)
                else:
                    result = {"success": False,
                              "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
            )


if __name__ == "__main__":
    main()

