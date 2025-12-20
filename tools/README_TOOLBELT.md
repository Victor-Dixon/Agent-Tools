# CLI Toolbelt - Unified Tool Access 🛠️

**Version:** 1.0.0  
**Architecture:** Agent-2 (C-058-2)  
**Implementation:** Agent-1 (C-058-1)  
**Date:** 2025-10-11  

---

## 🎯 Overview

CLI Toolbelt provides a unified command-line interface to access all project development and quality assurance tools through simple, memorable flags.

**Instead of:**
```bash
python tools/run_project_scan.py
python tools/v2_checker_cli.py --fail-on-major
python tools/autonomous_leaderboard.py --top 10
```

**Now:**
```bash
python -m tools.toolbelt --scan
python -m tools.toolbelt --v2-check --fail-on-major
python -m tools.toolbelt --leaderboard --top 10
```

---

## 🚀 Quick Start

### Show All Available Tools
```bash
python -m tools.toolbelt --help
```

### List Tools
```bash
python -m tools.toolbelt --list
```

### Run a Tool
```bash
python -m tools.toolbelt --scan
python -m tools.toolbelt --v2-check
python -m tools.toolbelt --dashboard
```

---

## 📊 Available Tools

### Core Project Tools

| Tool | Flags | Description |
|------|-------|-------------|
| **Project Scanner** | `--scan`, `-s` | Scan project structure and generate analysis |
| **V2 Compliance Checker** | `--v2-check`, `--v2`, `-v` | Check V2 compliance violations |
| **Compliance Dashboard** | `--dashboard`, `-d` | Open compliance tracking dashboard |
| **Complexity Analyzer** | `--complexity`, `-c` | Analyze code complexity metrics |
| **Refactoring Suggestions** | `--refactor`, `-r` | Get intelligent refactoring suggestions |
| **Duplication Analyzer** | `--duplication`, `--dup` | Find duplicate code across project |
| **Functionality Verification** | `--functionality`, `--verify` | Verify functionality preservation |
| **Autonomous Leaderboard** | `--leaderboard`, `-l` | Show agent performance leaderboard |
| **Compliance History** | `--history` | Track compliance history over time |

### QA & Validation Tools (NEW! Agent-8)

| Tool | Flags | Description |
|------|-------|-------------|
| **Memory Leak Scanner** | `--memory-scan` | Detect unbounded caches, lists, and memory leaks |
| **Git Commit Verifier** | `--git-verify` | Verify claimed work exists in git history |
| **Test Pyramid Analyzer** | `--test-pyramid` | Analyze test distribution vs 60/30/10 target |
| **V2 Batch Checker** | `--v2-batch` | Quick V2 compliance check for multiple files |
| **Coverage Validator** | `--coverage-check` | Validate test coverage meets thresholds |
| **QA Checklist** | `--qa-checklist` | Automated QA validation checklist |

---

## 💡 Usage Examples

### Basic Usage

```bash
# Run project scanner
python -m tools.toolbelt --scan

# Check V2 compliance
python -m tools.toolbelt --v2-check

# Open dashboard
python -m tools.toolbelt --dashboard

# Show leaderboard
python -m tools.toolbelt --leaderboard
```

### With Tool Arguments

```bash
# Scan with custom project root
python -m tools.toolbelt --scan --project-root ./src

# V2 check with fail-on-major flag
python -m tools.toolbelt --v2-check --fail-on-major --suggest

# Complexity analysis for specific file
python -m tools.toolbelt --complexity src/services/messaging_cli.py

# Leaderboard top 5
python -m tools.toolbelt --leaderboard --top 5
```

### Using Short Flags

```bash
python -m tools.toolbelt -s           # Same as --scan
python -m tools.toolbelt -v           # Same as --v2-check
python -m tools.toolbelt -d           # Same as --dashboard
python -m tools.toolbelt -l --top 10  # Leaderboard with args
```

---

## 🏗️ Architecture

### Components

```
tools/
├── toolbelt.py              # Main entry point (102 lines)
├── toolbelt_registry.py     # Tool registry (149 lines)
├── toolbelt_runner.py       # Execution engine (92 lines)
├── toolbelt_help.py         # Help system (108 lines)
└── __main__.py              # Package entry point
```

**Total:** 451 lines (V2 compliant)

### Design Principles

- **Single Responsibility**: Each module has one clear purpose
- **Open-Closed**: Easy to add new tools without modifying core
- **Dependency Injection**: Registry injected into components
- **Separation of Concerns**: Parse → Discover → Execute → Help
- **V2 Compliance**: All files <400 lines

---

## 🔧 Adding New Tools

### Step 1: Add to Registry

Edit `tools/toolbelt_registry.py`:

```python
TOOLS_REGISTRY = {
    # ... existing tools ...
    "your-tool": {
        "name": "Your Tool Name",
        "module": "tools.your_tool_cli",
        "main_function": "main",
        "description": "Your tool description",
        "flags": ["--your-tool", "-yt"],
        "args_passthrough": True
    }
}
```

### Step 2: Tool Requirements

Your tool should:
1. Have a `main()` function
2. Return exit code (0 = success, 1+ = error)
3. Accept arguments via `sys.argv` if `args_passthrough: True`

---

## ✅ Testing

### Run Tests

```bash
pytest tests/test_toolbelt.py -v
```

### Test Coverage

- ✅ Registry initialization and tool lookup
- ✅ Tool execution with argument passthrough
- ✅ Help system generation
- ✅ Error handling
- ✅ Flag aliases
- ✅ Version and list commands

---

## 📚 Technical Details

### Argument Passthrough

When `args_passthrough: True`, remaining arguments are passed to the tool:

```bash
python -m tools.toolbelt --scan --project-root . --verbose
                                 ^^^^^^^^^^^^^^^^^^^^^^^^
                                 Passed to projectscanner
```

Implementation:
```python
# toolbelt_runner.py
sys.argv = [module_name] + args  # Set argv for tool
exit_code = main_func()           # Tool reads from sys.argv
sys.argv = original_argv          # Restore argv
```

### Dynamic Tool Loading

```python
# toolbelt_runner.py
module = importlib.import_module(tool_config["module"])
main_func = getattr(module, tool_config["main_function"])
exit_code = main_func()
```

### Help Generation

```python
# toolbelt_help.py
for tool in registry.list_tools():
    print(f"{tool['name']} ({', '.join(tool['flags'])})")
    print(f"  {tool['description']}")
```

---

## 📦 Archived & Deprecated Tools

### **Archived Tools**

Tools that have been archived are located in `tools/deprecated/` and should not be used:

- **`aria_active_response.py`** - Archived (functionality consolidated)
- **`captain_check_agent_status.py`** - Archived (consolidated into `unified_monitor.py`)

**Replacement**: Use `--unified-validator` or `--unified-monitor` flags

### **Deprecated Tools** (Archive Pending)

These tools are deprecated and will be archived after migration period:

- **`file_refactor_detector.py`** → Use `--unified-validator --category refactor`
- **`session_transition_helper.py`** → Use `--unified-validator --category session`
- **`tracker_status_validator.py`** → Use `--unified-validator --category tracker`
- **`workspace_health_monitor.py`** → Use `--unified-monitor --category workspace`

**Migration Guides**:
- Validation Tools: `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`
- Monitoring Tools: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- Archived Tools: `tools/ARCHIVED_TOOLS_MIGRATION_GUIDE.md`
- Deprecation Notices: `tools/DEPRECATION_NOTICES.md`

---

## 🎯 Future Enhancements

### Phase 2 (Future)

- **Dynamic Tool Discovery**: Auto-scan `tools/` for CLI tools
- **Tool Chaining**: Pipe output between tools
- **Configuration Files**: `toolbelt.json` for custom settings
- **Custom Aliases**: User-defined shortcuts
- **Plugin System**: External tool registration

---

## 🏆 Credits

- **Architecture Design**: Agent-2 (Architecture & Design Specialist)
- **Implementation**: Agent-1 (Code Integration & Testing Specialist)
- **Mission**: C-058 CLI Toolbelt
- **Framework**: Entry #025 Competitive Collaboration

---

## 📝 Version History

### v1.0.0 (2025-10-11)
- ✅ Initial release
- ✅ 9 tools integrated
- ✅ Flag-based tool selection
- ✅ Auto-generated help system
- ✅ Argument passthrough
- ✅ V2 compliant (451 lines across 4 modules)

---

🐝 **WE. ARE. SWARM.** ⚡🔥

