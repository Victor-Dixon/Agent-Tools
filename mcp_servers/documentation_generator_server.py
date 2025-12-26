#!/usr/bin/env python3
"""
Documentation Generator Server - MCP server to keep documentation in sync.

Tools:
- generate_api_docs: Generate OpenAPI/Swagger docs from code
- update_readme: Update README with code changes
- generate_type_docs: Generate TypeDoc/Sphinx documentation
- check_doc_coverage: Find undocumented functions
- validate_links: Check for broken documentation links
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

EXCLUDED_DIRS = {'node_modules', '.git', 'vendor', 'venv', '.venv', '__pycache__', 'dist', 'build', '.next', 'coverage'}


def generate_api_docs(
    project_path: str = ".",
    framework: str = "auto",
    output_path: str | None = None,
    format: str = "json"
) -> dict[str, Any]:
    """Generate OpenAPI/Swagger documentation from code."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect framework
    if framework == "auto":
        if (project_path / "package.json").exists():
            pkg_content = (project_path / "package.json").read_text()
            if '"express"' in pkg_content or "'express'" in pkg_content:
                framework = "express"
            elif '"fastify"' in pkg_content:
                framework = "fastify"
            elif '"@nestjs/core"' in pkg_content:
                framework = "nestjs"
            elif '"next"' in pkg_content:
                framework = "nextjs"
        elif (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            reqs = ""
            if (project_path / "requirements.txt").exists():
                reqs = (project_path / "requirements.txt").read_text()
            if (project_path / "pyproject.toml").exists():
                reqs += (project_path / "pyproject.toml").read_text()
            
            if "fastapi" in reqs.lower():
                framework = "fastapi"
            elif "flask" in reqs.lower():
                framework = "flask"
            elif "django" in reqs.lower():
                framework = "django"
        elif (project_path / "Cargo.toml").exists():
            cargo = (project_path / "Cargo.toml").read_text()
            if "actix-web" in cargo:
                framework = "actix"
            elif "axum" in cargo:
                framework = "axum"
    
    output_path = output_path or str(project_path / "docs" / "openapi.json")
    
    # Framework-specific commands
    commands = {
        "fastapi": {
            "cmd": ["python", "-c", """
import json
import sys
sys.path.insert(0, '.')
try:
    from main import app
except:
    try:
        from app.main import app
    except:
        from app import app
print(json.dumps(app.openapi()))
"""],
            "output_type": "stdout"
        },
        "nestjs": {
            "cmd": ["npx", "nestia", "swagger"],
            "output_type": "file",
            "output_file": "swagger.json"
        },
        "express": {
            "cmd": ["npx", "swagger-jsdoc", "-d", "swagger.config.js", "-o", output_path],
            "output_type": "file",
            "output_file": output_path
        }
    }
    
    if framework not in commands:
        # Try to find existing OpenAPI spec
        possible_specs = [
            project_path / "openapi.json",
            project_path / "openapi.yaml",
            project_path / "swagger.json",
            project_path / "swagger.yaml",
            project_path / "docs" / "openapi.json",
            project_path / "docs" / "swagger.json",
            project_path / "api" / "openapi.json",
        ]
        
        for spec_path in possible_specs:
            if spec_path.exists():
                return {
                    "success": True,
                    "existing_spec": str(spec_path),
                    "message": "Found existing OpenAPI specification"
                }
        
        return {
            "success": False,
            "error": f"Unsupported or unrecognized framework: {framework}",
            "detected_framework": framework,
            "supported": list(commands.keys())
        }
    
    cmd_info = commands[framework]
    
    try:
        result = subprocess.run(
            cmd_info["cmd"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if cmd_info["output_type"] == "stdout" and result.returncode == 0:
            spec = json.loads(result.stdout)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            if format == "json":
                Path(output_path).write_text(json.dumps(spec, indent=2))
            else:
                import yaml
                Path(output_path).write_text(yaml.dump(spec, default_flow_style=False))
            
            return {
                "success": True,
                "output_path": output_path,
                "info": {
                    "title": spec.get("info", {}).get("title"),
                    "version": spec.get("info", {}).get("version"),
                    "paths_count": len(spec.get("paths", {}))
                }
            }
        elif result.returncode == 0:
            return {
                "success": True,
                "output_path": cmd_info.get("output_file", output_path),
                "command": " ".join(cmd_info["cmd"])
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "command": " ".join(cmd_info["cmd"])
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse OpenAPI spec: {e}"}
    except FileNotFoundError as e:
        return {"success": False, "error": f"Command not found: {e}"}


def update_readme(
    project_path: str = ".",
    sections: list[str] | None = None,
    readme_path: str = "README.md"
) -> dict[str, Any]:
    """Update README with project information from code."""
    project_path = Path(project_path).resolve()
    readme_file = project_path / readme_path
    
    if not readme_file.exists():
        return {"success": False, "error": f"README not found: {readme_path}"}
    
    sections = sections or ["installation", "usage", "api"]
    readme_content = readme_file.read_text()
    updates = []
    
    # Auto-generate sections based on project
    generated_sections = {}
    
    # Installation section
    if "installation" in sections:
        install_content = []
        
        if (project_path / "package.json").exists():
            pkg = json.loads((project_path / "package.json").read_text())
            pkg_name = pkg.get("name", "package")
            install_content.append(f"```bash\nnpm install {pkg_name}\n# or\nyarn add {pkg_name}\n```")
        
        if (project_path / "requirements.txt").exists():
            install_content.append("```bash\npip install -r requirements.txt\n```")
        
        if (project_path / "pyproject.toml").exists():
            install_content.append("```bash\npip install .\n# or\npoetry install\n```")
        
        if (project_path / "Cargo.toml").exists():
            install_content.append("```bash\ncargo build\n```")
        
        if install_content:
            generated_sections["installation"] = "\n\n".join(install_content)
    
    # Scripts section from package.json
    if "scripts" in sections and (project_path / "package.json").exists():
        pkg = json.loads((project_path / "package.json").read_text())
        scripts = pkg.get("scripts", {})
        if scripts:
            script_lines = ["| Script | Command |", "|--------|---------|"]
            for name, cmd in list(scripts.items())[:10]:
                script_lines.append(f"| `{name}` | `{cmd[:50]}{'...' if len(cmd) > 50 else ''}` |")
            generated_sections["scripts"] = "\n".join(script_lines)
    
    # API endpoints from routes
    if "api" in sections:
        endpoints = []
        
        # Scan for route definitions
        route_patterns = [
            r'@(app|router)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',  # FastAPI/Flask
            r'(router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',  # Express
        ]
        
        for py_file in project_path.rglob("*.py"):
            if any(d in py_file.parts for d in EXCLUDED_DIRS):
                continue
            try:
                content = py_file.read_text()
                for pattern in route_patterns:
                    for match in re.finditer(pattern, content):
                        method = match.group(2).upper() if len(match.groups()) >= 2 else match.group(1).upper()
                        path = match.group(3) if len(match.groups()) >= 3 else match.group(2)
                        endpoints.append({"method": method, "path": path})
            except:
                continue
        
        if endpoints:
            endpoint_lines = ["| Method | Endpoint |", "|--------|----------|"]
            for ep in endpoints[:20]:
                endpoint_lines.append(f"| `{ep['method']}` | `{ep['path']}` |")
            generated_sections["api"] = "\n".join(endpoint_lines)
    
    # Update README with generated sections
    for section_name, content in generated_sections.items():
        # Look for existing section markers
        section_pattern = rf'(<!--\s*{section_name}:start\s*-->)(.*?)(<!--\s*{section_name}:end\s*-->)'
        
        if re.search(section_pattern, readme_content, re.DOTALL | re.IGNORECASE):
            readme_content = re.sub(
                section_pattern,
                rf'\1\n{content}\n\3',
                readme_content,
                flags=re.DOTALL | re.IGNORECASE
            )
            updates.append({
                "section": section_name,
                "action": "updated",
                "content_preview": content[:100]
            })
    
    if updates:
        readme_file.write_text(readme_content)
    
    return {
        "success": True,
        "readme_path": str(readme_file),
        "updates": updates,
        "generated_sections": list(generated_sections.keys()),
        "hint": "Use <!-- section:start --> and <!-- section:end --> markers to enable auto-updates"
    }


def generate_type_docs(
    project_path: str = ".",
    tool: str = "auto",
    output_path: str | None = None
) -> dict[str, Any]:
    """Generate type documentation using TypeDoc, Sphinx, or similar tools."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect tool
    if tool == "auto":
        if (project_path / "tsconfig.json").exists():
            tool = "typedoc"
        elif (project_path / "docs" / "conf.py").exists():
            tool = "sphinx"
        elif (project_path / "pyproject.toml").exists() or (project_path / "setup.py").exists():
            tool = "sphinx"
        elif (project_path / "Cargo.toml").exists():
            tool = "rustdoc"
        elif (project_path / "go.mod").exists():
            tool = "godoc"
        else:
            return {"success": False, "error": "Could not auto-detect documentation tool"}
    
    output_path = output_path or str(project_path / "docs" / "api")
    
    commands = {
        "typedoc": {
            "cmd": ["npx", "typedoc", "--out", output_path, "src"],
            "install": "npm install --save-dev typedoc"
        },
        "sphinx": {
            "cmd": ["sphinx-build", "-b", "html", "docs", output_path],
            "install": "pip install sphinx"
        },
        "rustdoc": {
            "cmd": ["cargo", "doc", "--no-deps", "--document-private-items"],
            "output_path": "target/doc"
        },
        "godoc": {
            "cmd": ["go", "doc", "-all", "."],
            "output_type": "stdout"
        },
        "jsdoc": {
            "cmd": ["npx", "jsdoc", "-r", "src", "-d", output_path],
            "install": "npm install --save-dev jsdoc"
        }
    }
    
    if tool not in commands:
        return {"success": False, "error": f"Unknown tool: {tool}", "supported": list(commands.keys())}
    
    cmd_info = commands[tool]
    
    try:
        # Create output directory
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        result = subprocess.run(
            cmd_info["cmd"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            actual_output = cmd_info.get("output_path", output_path)
            return {
                "success": True,
                "tool": tool,
                "output_path": actual_output,
                "message": "Documentation generated successfully"
            }
        else:
            return {
                "success": False,
                "tool": tool,
                "error": result.stderr,
                "install_hint": cmd_info.get("install")
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Tool '{tool}' not found",
            "install_hint": cmd_info.get("install")
        }


def check_doc_coverage(
    project_path: str = ".",
    include_private: bool = False,
    languages: list[str] | None = None
) -> dict[str, Any]:
    """Find undocumented functions, classes, and methods."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    languages = languages or ["python", "javascript", "typescript"]
    
    undocumented = []
    documented = 0
    total = 0
    
    # Python docstring patterns
    if "python" in languages:
        py_func_pattern = r'^(\s*)def\s+(\w+)\s*\([^)]*\)\s*(?:->[^:]+)?:'
        py_class_pattern = r'^(\s*)class\s+(\w+)\s*(?:\([^)]*\))?:'
        
        for py_file in project_path.rglob("*.py"):
            if any(d in py_file.parts for d in EXCLUDED_DIRS):
                continue
            
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                rel_path = str(py_file.relative_to(project_path))
                
                for i, line in enumerate(lines):
                    # Check functions
                    func_match = re.match(py_func_pattern, line)
                    if func_match:
                        indent, name = func_match.groups()
                        
                        # Skip private functions if not included
                        if name.startswith('_') and not include_private:
                            continue
                        
                        total += 1
                        
                        # Check for docstring on next non-empty line
                        has_docstring = False
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            if next_line.startswith('"""') or next_line.startswith("'''"):
                                has_docstring = True
                                break
                            elif next_line and not next_line.startswith('#'):
                                break
                        
                        if has_docstring:
                            documented += 1
                        else:
                            undocumented.append({
                                "file": rel_path,
                                "line": i + 1,
                                "type": "function",
                                "name": name
                            })
                    
                    # Check classes
                    class_match = re.match(py_class_pattern, line)
                    if class_match:
                        indent, name = class_match.groups()
                        
                        if name.startswith('_') and not include_private:
                            continue
                        
                        total += 1
                        
                        has_docstring = False
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            if next_line.startswith('"""') or next_line.startswith("'''"):
                                has_docstring = True
                                break
                            elif next_line and not next_line.startswith('#'):
                                break
                        
                        if has_docstring:
                            documented += 1
                        else:
                            undocumented.append({
                                "file": rel_path,
                                "line": i + 1,
                                "type": "class",
                                "name": name
                            })
                            
            except:
                continue
    
    # JavaScript/TypeScript JSDoc patterns
    if "javascript" in languages or "typescript" in languages:
        js_func_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\('
        js_method_pattern = r'^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*{'
        js_arrow_pattern = r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>'
        
        extensions = []
        if "javascript" in languages:
            extensions.extend([".js", ".jsx"])
        if "typescript" in languages:
            extensions.extend([".ts", ".tsx"])
        
        for ext in extensions:
            for js_file in project_path.rglob(f"*{ext}"):
                if any(d in js_file.parts for d in EXCLUDED_DIRS):
                    continue
                if js_file.suffix == '.d.ts':
                    continue
                
                try:
                    content = js_file.read_text()
                    lines = content.split('\n')
                    rel_path = str(js_file.relative_to(project_path))
                    
                    for i, line in enumerate(lines):
                        for pattern in [js_func_pattern, js_arrow_pattern]:
                            match = re.search(pattern, line)
                            if match:
                                name = match.group(1)
                                
                                if name.startswith('_') and not include_private:
                                    continue
                                
                                total += 1
                                
                                # Check for JSDoc comment before
                                has_jsdoc = False
                                for j in range(max(0, i - 10), i):
                                    if '/**' in lines[j] or '@param' in lines[j] or '@returns' in lines[j]:
                                        has_jsdoc = True
                                        break
                                
                                if has_jsdoc:
                                    documented += 1
                                else:
                                    undocumented.append({
                                        "file": rel_path,
                                        "line": i + 1,
                                        "type": "function",
                                        "name": name
                                    })
                                break
                                
                except:
                    continue
    
    coverage = (documented / total * 100) if total > 0 else 100
    
    return {
        "success": True,
        "total_items": total,
        "documented": documented,
        "undocumented_count": len(undocumented),
        "coverage_percent": round(coverage, 1),
        "undocumented": undocumented[:50],  # Limit results
        "truncated": len(undocumented) > 50
    }


def validate_links(
    project_path: str = ".",
    include_external: bool = False,
    timeout: int = 5
) -> dict[str, Any]:
    """Check for broken links in documentation files."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Find all markdown and RST files
    doc_files = []
    for pattern in ["*.md", "*.rst", "*.mdx"]:
        doc_files.extend(project_path.rglob(pattern))
    
    # Filter out excluded directories
    doc_files = [f for f in doc_files if not any(d in f.parts for d in EXCLUDED_DIRS)]
    
    results = {
        "files_checked": len(doc_files),
        "links_checked": 0,
        "broken_links": [],
        "warnings": []
    }
    
    # Link patterns
    md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    for doc_file in doc_files:
        try:
            content = doc_file.read_text()
            rel_path = str(doc_file.relative_to(project_path))
            
            for match in re.finditer(md_link_pattern, content):
                link_text, link_url = match.groups()
                line_num = content[:match.start()].count('\n') + 1
                
                results["links_checked"] += 1
                
                # Skip anchors
                if link_url.startswith('#'):
                    continue
                
                # Skip mailto links
                if link_url.startswith('mailto:'):
                    continue
                
                # Check external links
                if link_url.startswith(('http://', 'https://')):
                    if include_external:
                        try:
                            req = urllib.request.Request(
                                link_url,
                                method='HEAD',
                                headers={'User-Agent': 'Mozilla/5.0 LinkChecker'}
                            )
                            urllib.request.urlopen(req, timeout=timeout)
                        except urllib.error.HTTPError as e:
                            if e.code >= 400:
                                results["broken_links"].append({
                                    "file": rel_path,
                                    "line": line_num,
                                    "link": link_url,
                                    "text": link_text,
                                    "error": f"HTTP {e.code}"
                                })
                        except Exception as e:
                            results["broken_links"].append({
                                "file": rel_path,
                                "line": line_num,
                                "link": link_url,
                                "text": link_text,
                                "error": str(e)[:50]
                            })
                else:
                    # Check local links
                    # Handle relative paths and anchors
                    link_path = link_url.split('#')[0]
                    if not link_path:
                        continue
                    
                    # Resolve relative to doc file's directory
                    if link_path.startswith('/'):
                        target = project_path / link_path[1:]
                    else:
                        target = doc_file.parent / link_path
                    
                    if not target.exists():
                        results["broken_links"].append({
                            "file": rel_path,
                            "line": line_num,
                            "link": link_url,
                            "text": link_text,
                            "error": "File not found"
                        })
                        
        except Exception as e:
            results["warnings"].append({
                "file": rel_path,
                "error": str(e)
            })
    
    results["success"] = True
    results["has_broken_links"] = len(results["broken_links"]) > 0
    
    return results


# MCP Server Implementation
TOOLS = [
    {
        "name": "generate_api_docs",
        "description": "Generate OpenAPI/Swagger documentation from code (supports FastAPI, Express, NestJS)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "framework": {
                    "type": "string",
                    "description": "Framework (auto, fastapi, express, nestjs, flask)",
                    "default": "auto"
                },
                "output_path": {
                    "type": "string",
                    "description": "Output path for the generated spec"
                },
                "format": {
                    "type": "string",
                    "description": "Output format (json, yaml)",
                    "default": "json"
                }
            }
        }
    },
    {
        "name": "update_readme",
        "description": "Update README with project information from code",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "sections": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sections to update (installation, usage, api, scripts)"
                },
                "readme_path": {
                    "type": "string",
                    "description": "Path to README file",
                    "default": "README.md"
                }
            }
        }
    },
    {
        "name": "generate_type_docs",
        "description": "Generate type documentation using TypeDoc, Sphinx, or similar tools",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "tool": {
                    "type": "string",
                    "description": "Documentation tool (auto, typedoc, sphinx, rustdoc, godoc, jsdoc)",
                    "default": "auto"
                },
                "output_path": {
                    "type": "string",
                    "description": "Output directory for documentation"
                }
            }
        }
    },
    {
        "name": "check_doc_coverage",
        "description": "Find undocumented functions, classes, and methods",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "include_private": {
                    "type": "boolean",
                    "description": "Include private/internal items",
                    "default": False
                },
                "languages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Languages to check (python, javascript, typescript)"
                }
            }
        }
    },
    {
        "name": "validate_links",
        "description": "Check for broken links in documentation files",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "include_external": {
                    "type": "boolean",
                    "description": "Check external (http/https) links",
                    "default": False
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds for external link checks",
                    "default": 5
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "generate_api_docs":
        return generate_api_docs(**arguments)
    elif name == "update_readme":
        return update_readme(**arguments)
    elif name == "generate_type_docs":
        return generate_type_docs(**arguments)
    elif name == "check_doc_coverage":
        return check_doc_coverage(**arguments)
    elif name == "validate_links":
        return validate_links(**arguments)
    else:
        return {"error": f"Unknown tool: {name}"}


def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {
                            "name": "documentation-generator-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})
                result = handle_tool_call(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            elif method == "notifications/initialized":
                continue
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
