# 🛠️ Tools Usage Guide - Phase 0A Support

**Date**: 2025-12-26  
**Purpose**: How to install and use existing tools to help with Phase 0A: Organization & Planning

---

## 📦 Installation

### 1. Install Project Dependencies

```bash
# Install in development mode (recommended)
cd /home/dream/Development/projects/personal/AgentTools
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"

# Or install with full dependencies
pip install -e ".[full]"
```

### 2. Verify Installation

```bash
# Check Python version (needs 3.10+)
python3 --version

# Verify project structure
ls -la tools/monitoring/unified_monitor.py
ls -la tools/validation/unified_validator.py
ls -la tools/analysis/unified_analyzer.py
```

---

## 🚀 Using the Tools

### Method 1: Direct Tool Execution (Recommended)

Run tools directly from their module paths:

```bash
# Unified Analyzer
python3 tools/analysis/unified_analyzer.py --help
python3 tools/analysis/unified_analyzer.py --category all

# Unified Validator
python3 tools/validation/unified_validator.py --help
python3 tools/validation/unified_validator.py --all

# Unified Monitor
python3 tools/monitoring/unified_monitor.py --help
python3 tools/monitoring/unified_monitor.py --category all
```

### Method 2: Using Python Module Syntax

```bash
# Run as Python modules
python3 -m tools.analysis.unified_analyzer --category all
python3 -m tools.validation.unified_validator --all
python3 -m tools.monitoring.unified_monitor --category all
```

### Alternative: CLI Dispatcher

For tools registered in the CLI registry:

```bash
# Use unified dispatcher
python3 -m tools.cli.dispatchers.unified_dispatcher <command> [args...]

# Example: Run a registered command
python3 -m tools.cli.dispatchers.unified_dispatcher tool-name --args
```

---

## 🎯 Tools for Phase 0A Tasks

### 1. Tool Inventory System

#### Use Unified Analyzer for Tool Discovery
```bash
# Analyze repository structure
python3 tools/analysis/unified_analyzer.py --category repository

# Analyze project structure
python3 tools/analysis/unified_analyzer.py --category structure

# Detect consolidation opportunities
python3 tools/analysis/unified_analyzer.py --category consolidation

# Find overlap between tools
python3 tools/analysis/unified_analyzer.py --category overlap

# Run all analysis categories
python3 tools/analysis/unified_analyzer.py --category all
```

#### Use Consolidation Analyzer (Diamond Tool)
```bash
# Analyze consolidation opportunities
python3 -m tools.toolbelt --analyze-consolidation

# Or directly
python3 tools/consolidation/consolidation_analyzer.py
```

#### Use Source Analyzer (Diamond Tool)
```bash
# Get source code statistics
python3 -m tools.toolbelt --analyze-source

# Or directly
python3 tools/analysis/source_analyzer.py
```

### 2. Dependency Mapping

#### Use Unified Validator for Import Analysis
```bash
# Validate all imports
python3 tools/validation/unified_validator.py --category imports

# Audit imports (Gold Tool)
python3 -m tools.toolbelt --audit-imports

# Or directly
python3 tools/validation/audit_imports.py
```

#### Use Import Chain Validator
```bash
# Validate import chains
python3 tools/validation/import_chain_validator.py
```

### 3. Usage Analysis

#### Use Unified Analyzer
```bash
# Analyze code complexity
python3 tools/analysis/unified_analyzer.py --category complexity

# Find duplicate code
python3 tools/analysis/unified_analyzer.py --category duplicates
```

#### Use Technical Debt Analyzer (Diamond Tool)
```bash
# Deep scan for technical debt
python3 -m tools.toolbelt --analyze-debt

# Or directly
python3 tools/analysis/technical_debt_analyzer.py
```

### 4. V2 Compliance Checking

#### Use V2 Compliance Checker
```bash
# Check V2 compliance
python3 -m tools.toolbelt --v2-check

# Or directly
python3 tools/validation/v2_compliance_checker.py
```

---

## 📋 Phase 0A Task → Tool Mapping

| Phase 0A Task | Recommended Tool | Command |
|----------------|------------------|---------|
| **1.1 Create Tool Inventory** | Unified Analyzer | `python3 tools/analysis/unified_analyzer.py --category all` |
| **1.2 Automated Discovery** | Source Analyzer | `python3 -m tools.toolbelt --analyze-source` |
| **1.3 Manual Review** | Consolidation Analyzer | `python3 -m tools.toolbelt --analyze-consolidation` |
| **1.4 V2 Tools Inventory** | V2 Compliance Checker | `python3 -m tools.toolbelt --v2-check` |
| **2.1 Import Analysis** | Unified Validator | `python3 tools/validation/unified_validator.py --category imports` |
| **2.2 Registry Dependencies** | Unified Analyzer | `python3 tools/analysis/unified_analyzer.py --category repository` |
| **3.1 Codebase Usage** | Technical Debt Analyzer | `python3 -m tools.toolbelt --analyze-debt` |
| **3.2 Documentation Scan** | Unified Analyzer | `python3 tools/analysis/unified_analyzer.py --category structure` |
| **4.1 Category Mapping** | Consolidation Analyzer | `python3 -m tools.toolbelt --analyze-consolidation` |
| **5.1 Technical Risks** | V2 Compliance Checker | `python3 -m tools.toolbelt --v2-check` |
| **6.1 Progress Tracking** | Unified Monitor | `python3 tools/monitoring/unified_monitor.py --category all` |

---

## 🔧 Creating Phase 0A Helper Scripts

### Script 1: Tool Inventory Generator

Create `scripts/inventory_tools.py`:

```python
#!/usr/bin/env python3
"""
Tool Inventory Generator for Phase 0A
Scans tools/ directory and generates tools_inventory.json
"""
import json
import ast
from pathlib import Path
from typing import Dict, List

def scan_tools_directory():
    """Scan tools/ directory and extract metadata."""
    tools_dir = Path("tools")
    inventory = {"tools": {}, "categories": {}, "duplicates": {}}
    
    # Use Unified Analyzer to get initial data
    # Then enhance with manual review
    
    return inventory

if __name__ == "__main__":
    inventory = scan_tools_directory()
    with open("tools_inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)
    print("✅ Tool inventory generated: tools_inventory.json")
```

### Script 2: Dependency Analyzer

Create `scripts/analyze_dependencies.py`:

```python
#!/usr/bin/env python3
"""
Dependency Analyzer for Phase 0A
Uses Unified Validator for import analysis
"""
import subprocess
import json
from pathlib import Path

def analyze_dependencies():
    """Analyze dependencies using Unified Validator."""
    # Run Unified Validator
    result = subprocess.run(
        ["python3", "tools/validation/unified_validator.py", "--category", "imports"],
        capture_output=True,
        text=True
    )
    
    # Parse and enhance results
    # Create dependency graph
    
    return dependency_graph

if __name__ == "__main__":
    graph = analyze_dependencies()
    with open("dependency_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    print("✅ Dependency graph generated: dependency_graph.json")
```

---

## 💡 Quick Commands for Phase 0A

### Get Started Quickly

```bash
# 1. Navigate to project root
cd /home/dream/Development/projects/personal/AgentTools

# 2. (Optional) Install in development mode
pip install -e .

# 3. Run comprehensive analysis
python3 tools/analysis/unified_analyzer.py --category all --json > analysis_report.json

# 4. Validate all imports
python3 tools/validation/unified_validator.py --all --json > validation_report.json

# 5. Monitor system health
python3 tools/monitoring/unified_monitor.py --category all --json > monitor_report.json

# 6. Check help for any tool
python3 tools/analysis/unified_analyzer.py --help
python3 tools/validation/unified_validator.py --help
python3 tools/monitoring/unified_monitor.py --help
```

### Generate Phase 0A Reports

```bash
# Create reports directory
mkdir -p phase0a_reports

# Generate all reports
python3 tools/analysis/unified_analyzer.py --category all > phase0a_reports/analysis.json
python3 tools/validation/unified_validator.py --all > phase0a_reports/validation.json
python3 -m tools.toolbelt --v2-check > phase0a_reports/v2_compliance.json
python3 -m tools.toolbelt --analyze-consolidation > phase0a_reports/consolidation.json
python3 -m tools.toolbelt --analyze-source > phase0a_reports/source_stats.json
```

---

## 🎯 Using Tools_v2 System

### Access tools_v2 Tools

```bash
# Run tools_v2 toolbelt
python3 tools_v2/toolbelt_core.py

# Or use the adapter system
python3 -c "from tools_v2 import get_toolbelt_core; tb = get_toolbelt_core(); print(tb.list_tools())"
```

### List tools_v2 Tools

```python
# Python script
from tools_v2 import get_toolbelt_core

toolbelt = get_toolbelt_core()
tools = toolbelt.list_tools()
print(f"Available tools: {len(tools)}")
for tool in tools:
    print(f"  - {tool}")
```

---

## 📊 Tool Output Formats

### JSON Output

Most tools support JSON output:

```bash
# Unified Analyzer with JSON
python3 tools/analysis/unified_analyzer.py --category all --json > analysis.json

# Unified Validator with JSON
python3 tools/validation/unified_validator.py --all --json > validation.json
```

### Human-Readable Output

Default output is human-readable:

```bash
# Human-readable analysis
python3 tools/analysis/unified_analyzer.py --category all

# Human-readable validation
python3 tools/validation/unified_validator.py --all
```

---

## 🔍 Troubleshooting

### Common Issues

1. **Module Not Found**
   ```bash
   # Ensure you're in project root
   cd /home/dream/Development/projects/personal/AgentTools
   
   # Install in development mode
   pip install -e .
   ```

2. **Python Version**
   ```bash
   # Check Python version (needs 3.10+)
   python3 --version
   
   # Use python3 explicitly
   python3 -m tools.toolbelt --help
   ```

3. **Import Errors**
   ```bash
   # Run from project root
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   python3 tools/analysis/unified_analyzer.py --help
   ```

---

## 📚 Additional Resources

- **Toolbelt Documentation**: `tools/README_TOOLBELT.md`
- **Tool Registry**: `tools/toolbelt_registry.py`
- **Unified Tools**: See `tools/monitoring/`, `tools/validation/`, `tools/analysis/`
- **Tools_v2 System**: `tools_v2/README.md`
- **Phase 0A Plan**: `PHASE_0A_ORGANIZATION_PLAN.md`

---

## 🎯 Next Steps

1. **Install project**: `pip install -e .`
2. **Run initial analysis**: `python3 tools/analysis/unified_analyzer.py --category all`
3. **Validate imports**: `python3 tools/validation/unified_validator.py --category imports`
4. **Check V2 compliance**: `python3 -m tools.toolbelt --v2-check`
5. **Start Phase 0A**: Follow `PHASE_0A_ORGANIZATION_PLAN.md`

---

**🐺 WE ARE SWARM**

*"The strength of the pack is the wolf, and the strength of the wolf is the pack."*

