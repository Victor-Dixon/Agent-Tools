"""
Swarm System Inventory - Complete Catalog of All Systems
========================================================

Scans and catalogs ALL systems, tools, integrations, and connections.
Provides comprehensive discovery of what exists in the swarm.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-05
Priority: CRITICAL - System Discovery
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from collections import defaultdict


class SwarmSystemInventory:
    """Complete inventory of all swarm systems, tools, and integrations."""

    def __init__(self, repo_path: str = "."):
        """Initialize system inventory."""
        self.repo_path = Path(repo_path)
        self.tools_dir = self.repo_path / "tools"
        self.src_dir = self.repo_path / "src"
        self.systems_dir = self.repo_path / "systems"
        self.docs_dir = self.repo_path / "docs"
        self.agent_workspaces = self.repo_path / "agent_workspaces"
        
        # Inventory data
        self.tools: List[Dict[str, Any]] = []
        self.systems: List[Dict[str, Any]] = []
        self.integrations: List[Dict[str, Any]] = []
        self.services: List[Dict[str, Any]] = []
        self.agents: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []

    def scan_all_tools(self) -> List[Dict[str, Any]]:
        """Scan all tools in tools/ directory."""
        tools = []
        
        # Read toolbelt registry
        registry_file = self.tools_dir / "toolbelt_registry.py"
        if registry_file.exists():
            registry_tools = self._parse_toolbelt_registry(registry_file)
            tools.extend(registry_tools)
        
        # Scan tools directory
        for tool_file in self.tools_dir.glob("*.py"):
            if tool_file.name.startswith("_"):
                continue
            
            tool_info = self._analyze_tool_file(tool_file)
            if tool_info:
                tools.append(tool_info)
        
        self.tools = tools
        return tools

    def _parse_toolbelt_registry(self, registry_file: Path) -> List[Dict[str, Any]]:
        """Parse toolbelt registry to extract tool information."""
        tools = []
        
        try:
            content = registry_file.read_text(encoding="utf-8")
            # Extract TOOLS_REGISTRY dictionary
            match = re.search(r'TOOLS_REGISTRY\s*=\s*\{([^}]+)\}', content, re.DOTALL)
            if match:
                # Parse registry entries
                registry_content = match.group(1)
                # Simple extraction - could be enhanced
                entries = re.findall(r'"([^"]+)":\s*\{([^}]+)\}', registry_content)
                for tool_id, tool_data in entries:
                    tool_info = {
                        "id": tool_id,
                        "source": "toolbelt_registry",
                        "file": str(registry_file),
                    }
                    # Extract name, description, flags
                    name_match = re.search(r'"name":\s*"([^"]+)"', tool_data)
                    if name_match:
                        tool_info["name"] = name_match.group(1)
                    
                    desc_match = re.search(r'"description":\s*"([^"]+)"', tool_data)
                    if desc_match:
                        tool_info["description"] = desc_match.group(1)
                    
                    flags_match = re.search(r'"flags":\s*\[([^\]]+)\]', tool_data)
                    if flags_match:
                        flags_str = flags_match.group(1)
                        flags = [f.strip('"') for f in re.findall(r'"([^"]+)"', flags_str)]
                        tool_info["flags"] = flags
                    
                    module_match = re.search(r'"module":\s*"([^"]+)"', tool_data)
                    if module_match:
                        tool_info["module"] = module_match.group(1)
                    
                    tools.append(tool_info)
        except Exception as e:
            print(f"⚠️ Error parsing toolbelt registry: {e}")
        
        return tools

    def _analyze_tool_file(self, tool_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a tool file to extract information."""
        try:
            content = tool_file.read_text(encoding="utf-8")
            
            tool_info = {
                "id": tool_file.stem,
                "name": tool_file.stem.replace("_", " ").title(),
                "file": str(tool_file),
                "source": "tools_directory",
            }
            
            # Extract docstring
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
                tool_info["description"] = docstring.split("\n")[0]
                tool_info["full_docstring"] = docstring
            
            # Extract imports (shows dependencies)
            imports = self._extract_imports(content)
            tool_info["imports"] = imports
            
            # Extract main function
            if "def main()" in content or "if __name__" in content:
                tool_info["has_cli"] = True
            
            # Check for class definitions
            classes = re.findall(r'class\s+(\w+)', content)
            tool_info["classes"] = classes
            
            # Check for integration points
            integration_keywords = [
                "CaptainSwarmCoordinator",
                "AutonomousTaskEngine",
                "MarkovTaskOptimizer",
                "contract",
                "status.json",
                "inbox",
            ]
            integrations_found = [
                kw for kw in integration_keywords if kw in content
            ]
            if integrations_found:
                tool_info["integrations"] = integrations_found
            
            return tool_info
        except Exception as e:
            print(f"⚠️ Error analyzing {tool_file}: {e}")
            return None

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from code."""
        imports = []
        
        # Find all import statements
        import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+([^\n]+)'
        matches = re.finditer(import_pattern, content, re.MULTILINE)
        
        for match in matches:
            module = match.group(1) or match.group(2).split(",")[0].strip()
            imports.append(module)
        
        return imports

    def scan_all_systems(self) -> List[Dict[str, Any]]:
        """Scan all systems in systems/ directory."""
        systems = []
        
        if not self.systems_dir.exists():
            return systems
        
        for system_dir in self.systems_dir.iterdir():
            if not system_dir.is_dir():
                continue
            
            system_info = {
                "id": system_dir.name,
                "name": system_dir.name.replace("_", " ").title(),
                "path": str(system_dir),
                "type": "system",
            }
            
            # Check for README
            readme = system_dir / "README.md"
            if readme.exists():
                system_info["has_readme"] = True
                content = readme.read_text(encoding="utf-8")
                system_info["description"] = content.split("\n")[0] if content else ""
            
            # Find Python files
            py_files = list(system_dir.rglob("*.py"))
            system_info["python_files"] = len(py_files)
            
            systems.append(system_info)
        
        self.systems = systems
        return systems

    def scan_all_services(self) -> List[Dict[str, Any]]:
        """Scan all services in src/services/ directory."""
        services = []
        services_dir = self.src_dir / "services"
        
        if not services_dir.exists():
            return services
        
        for service_file in services_dir.rglob("*.py"):
            if service_file.name.startswith("_"):
                continue
            
            service_info = {
                "id": service_file.stem,
                "name": service_file.stem.replace("_", " ").title(),
                "file": str(service_file),
                "type": "service",
            }
            
            # Extract docstring
            try:
                content = service_file.read_text(encoding="utf-8")
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    service_info["description"] = docstring_match.group(1).strip().split("\n")[0]
                
                # Check for class definitions
                classes = re.findall(r'class\s+(\w+)', content)
                service_info["classes"] = classes
            except Exception:
                pass
            
            services.append(service_info)
        
        self.services = services
        return services

    def scan_all_agents(self) -> List[Dict[str, Any]]:
        """Scan all agent workspaces."""
        agents = []
        
        if not self.agent_workspaces.exists():
            return agents
        
        for agent_dir in self.agent_workspaces.iterdir():
            if not agent_dir.is_dir():
                continue
            
            agent_id = agent_dir.name
            agent_info = {
                "id": agent_id,
                "name": agent_id.replace("-", " ").title(),
                "workspace": str(agent_dir),
            }
            
            # Read status.json
            status_file = agent_dir / "status.json"
            if status_file.exists():
                try:
                    status = json.loads(status_file.read_text(encoding="utf-8"))
                    agent_info["status"] = status.get("status", "unknown")
                    agent_info["mission"] = status.get("current_mission", "")
                    agent_info["specialty"] = status.get("agent_name", "")
                except Exception:
                    pass
            
            # Check for inbox
            inbox_dir = agent_dir / "inbox"
            if inbox_dir.exists():
                agent_info["has_inbox"] = True
                inbox_files = list(inbox_dir.glob("*.md"))
                agent_info["inbox_messages"] = len(inbox_files)
            
            agents.append(agent_info)
        
        self.agents = agents
        return agents

    def scan_integrations(self) -> List[Dict[str, Any]]:
        """Scan for integration points between systems."""
        integrations = []
        
        # Scan tools for integration patterns
        for tool in self.tools:
            tool_integrations = tool.get("integrations", [])
            if tool_integrations:
                for integration_type in tool_integrations:
                    integrations.append({
                        "from": tool["id"],
                        "to": integration_type,
                        "type": "tool_integration",
                        "description": f"{tool['name']} integrates with {integration_type}",
                    })
        
        # Scan services for integration patterns
        for service in self.services:
            service_file = Path(service["file"])
            if service_file.exists():
                content = service_file.read_text(encoding="utf-8")
                
                # Check for common integration patterns
                if "CaptainSwarmCoordinator" in content:
                    integrations.append({
                        "from": service["id"],
                        "to": "CaptainSwarmCoordinator",
                        "type": "service_integration",
                    })
                
                if "contract" in content.lower():
                    integrations.append({
                        "from": service["id"],
                        "to": "ContractSystem",
                        "type": "service_integration",
                    })
        
        self.integrations = integrations
        return integrations

    def generate_inventory_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report."""
        print("🔍 Scanning tools...")
        self.scan_all_tools()
        
        print("🔍 Scanning systems...")
        self.scan_all_systems()
        
        print("🔍 Scanning services...")
        self.scan_all_services()
        
        print("🔍 Scanning agents...")
        self.scan_all_agents()
        
        print("🔍 Scanning integrations...")
        self.scan_integrations()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tools": len(self.tools),
                "total_systems": len(self.systems),
                "total_services": len(self.services),
                "total_agents": len(self.agents),
                "total_integrations": len(self.integrations),
            },
            "tools": self.tools,
            "systems": self.systems,
            "services": self.services,
            "agents": self.agents,
            "integrations": self.integrations,
        }
        
        return report

    def print_inventory(self, report: Optional[Dict[str, Any]] = None):
        """Print formatted inventory report."""
        if report is None:
            report = self.generate_inventory_report()
        
        print("\n" + "=" * 80)
        print("🐝 SWARM SYSTEM INVENTORY - COMPLETE CATALOG")
        print("=" * 80)
        
        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Tools: {summary['total_tools']}")
        print(f"   Systems: {summary['total_systems']}")
        print(f"   Services: {summary['total_services']}")
        print(f"   Agents: {summary['total_agents']}")
        print(f"   Integrations: {summary['total_integrations']}")
        
        print(f"\n🛠️  TOOLS ({summary['total_tools']}):")
        for tool in sorted(self.tools, key=lambda x: x.get("name", ""))[:20]:
            name = tool.get("name", tool.get("id", "Unknown"))
            desc = tool.get("description", "No description")
            print(f"   • {name}")
            print(f"     {desc[:70]}...")
        
        if summary['total_tools'] > 20:
            print(f"   ... and {summary['total_tools'] - 20} more tools")
        
        print(f"\n⚙️  SYSTEMS ({summary['total_systems']}):")
        for system in self.systems:
            name = system.get("name", system.get("id", "Unknown"))
            print(f"   • {name}")
        
        print(f"\n🔧 SERVICES ({summary['total_services']}):")
        for service in sorted(self.services, key=lambda x: x.get("name", ""))[:10]:
            name = service.get("name", service.get("id", "Unknown"))
            print(f"   • {name}")
        
        if summary['total_services'] > 10:
            print(f"   ... and {summary['total_services'] - 10} more services")
        
        print(f"\n👥 AGENTS ({summary['total_agents']}):")
        for agent in self.agents:
            name = agent.get("name", agent.get("id", "Unknown"))
            status = agent.get("status", "unknown")
            print(f"   • {name}: {status}")
        
        print(f"\n🔗 INTEGRATIONS ({summary['total_integrations']}):")
        integration_groups = defaultdict(list)
        for integration in self.integrations:
            integration_groups[integration["to"]].append(integration["from"])
        
        for target, sources in list(integration_groups.items())[:10]:
            print(f"   • {target}: {len(sources)} connections")
            for source in sources[:3]:
                print(f"     - {source}")
            if len(sources) > 3:
                print(f"     ... and {len(sources) - 3} more")
        
        print("\n" + "=" * 80)
        print("✅ Inventory complete! Use --json to export full data.")
        print("=" * 80)

    def save_inventory(self, output_file: Path):
        """Save inventory to JSON file."""
        report = self.generate_inventory_report()
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Inventory saved to: {output_file}")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Swarm System Inventory - Complete Catalog of All Systems"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Save inventory to JSON file",
    )
    parser.add_argument(
        "--search",
        help="Search for specific system/tool by name",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all tools",
    )
    parser.add_argument(
        "--list-systems",
        action="store_true",
        help="List all systems",
    )
    parser.add_argument(
        "--list-integrations",
        action="store_true",
        help="List all integrations",
    )
    
    args = parser.parse_args()
    
    inventory = SwarmSystemInventory()
    
    if args.json:
        inventory.save_inventory(args.json)
        return
    
    if args.search:
        report = inventory.generate_inventory_report()
        # Search implementation
        print(f"🔍 Searching for: {args.search}")
        # TODO: Implement search
        return
    
    if args.list_tools:
        inventory.scan_all_tools()
        print(f"\n🛠️  TOOLS ({len(inventory.tools)}):")
        for tool in sorted(inventory.tools, key=lambda x: x.get("name", "")):
            name = tool.get("name", tool.get("id", "Unknown"))
            print(f"   • {name}")
        return
    
    if args.list_systems:
        inventory.scan_all_systems()
        print(f"\n⚙️  SYSTEMS ({len(inventory.systems)}):")
        for system in inventory.systems:
            name = system.get("name", system.get("id", "Unknown"))
            print(f"   • {name}")
        return
    
    if args.list_integrations:
        inventory.scan_all_tools()
        inventory.scan_integrations()
        print(f"\n🔗 INTEGRATIONS ({len(inventory.integrations)}):")
        for integration in inventory.integrations:
            print(f"   • {integration['from']} → {integration['to']}")
        return
    
    # Default: print full inventory
    report = inventory.generate_inventory_report()
    inventory.print_inventory(report)


if __name__ == "__main__":
    main()

