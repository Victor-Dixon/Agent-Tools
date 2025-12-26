#!/usr/bin/env python3
"""
Code Quality Server - MCP server for automated code improvements.

Tools:
- run_linter: Run ESLint/Ruff/etc.
- auto_fix_lint: Auto-fix linter issues
- format_code: Run Prettier/Black
- check_types: TypeScript/mypy type checking
- find_dead_code: Find unused exports/functions
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

EXCLUDED_DIRS = {'node_modules', '.git', 'vendor', 'venv', '.venv', '__pycache__', 'dist', 'build', '.next', 'coverage'}


def detect_linter(project_path: Path) -> list[str]:
    """Detect available linters in the project."""
    linters = []
    
    # JavaScript/TypeScript linters
    if (project_path / "package.json").exists():
        pkg_content = (project_path / "package.json").read_text()
        if '"eslint"' in pkg_content:
            linters.append("eslint")
        if '"biome"' in pkg_content or '"@biomejs/biome"' in pkg_content:
            linters.append("biome")
        if '"oxlint"' in pkg_content:
            linters.append("oxlint")
    
    if (project_path / ".eslintrc").exists() or \
       (project_path / ".eslintrc.js").exists() or \
       (project_path / ".eslintrc.json").exists() or \
       (project_path / "eslint.config.js").exists() or \
       (project_path / "eslint.config.mjs").exists():
        if "eslint" not in linters:
            linters.append("eslint")
    
    # Python linters
    if (project_path / "pyproject.toml").exists():
        pyproject = (project_path / "pyproject.toml").read_text()
        if "[tool.ruff]" in pyproject or "ruff" in pyproject:
            linters.append("ruff")
        if "[tool.flake8]" in pyproject:
            linters.append("flake8")
        if "[tool.pylint]" in pyproject:
            linters.append("pylint")
    
    if (project_path / "ruff.toml").exists() or (project_path / ".ruff.toml").exists():
        if "ruff" not in linters:
            linters.append("ruff")
    
    if (project_path / ".flake8").exists():
        if "flake8" not in linters:
            linters.append("flake8")
    
    # Rust linter
    if (project_path / "Cargo.toml").exists():
        linters.append("clippy")
    
    # Go linter
    if (project_path / "go.mod").exists():
        linters.append("golangci-lint")
    
    return linters


def run_linter(
    project_path: str = ".",
    linter: str = "auto",
    files: list[str] | None = None,
    config: str | None = None
) -> dict[str, Any]:
    """Run linter and return issues found."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    available_linters = detect_linter(project_path)
    
    if linter == "auto":
        if not available_linters:
            return {"success": False, "error": "No linter detected", "hint": "Install eslint, ruff, or another linter"}
        linter = available_linters[0]
    
    commands = {
        "eslint": {
            "cmd": ["npx", "eslint", "--format", "json"],
            "files_default": ["."],
            "parse_json": True
        },
        "biome": {
            "cmd": ["npx", "@biomejs/biome", "lint", "--reporter", "json"],
            "files_default": ["."],
            "parse_json": True
        },
        "oxlint": {
            "cmd": ["npx", "oxlint", "--format", "json"],
            "files_default": ["."],
            "parse_json": True
        },
        "ruff": {
            "cmd": ["ruff", "check", "--output-format", "json"],
            "files_default": ["."],
            "parse_json": True
        },
        "flake8": {
            "cmd": ["flake8", "--format", "json"],
            "files_default": ["."],
            "parse_json": True
        },
        "pylint": {
            "cmd": ["pylint", "--output-format", "json"],
            "files_default": ["."],
            "parse_json": True
        },
        "clippy": {
            "cmd": ["cargo", "clippy", "--message-format", "json"],
            "files_default": [],
            "parse_json": True
        },
        "golangci-lint": {
            "cmd": ["golangci-lint", "run", "--out-format", "json"],
            "files_default": ["./..."],
            "parse_json": True
        }
    }
    
    if linter not in commands:
        return {"success": False, "error": f"Unknown linter: {linter}", "supported": list(commands.keys())}
    
    cmd_info = commands[linter]
    cmd = cmd_info["cmd"].copy()
    
    if config:
        if linter == "eslint":
            cmd.extend(["--config", config])
        elif linter == "ruff":
            cmd.extend(["--config", config])
    
    target_files = files or cmd_info["files_default"]
    cmd.extend(target_files)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        issues = []
        
        if cmd_info["parse_json"] and result.stdout:
            try:
                lint_output = json.loads(result.stdout)
                
                # Parse based on linter format
                if linter == "eslint":
                    for file_result in lint_output:
                        for msg in file_result.get("messages", []):
                            issues.append({
                                "file": file_result.get("filePath", "").replace(str(project_path) + "/", ""),
                                "line": msg.get("line", 0),
                                "column": msg.get("column", 0),
                                "severity": "error" if msg.get("severity") == 2 else "warning",
                                "message": msg.get("message", ""),
                                "rule": msg.get("ruleId", "")
                            })
                
                elif linter == "ruff":
                    for issue in lint_output:
                        issues.append({
                            "file": issue.get("filename", "").replace(str(project_path) + "/", ""),
                            "line": issue.get("location", {}).get("row", 0),
                            "column": issue.get("location", {}).get("column", 0),
                            "severity": "error",
                            "message": issue.get("message", ""),
                            "rule": issue.get("code", "")
                        })
                
                elif linter == "pylint":
                    for issue in lint_output:
                        issues.append({
                            "file": issue.get("path", ""),
                            "line": issue.get("line", 0),
                            "column": issue.get("column", 0),
                            "severity": issue.get("type", "warning"),
                            "message": issue.get("message", ""),
                            "rule": issue.get("symbol", "")
                        })
                        
            except json.JSONDecodeError:
                # Fallback to raw output
                pass
        
        # Count by severity
        error_count = len([i for i in issues if i.get("severity") == "error"])
        warning_count = len([i for i in issues if i.get("severity") == "warning"])
        
        return {
            "success": True,
            "linter": linter,
            "issues": issues[:100],  # Limit results
            "total_issues": len(issues),
            "errors": error_count,
            "warnings": warning_count,
            "exit_code": result.returncode,
            "has_issues": len(issues) > 0,
            "truncated": len(issues) > 100
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Linter timed out"}
    except FileNotFoundError:
        return {"success": False, "error": f"Linter '{linter}' not found"}


def auto_fix_lint(
    project_path: str = ".",
    linter: str = "auto",
    files: list[str] | None = None,
    dry_run: bool = False
) -> dict[str, Any]:
    """Auto-fix linter issues where possible."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    available_linters = detect_linter(project_path)
    
    if linter == "auto":
        if not available_linters:
            return {"success": False, "error": "No linter detected"}
        linter = available_linters[0]
    
    fix_commands = {
        "eslint": ["npx", "eslint", "--fix"],
        "biome": ["npx", "@biomejs/biome", "lint", "--apply"],
        "ruff": ["ruff", "check", "--fix"],
        "clippy": ["cargo", "clippy", "--fix", "--allow-dirty"],
        "golangci-lint": ["golangci-lint", "run", "--fix"],
    }
    
    if linter not in fix_commands:
        return {"success": False, "error": f"Auto-fix not supported for: {linter}"}
    
    cmd = fix_commands[linter].copy()
    
    if dry_run and linter == "ruff":
        cmd.append("--diff")
    elif dry_run and linter == "eslint":
        # ESLint doesn't have a dry-run, so run without --fix
        cmd = ["npx", "eslint", "--format", "stylish"]
    
    target_files = files or ["."]
    cmd.extend(target_files)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "linter": linter,
            "dry_run": dry_run,
            "command": " ".join(cmd),
            "stdout": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Auto-fix timed out"}
    except FileNotFoundError:
        return {"success": False, "error": f"Linter '{linter}' not found"}


def format_code(
    project_path: str = ".",
    formatter: str = "auto",
    files: list[str] | None = None,
    check_only: bool = False
) -> dict[str, Any]:
    """Run code formatter (Prettier, Black, etc.)."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect formatter
    if formatter == "auto":
        if (project_path / "package.json").exists():
            pkg = (project_path / "package.json").read_text()
            if '"prettier"' in pkg:
                formatter = "prettier"
            elif '"biome"' in pkg or '"@biomejs/biome"' in pkg:
                formatter = "biome"
        
        if formatter == "auto":
            if (project_path / "pyproject.toml").exists():
                pyproject = (project_path / "pyproject.toml").read_text()
                if "[tool.black]" in pyproject or "black" in pyproject:
                    formatter = "black"
                elif "ruff" in pyproject:
                    formatter = "ruff-format"
        
        if formatter == "auto":
            if (project_path / "Cargo.toml").exists():
                formatter = "rustfmt"
            elif (project_path / "go.mod").exists():
                formatter = "gofmt"
        
        if formatter == "auto":
            return {"success": False, "error": "No formatter detected"}
    
    format_commands = {
        "prettier": {
            "format": ["npx", "prettier", "--write"],
            "check": ["npx", "prettier", "--check"],
            "default_files": ["."]
        },
        "biome": {
            "format": ["npx", "@biomejs/biome", "format", "--write"],
            "check": ["npx", "@biomejs/biome", "format"],
            "default_files": ["."]
        },
        "black": {
            "format": ["black"],
            "check": ["black", "--check"],
            "default_files": ["."]
        },
        "ruff-format": {
            "format": ["ruff", "format"],
            "check": ["ruff", "format", "--check"],
            "default_files": ["."]
        },
        "rustfmt": {
            "format": ["cargo", "fmt"],
            "check": ["cargo", "fmt", "--check"],
            "default_files": []
        },
        "gofmt": {
            "format": ["gofmt", "-w"],
            "check": ["gofmt", "-d"],
            "default_files": ["."]
        },
    }
    
    if formatter not in format_commands:
        return {"success": False, "error": f"Unknown formatter: {formatter}", "supported": list(format_commands.keys())}
    
    cmd_info = format_commands[formatter]
    cmd = cmd_info["check"].copy() if check_only else cmd_info["format"].copy()
    
    target_files = files or cmd_info["default_files"]
    cmd.extend(target_files)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            "success": result.returncode == 0,
            "formatter": formatter,
            "check_only": check_only,
            "command": " ".join(cmd),
            "stdout": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "exit_code": result.returncode,
            "needs_formatting": result.returncode != 0 if check_only else None
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Formatter timed out"}
    except FileNotFoundError:
        return {"success": False, "error": f"Formatter '{formatter}' not found"}


def check_types(
    project_path: str = ".",
    checker: str = "auto",
    strict: bool = False
) -> dict[str, Any]:
    """Run type checker (TypeScript, mypy, etc.)."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect type checker
    if checker == "auto":
        if (project_path / "tsconfig.json").exists():
            checker = "typescript"
        elif (project_path / "pyproject.toml").exists() or (project_path / "mypy.ini").exists():
            checker = "mypy"
        elif (project_path / "pyrightconfig.json").exists():
            checker = "pyright"
        else:
            return {"success": False, "error": "No type checker configuration found"}
    
    type_commands = {
        "typescript": {
            "cmd": ["npx", "tsc", "--noEmit"],
            "strict_flag": "--strict"
        },
        "mypy": {
            "cmd": ["mypy", "."],
            "strict_flag": "--strict"
        },
        "pyright": {
            "cmd": ["npx", "pyright"],
            "strict_flag": None  # Configured in pyrightconfig.json
        },
    }
    
    if checker not in type_commands:
        return {"success": False, "error": f"Unknown type checker: {checker}"}
    
    cmd_info = type_commands[checker]
    cmd = cmd_info["cmd"].copy()
    
    if strict and cmd_info["strict_flag"]:
        cmd.append(cmd_info["strict_flag"])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        # Parse type errors
        errors = []
        output = result.stdout + result.stderr
        
        if checker == "typescript":
            # Parse TypeScript errors
            error_pattern = r'([^(]+)\((\d+),(\d+)\): error (\w+): (.+)'
            for match in re.finditer(error_pattern, output):
                errors.append({
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "column": int(match.group(3)),
                    "code": match.group(4),
                    "message": match.group(5)
                })
        
        elif checker == "mypy":
            # Parse mypy errors
            error_pattern = r'([^:]+):(\d+): error: (.+)'
            for match in re.finditer(error_pattern, output):
                errors.append({
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "message": match.group(3)
                })
        
        return {
            "success": result.returncode == 0,
            "checker": checker,
            "errors": errors[:100],
            "total_errors": len(errors),
            "output": output[-3000:] if len(output) > 3000 else output,
            "exit_code": result.returncode,
            "has_type_errors": len(errors) > 0
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Type checking timed out"}
    except FileNotFoundError:
        return {"success": False, "error": f"Type checker '{checker}' not found"}


def find_dead_code(
    project_path: str = ".",
    language: str = "auto",
    include_tests: bool = False
) -> dict[str, Any]:
    """Find unused exports, functions, and variables."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect language
    if language == "auto":
        if (project_path / "package.json").exists():
            language = "javascript"
        elif (project_path / "pyproject.toml").exists() or list(project_path.glob("*.py")):
            language = "python"
        else:
            return {"success": False, "error": "Could not detect project language"}
    
    dead_code = []
    
    if language in ["javascript", "typescript"]:
        # Try ts-prune for TypeScript
        try:
            cmd = ["npx", "ts-prune"]
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 or result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('('):
                        # Parse: file:line - export name
                        match = re.match(r'(.+):(\d+) - (.+)', line)
                        if match:
                            file_path = match.group(1)
                            if not include_tests and ('test' in file_path or 'spec' in file_path):
                                continue
                            dead_code.append({
                                "file": file_path,
                                "line": int(match.group(2)),
                                "export": match.group(3),
                                "type": "unused_export"
                            })
            
            return {
                "success": True,
                "language": language,
                "tool": "ts-prune",
                "dead_code": dead_code[:50],
                "total": len(dead_code),
                "truncated": len(dead_code) > 50
            }
            
        except FileNotFoundError:
            # Try knip as alternative
            try:
                result = subprocess.run(
                    ["npx", "knip", "--reporter", "json"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.stdout:
                    try:
                        knip_output = json.loads(result.stdout)
                        for category, items in knip_output.items():
                            for item in items[:20]:
                                dead_code.append({
                                    "type": category,
                                    "item": str(item)[:100]
                                })
                    except:
                        pass
                
                return {
                    "success": True,
                    "language": language,
                    "tool": "knip",
                    "dead_code": dead_code[:50],
                    "total": len(dead_code)
                }
                
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "No dead code finder available. Install ts-prune or knip.",
                    "hint": "npm install -D ts-prune"
                }
    
    elif language == "python":
        # Try vulture for Python
        try:
            cmd = ["vulture", ".", "--min-confidence", "80"]
            if not include_tests:
                cmd.extend(["--exclude", "test,tests,*_test.py,test_*.py"])
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse vulture output
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Format: file:line: message (confidence%)
                    match = re.match(r'(.+):(\d+): (.+) \((\d+)% confidence\)', line)
                    if match:
                        dead_code.append({
                            "file": match.group(1).replace(str(project_path) + "/", ""),
                            "line": int(match.group(2)),
                            "message": match.group(3),
                            "confidence": int(match.group(4)),
                            "type": "unused_code"
                        })
            
            return {
                "success": True,
                "language": language,
                "tool": "vulture",
                "dead_code": dead_code[:50],
                "total": len(dead_code),
                "truncated": len(dead_code) > 50
            }
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": "vulture not found. Install with: pip install vulture"
            }
    
    return {"success": False, "error": f"Dead code detection not supported for: {language}"}


# MCP Server Implementation
TOOLS = [
    {
        "name": "run_linter",
        "description": "Run linter (ESLint, Ruff, etc.) and return issues found",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "linter": {
                    "type": "string",
                    "description": "Linter to use (auto, eslint, biome, ruff, flake8, pylint, clippy, golangci-lint)",
                    "default": "auto"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific files or directories to lint"
                },
                "config": {
                    "type": "string",
                    "description": "Path to linter configuration file"
                }
            }
        }
    },
    {
        "name": "auto_fix_lint",
        "description": "Auto-fix linter issues where possible",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "linter": {
                    "type": "string",
                    "description": "Linter to use",
                    "default": "auto"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific files to fix"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Show what would be fixed without making changes",
                    "default": False
                }
            }
        }
    },
    {
        "name": "format_code",
        "description": "Run code formatter (Prettier, Black, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "formatter": {
                    "type": "string",
                    "description": "Formatter to use (auto, prettier, biome, black, ruff-format, rustfmt, gofmt)",
                    "default": "auto"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific files to format"
                },
                "check_only": {
                    "type": "boolean",
                    "description": "Only check formatting without making changes",
                    "default": False
                }
            }
        }
    },
    {
        "name": "check_types",
        "description": "Run type checker (TypeScript, mypy, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "checker": {
                    "type": "string",
                    "description": "Type checker to use (auto, typescript, mypy, pyright)",
                    "default": "auto"
                },
                "strict": {
                    "type": "boolean",
                    "description": "Enable strict mode",
                    "default": False
                }
            }
        }
    },
    {
        "name": "find_dead_code",
        "description": "Find unused exports, functions, and variables",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "language": {
                    "type": "string",
                    "description": "Project language (auto, javascript, typescript, python)",
                    "default": "auto"
                },
                "include_tests": {
                    "type": "boolean",
                    "description": "Include test files in analysis",
                    "default": False
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "run_linter":
        return run_linter(**arguments)
    elif name == "auto_fix_lint":
        return auto_fix_lint(**arguments)
    elif name == "format_code":
        return format_code(**arguments)
    elif name == "check_types":
        return check_types(**arguments)
    elif name == "find_dead_code":
        return find_dead_code(**arguments)
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
                            "name": "code-quality-server",
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
