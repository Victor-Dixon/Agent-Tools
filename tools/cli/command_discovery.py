#!/usr/bin/env python3
"""
Command Discovery - CLI Consolidation
=====================================

Discovers CLI commands in tools directory and generates registry entries.
Scans for argparse, click, and main() patterns.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-05
V2 Compliant: Yes (<300 lines)
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"


class CommandDiscovery:
    """Discovers CLI commands in tools directory."""
    
    def __init__(self, tools_dir: Path = TOOLS_DIR):
        """Initialize command discovery."""
        self.tools_dir = tools_dir
        self.commands: List[Dict] = []
    
    def discover_commands(self) -> List[Dict]:
        """
        Discover all CLI commands in tools directory.
        
        Returns:
            List of command dictionaries with metadata
        """
        self.commands = []
        
        # Scan tools directory
        for py_file in self.tools_dir.rglob("*.py"):
            # Skip CLI framework files
            if "cli" in str(py_file) and "dispatcher" in str(py_file):
                continue
            
            # Skip __pycache__ and test files
            if "__pycache__" in str(py_file) or "test" in py_file.name.lower():
                continue
            
            try:
                command_info = self._analyze_file(py_file)
                if command_info:
                    self.commands.append(command_info)
            except Exception as e:
                logger.debug(f"Error analyzing {py_file}: {e}")
        
        return self.commands
    
    def _analyze_file(self, file_path: Path) -> Optional[Dict]:
        """
        Analyze a Python file for CLI command patterns.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Command info dict or None if not a CLI command
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None
        
        # Check for CLI indicators
        has_main = "__main__" in content or "def main(" in content
        has_argparse = "argparse" in content or "ArgumentParser" in content
        has_click = "@click" in content or "click.command" in content
        
        if not (has_main or has_argparse or has_click):
            return None
        
        # Extract command name from file path
        relative_path = file_path.relative_to(self.tools_dir)
        command_name = self._extract_command_name(file_path, content)
        
        # Determine module path
        module_path = self._get_module_path(relative_path)
        
        # Extract description if available
        description = self._extract_description(content)
        
        # Determine function name
        function_name = self._extract_function_name(content)
        
        return {
            "name": command_name,
            "module": module_path,
            "function": function_name,
            "file": str(relative_path),
            "description": description,
            "category": self._categorize_command(command_name, content)
        }
    
    def _extract_command_name(self, file_path: Path, content: str) -> str:
        """Extract command name from file."""
        # Use filename without extension
        name = file_path.stem
        
        # Remove common prefixes
        name = re.sub(r"^(run_|execute_|start_|stop_)", "", name)
        
        # Convert snake_case to kebab-case for CLI
        name = name.replace("_", "-")
        
        return name
    
    def _get_module_path(self, relative_path: Path) -> str:
        """Convert file path to module import path."""
        # Remove .py extension
        parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        
        # Convert to module path
        module_path = "tools." + ".".join(parts)
        
        return module_path
    
    def _extract_description(self, content: str) -> str:
        """Extract description from docstring or comments."""
        # Try to find module docstring
        try:
            tree = ast.parse(content)
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, ast.Str):
                    docstring = tree.body[0].value.s
                    # Extract first line
                    first_line = docstring.split("\n")[0].strip()
                    if first_line:
                        return first_line
        except Exception:
            pass
        
        # Fallback: look for description in argparse
        match = re.search(r'description=["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
        
        return ""
    
    def _extract_function_name(self, content: str) -> str:
        """Extract main function name."""
        # Check for main() function
        if "def main(" in content:
            return "main"
        
        # Check for click command
        match = re.search(r'@click\.command\([^)]*\)\s*def\s+(\w+)', content)
        if match:
            return match.group(1)
        
        # Default to main
        return "main"
    
    def _categorize_command(self, name: str, content: str) -> str:
        """Categorize command by name and content."""
        name_lower = name.lower()
        content_lower = content.lower()
        
        # Analysis commands
        if any(word in name_lower for word in ["analyze", "scan", "check", "verify", "review"]):
            return "analysis"
        
        # Consolidation commands
        if any(word in name_lower for word in ["merge", "consolidate", "archive", "consolidation"]):
            return "consolidation"
        
        # Deployment commands
        if any(word in name_lower for word in ["deploy", "upload", "sync", "push"]):
            return "deployment"
        
        # Maintenance commands
        if any(word in name_lower for word in ["cleanup", "optimize", "validate", "fix"]):
            return "maintenance"
        
        # Monitoring commands
        if any(word in name_lower for word in ["monitor", "status", "health", "check"]):
            return "monitoring"
        
        # Communication commands
        if "communication" in content_lower or "message" in content_lower:
            return "communication"
        
        # Default
        return "general"
    
    def generate_registry_code(self) -> str:
        """
        Generate Python code for command registry.
        
        Returns:
            Python code string for registry
        """
        lines = [
            "# Auto-generated command registry",
            "# Generated by: tools/cli/command_discovery.py",
            "",
            "from typing import Dict",
            "",
            "COMMAND_REGISTRY: Dict[str, Dict] = {"
        ]
        
        # Sort commands by category, then name
        sorted_commands = sorted(
            self.commands,
            key=lambda c: (c.get("category", "general"), c["name"])
        )
        
        for cmd in sorted_commands:
            lines.append(f'    "{cmd["name"]}": {{')
            lines.append(f'        "module": "{cmd["module"]}",')
            lines.append(f'        "function": "{cmd["function"]}",')
            if cmd.get("description"):
                # Escape quotes in description
                desc = cmd["description"].replace('"', '\\"').replace("\\", "\\\\")
                lines.append(f'        "description": "{desc}",')
            lines.append(f'        "category": "{cmd.get("category", "general")}",')
            # Use forward slashes for file paths (works on Windows too)
            file_path = cmd["file"].replace("\\", "/")
            lines.append(f'        "file": "{file_path}",')
            lines.append("    },")
        
        lines.append("}")
        lines.append("")
        lines.append(f"# Total commands: {len(self.commands)}")
        
        return "\n".join(lines)


def main():
    """Main entry point for command discovery."""
    discovery = CommandDiscovery()
    commands = discovery.discover_commands()
    
    print(f"✅ Discovered {len(commands)} CLI commands")
    print(f"\nCategories:")
    categories = {}
    for cmd in commands:
        cat = cmd.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\n📝 Generating registry code...")
    registry_code = discovery.generate_registry_code()
    
    # Write to registry file
    registry_file = PROJECT_ROOT / "tools" / "cli" / "commands" / "registry.py"
    registry_file.write_text(registry_code, encoding="utf-8")
    
    print(f"✅ Registry written to: {registry_file}")
    print(f"   Total commands registered: {len(commands)}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

