#!/usr/bin/env python3
"""
Service Migration Helper Tool
=============================

Tool I wished I had during service patterns analysis:
- Automatically detect services that should use BaseService
- Generate migration templates
- Verify migration correctness
- Check for common patterns

<!-- SSOT Domain: infrastructure -->

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-05
License: MIT
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceMigrationHelper:
    """Helper tool for migrating services to BaseService."""

    def __init__(self, services_dir: str = "src/services"):
        """Initialize service migration helper."""
        self.services_dir = Path(services_dir)
        self.services: List[Dict[str, Any]] = []

    def discover_services(self) -> List[Dict[str, Any]]:
        """Discover all service files that should use BaseService."""
        services = []

        for py_file in self.services_dir.rglob("*.py"):
            if py_file.name.startswith("_") or py_file.name == "__init__.py":
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content, filename=str(py_file))

                    # Find service classes
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Check if it's a service class
                            if self._is_service_class(node, content):
                                services.append({
                                    "file": str(py_file),
                                    "class_name": node.name,
                                    "uses_baseservice": self._uses_baseservice(node, content),
                                    "has_init": self._has_init(node),
                                    "has_lifecycle": self._has_lifecycle(node),
                                    "patterns": self._detect_patterns(node, content),
                                })
            except Exception as e:
                logger.warning(f"Failed to parse {py_file}: {e}")

        self.services = services
        return services

    def _is_service_class(self, node: ast.ClassDef, content: str) -> bool:
        """Check if class is a service class."""
        # Check if name contains "Service" or is in services directory
        if "Service" in node.name:
            return True

        # Check if it's in handlers directory (business logic handlers)
        if "handlers" in content and "Handler" in node.name:
            return True

        return False

    def _uses_baseservice(self, node: ast.ClassDef, content: str) -> bool:
        """Check if class uses BaseService."""
        return "BaseService" in content or "from src.core.base.base_service import" in content

    def _has_init(self, node: ast.ClassDef) -> bool:
        """Check if class has __init__ method."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                return True
        return False

    def _has_lifecycle(self, node: ast.ClassDef) -> bool:
        """Check if class has lifecycle methods."""
        lifecycle_methods = ["start", "stop", "initialize", "activate", "deactivate"]
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name in lifecycle_methods:
                return True
        return False

    def _detect_patterns(self, node: ast.ClassDef, content: str) -> List[str]:
        """Detect initialization patterns."""
        patterns = []

        if "repository" in content.lower() and "def __init__(self, repository" in content:
            patterns.append("dependency_injection")

        if "PYAUTOGUI_AVAILABLE" in content or "SELENIUM_AVAILABLE" in content:
            patterns.append("optional_dependencies")

        if "config_path" in content and "def __init__(self" in content:
            patterns.append("config_path")

        if "logging.getLogger" in content and "def __init__" in content:
            patterns.append("simple_init")

        return patterns

    def generate_migration_template(self, service: Dict[str, Any]) -> str:
        """Generate migration template for a service."""
        file_path = service["file"]
        class_name = service["class_name"]
        patterns = service["patterns"]

        template = f"""# Migration Template for {class_name}
# File: {file_path}

# Step 1: Add BaseService import
from src.core.base.base_service import BaseService

# Step 2: Update class definition
class {class_name}(BaseService):
    \"\"\"Migrated to use BaseService for consolidated patterns.\"\"\"

    def __init__(self, service_name: str = "{class_name}", **kwargs):
        # Initialize BaseService first
        super().__init__(service_name)
        
        # Your existing initialization code here
        # Patterns detected: {', '.join(patterns)}
"""

        if "dependency_injection" in patterns:
            template += """
        # Dependency injection pattern
        self.repository = kwargs.get('repository')
"""

        if "optional_dependencies" in patterns:
            template += """
        # Optional dependencies pattern
        # Check for optional dependencies
        try:
            import pyautogui
            self.pyautogui = pyautogui
        except ImportError:
            self.pyautogui = None
"""

        if "config_path" in patterns:
            template += """
        # Config loading pattern (now uses InitializationMixin)
        config_section = kwargs.get('config_section', service_name.lower())
        self.service_config = self.load_config(config_section)
"""

        template += """
    # Step 3: Use ErrorHandlingMixin for error handling
    def some_method(self):
        return self.safe_execute(
            operation=lambda: self._do_something(),
            operation_name="some_method",
            default_return=False,
            logger=self.logger,
            component_name=self.service_name
        )
"""

        return template

    def generate_migration_report(self) -> str:
        """Generate migration report."""
        if not self.services:
            self.discover_services()

        report = ["# Service Migration Report\n"]
        report.append(f"**Total Services**: {len(self.services)}\n")
        report.append(f"**Services Using BaseService**: {sum(1 for s in self.services if s['uses_baseservice'])}\n")
        report.append(f"**Services Needing Migration**: {sum(1 for s in self.services if not s['uses_baseservice'])}\n\n")

        report.append("## Services Needing Migration\n\n")
        for service in self.services:
            if not service["uses_baseservice"]:
                report.append(f"- **{service['class_name']}** ({service['file']})")
                report.append(f"  - Patterns: {', '.join(service['patterns'])}")
                report.append(f"  - Has __init__: {service['has_init']}")
                report.append(f"  - Has lifecycle: {service['has_lifecycle']}\n")

        return "\n".join(report)

    def verify_migration(self, file_path: str) -> Dict[str, Any]:
        """Verify a service migration is correct."""
        results = {
            "uses_baseservice": False,
            "uses_initialization_mixin": False,
            "uses_error_handling_mixin": False,
            "has_lifecycle": False,
            "errors": [],
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            results["uses_baseservice"] = "BaseService" in content
            results["uses_initialization_mixin"] = "InitializationMixin" in content or "initialize_with_config" in content
            results["uses_error_handling_mixin"] = "ErrorHandlingMixin" in content or "safe_execute" in content
            results["has_lifecycle"] = any(method in content for method in ["def start(", "def stop(", "def initialize("])

            if not results["uses_baseservice"]:
                results["errors"].append("Service does not inherit from BaseService")

            if not results["uses_initialization_mixin"]:
                results["errors"].append("Service does not use InitializationMixin")

            if not results["uses_error_handling_mixin"]:
                results["errors"].append("Service does not use ErrorHandlingMixin")

        except Exception as e:
            results["errors"].append(f"Failed to read file: {e}")

        return results


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Service Migration Helper")
    parser.add_argument("--discover", action="store_true", help="Discover services")
    parser.add_argument("--report", action="store_true", help="Generate migration report")
    parser.add_argument("--template", type=str, help="Generate template for service file")
    parser.add_argument("--verify", type=str, help="Verify migration for service file")

    args = parser.parse_args()

    helper = ServiceMigrationHelper()

    if args.discover:
        services = helper.discover_services()
        print(f"Discovered {len(services)} services")

    if args.report:
        report = helper.generate_migration_report()
        print(report)

    if args.template:
        services = helper.discover_services()
        service = next((s for s in services if args.template in s["file"]), None)
        if service:
            template = helper.generate_migration_template(service)
            print(template)
        else:
            print(f"Service not found: {args.template}")

    if args.verify:
        results = helper.verify_migration(args.verify)
        print(f"Migration verification for {args.verify}:")
        print(f"  Uses BaseService: {results['uses_baseservice']}")
        print(f"  Uses InitializationMixin: {results['uses_initialization_mixin']}")
        print(f"  Uses ErrorHandlingMixin: {results['uses_error_handling_mixin']}")
        if results["errors"]:
            print(f"  Errors: {', '.join(results['errors'])}")


if __name__ == "__main__":
    main()


