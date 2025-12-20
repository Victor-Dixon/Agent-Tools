#!/usr/bin/env python3
"""
MCP Server for V2 Compliance Checking
Exposes V2 compliance validation capabilities via Model Context Protocol
"""

import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def count_lines(file_path: str) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception:
        return 0


def count_function_lines(file_path: str, function_name: Optional[str] = None) -> Dict[str, Any]:
    """Count lines in a function."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_start = node.lineno
                func_end = node.end_lineno if hasattr(
                    node, 'end_lineno') else node.lineno
                func_lines = func_end - func_start + 1

                if not function_name or node.name == function_name:
                    functions.append({
                        "name": node.name,
                        "lines": func_lines,
                        "start_line": func_start,
                        "end_line": func_end,
                    })

        if function_name:
            func = next(
                (f for f in functions if f["name"] == function_name), None)
            if func:
                return {"success": True, "function": func}
            return {"success": False, "error": f"Function '{function_name}' not found"}

        return {"success": True, "functions": functions, "count": len(functions)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_v2_compliance(
    file_path: str, rules_file: Optional[str] = None
) -> Dict[str, Any]:
    """Check a file for V2 compliance."""
    project_root = Path(__file__).parent.parent

    # Load rules
    if rules_file:
        rules_path = Path(rules_file)
    else:
        rules_path = project_root / "config" / "v2_rules.yaml"

    rules = None
    if rules_path.exists() and HAS_YAML:
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
        except Exception:
            pass

    # Default limits
    max_file_lines = 300
    max_class_lines = 200
    max_function_lines = 30

    if rules and 'file_limits' in rules:
        max_file_lines = rules['file_limits'].get('max_lines', 300)
        max_class_lines = rules['file_limits'].get('max_class_lines', 200)
        max_function_lines = rules['file_limits'].get('max_function_lines', 30)

    file_path_obj = Path(file_path)
    if not file_path_obj.is_absolute():
        file_path_obj = project_root / file_path

    if not file_path_obj.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    violations = []
    line_count = count_lines(str(file_path_obj))

    # Check file size
    if line_count > max_file_lines:
        violations.append({
            "type": "file_size",
            "severity": "HIGH",
            "message": f"File exceeds {max_file_lines} line limit: {line_count} lines",
            "current": line_count,
            "limit": max_file_lines,
        })

    # Check function sizes
    if file_path_obj.suffix == '.py':
        func_result = count_function_lines(str(file_path_obj))
        if func_result.get("success") and "functions" in func_result:
            for func in func_result["functions"]:
                if func["lines"] > max_function_lines:
                    violations.append({
                        "type": "function_size",
                        "severity": "MEDIUM",
                        "message": f"Function '{func['name']}' exceeds {max_function_lines} line limit: {func['lines']} lines",
                        "function": func["name"],
                        "current": func["lines"],
                        "limit": max_function_lines,
                    })

    # Check exceptions
    exceptions_file = project_root / "docs" / "V2_COMPLIANCE_EXCEPTIONS.md"
    is_exception = False
    exception_info = None

    if exceptions_file.exists():
        content = exceptions_file.read_text(encoding='utf-8')
        # Simple check if file path appears in exceptions
        relative_path = file_path_obj.relative_to(
            project_root) if file_path_obj.is_relative_to(project_root) else file_path_obj
        if str(relative_path).replace('\\', '/') in content:
            is_exception = True
            exception_info = "File is listed in V2_COMPLIANCE_EXCEPTIONS.md"

    return {
        "success": True,
        "file_path": str(file_path_obj),
        "line_count": line_count,
        "max_file_lines": max_file_lines,
        "is_compliant": len(violations) == 0,
        "is_exception": is_exception,
        "exception_info": exception_info,
        "violations": violations,
        "violations_count": len(violations),
    }


def validate_file_size(file_path: str, max_lines: int = 300) -> Dict[str, Any]:
    """Validate file size against limit."""
    file_path_obj = Path(file_path)
    project_root = Path(__file__).parent.parent

    if not file_path_obj.is_absolute():
        file_path_obj = project_root / file_path

    if not file_path_obj.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    line_count = count_lines(str(file_path_obj))
    is_compliant = line_count <= max_lines

    return {
        "success": True,
        "file_path": str(file_path_obj),
        "line_count": line_count,
        "max_lines": max_lines,
        "is_compliant": is_compliant,
        "exceeds_by": line_count - max_lines if not is_compliant else 0,
    }


def check_function_size(
    file_path: str, function_name: Optional[str] = None, max_lines: int = 30
) -> Dict[str, Any]:
    """Check function size against limit."""
    file_path_obj = Path(file_path)
    project_root = Path(__file__).parent.parent

    if not file_path_obj.is_absolute():
        file_path_obj = project_root / file_path

    if not file_path_obj.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if file_path_obj.suffix != '.py':
        return {"success": False, "error": "Function checking only available for Python files"}

    result = count_function_lines(str(file_path_obj), function_name)

    if not result.get("success"):
        return result

    if function_name:
        # Single function check
        func = result.get("function")
        if func:
            is_compliant = func["lines"] <= max_lines
            return {
                "success": True,
                "function": func["name"],
                "line_count": func["lines"],
                "max_lines": max_lines,
                "is_compliant": is_compliant,
                "exceeds_by": func["lines"] - max_lines if not is_compliant else 0,
            }
        return result

    # All functions check
    functions = result.get("functions", [])
    violations = [f for f in functions if f["lines"] > max_lines]

    return {
        "success": True,
        "file_path": str(file_path_obj),
        "functions_count": len(functions),
        "violations_count": len(violations),
        "max_lines": max_lines,
        "violations": [
            {
                "function": f["name"],
                "line_count": f["lines"],
                "exceeds_by": f["lines"] - max_lines,
            }
            for f in violations
        ],
    }


def get_v2_exceptions() -> Dict[str, Any]:
    """Get list of approved V2 compliance exceptions."""
    project_root = Path(__file__).parent.parent
    exceptions_file = project_root / "docs" / "V2_COMPLIANCE_EXCEPTIONS.md"

    if not exceptions_file.exists():
        return {"success": False, "error": "V2_COMPLIANCE_EXCEPTIONS.md not found"}

    try:
        content = exceptions_file.read_text(encoding='utf-8')

        # Parse exceptions (simple extraction)
        exceptions = []
        current_exception = None

        for line in content.split('\n'):
            if line.strip().startswith('#### `') and '` - ' in line:
                # Extract file path and line count
                parts = line.split('` - ')
                if len(parts) == 2:
                    file_path = parts[0].replace('#### `', '').strip()
                    line_info = parts[1].strip()
                    if 'lines' in line_info:
                        line_count = int(line_info.split()[0])
                        current_exception = {
                            "file_path": file_path,
                            "line_count": line_count,
                            "reason": "",
                        }
                        exceptions.append(current_exception)
            elif current_exception and line.strip().startswith('**Reason:**'):
                current_exception["reason"] = line.replace(
                    '**Reason:**', '').strip()

        return {
            "success": True,
            "exceptions_count": len(exceptions),
            "exceptions": exceptions,
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
                            "check_v2_compliance": {
                                "description": "Check a file for V2 compliance",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {
                                            "type": "string",
                                            "description": "File path to check (relative or absolute)",
                                        },
                                        "rules_file": {
                                            "type": "string",
                                            "description": "Optional: Path to V2 rules YAML file",
                                        },
                                    },
                                    "required": ["file_path"],
                                },
                            },
                            "validate_file_size": {
                                "description": "Validate file size against V2 limit",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {
                                            "type": "string",
                                            "description": "File path to check",
                                        },
                                        "max_lines": {
                                            "type": "integer",
                                            "default": 300,
                                            "description": "Maximum lines allowed (default: 300)",
                                        },
                                    },
                                    "required": ["file_path"],
                                },
                            },
                            "check_function_size": {
                                "description": "Check function size against V2 limit",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {
                                            "type": "string",
                                            "description": "Python file path",
                                        },
                                        "function_name": {
                                            "type": "string",
                                            "description": "Optional: Specific function name to check",
                                        },
                                        "max_lines": {
                                            "type": "integer",
                                            "default": 30,
                                            "description": "Maximum lines per function (default: 30)",
                                        },
                                    },
                                    "required": ["file_path"],
                                },
                            },
                            "get_v2_exceptions": {
                                "description": "Get list of approved V2 compliance exceptions",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "v2-compliance-server", "version": "1.0.0"},
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

                if tool_name == "check_v2_compliance":
                    result = check_v2_compliance(**arguments)
                elif tool_name == "validate_file_size":
                    result = validate_file_size(**arguments)
                elif tool_name == "check_function_size":
                    result = check_function_size(**arguments)
                elif tool_name == "get_v2_exceptions":
                    result = get_v2_exceptions()
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

