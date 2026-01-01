# 🛠️ Setup Guide - Tools Installation & Configuration

**Date**: 2025-12-26  
**Purpose**: Complete setup instructions for using tools in Phase 0A and beyond

---

## ✅ Quick Setup Check

Run the environment checker to see what's needed:

```bash
cd /home/dream/Development/projects/personal/AgentTools
python3 tools/devops/unified_environment.py
```

This will show you:
- ✅ Installed tools (git, python3, pip, etc.)
- ❌ Missing tools
- 🔑 Environment variables status
- 🐳 Infrastructure status (Docker, etc.)

---

## 📦 Installation Options

### Option 1: No Installation Required (Recommended for Phase 0A)

**The unified tools work directly without installation!**

```bash
# Just run tools directly
python3 tools/analysis/unified_analyzer.py --help
python3 tools/validation/unified_validator.py --help
python3 tools/monitoring/unified_monitor.py --help
```

**Why this works:**
- Tools use only Python standard library (no external dependencies)
- `pyproject.toml` shows `dependencies = []` (no required packages)
- Tools are self-contained Python scripts

### Option 2: Development Installation (Optional)

If you want to use tools as Python modules or install the swarm-mcp package:

```bash
# Install in development mode
pip install -e .

# Or with dev dependencies (pytest, ruff, mypy)
pip install -e ".[dev]"

# Or with full dependencies (for advanced features)
pip install -e ".[full]"
```

**When to use this:**
- You want to import tools as Python modules
- You need dev tools (pytest, ruff, mypy)
- You're developing new tools

---

## 🔧 Required Tools

### Essential (Required)

| Tool | Purpose | Check |
|------|---------|-------|
| **Python 3.10+** | Run Python tools | `python3 --version` |
| **Git** | Version control | `git --version` |

### Optional (For Specific Features)

| Tool | Purpose | When Needed |
|------|---------|-------------|
| **pip** | Package management | If installing dependencies |
| **Docker** | Containerization | For mod deployment features |
| **Node.js/npm** | JavaScript tools | For web/Node.js features |

**Check your setup:**
```bash
python3 tools/devops/unified_environment.py
```

---

## 🔑 Environment Variables

### Optional Environment Variables

Most tools work without environment variables. Some optional ones:

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `OPENAI_API_KEY` | OpenAI API access | AI features (if used) |
| `GITHUB_TOKEN` | GitHub API access | GitHub tools |
| `HOSTINGER_HOST` | Hostinger SSH | WordPress deployment |
| `HOSTINGER_USER` | Hostinger username | WordPress deployment |
| `HOSTINGER_PASS` | Hostinger password | WordPress deployment |

**For Phase 0A:** None required! Tools work without any environment variables.

### Setting Environment Variables

```bash
# Option 1: Export in shell
export OPENAI_API_KEY="your-key-here"

# Option 2: Create .env file (if python-dotenv installed)
echo "OPENAI_API_KEY=your-key-here" > .env

# Option 3: Use unified_environment.py to check
python3 tools/devops/unified_environment.py
```

---

## 📋 Setup Checklist

### Phase 0A Setup (Minimal)

- [ ] **Python 3.10+** installed
  ```bash
  python3 --version  # Should show 3.10 or higher
  ```

- [ ] **Git** installed
  ```bash
  git --version  # Should show git version
  ```

- [ ] **Project cloned**
  ```bash
  cd /home/dream/Development/projects/personal/AgentTools
  ```

- [ ] **Test a tool**
  ```bash
  python3 tools/analysis/unified_analyzer.py --help
  ```

**That's it!** Phase 0A tools work with just Python 3.10+ and Git.

### Full Setup (Optional)

- [ ] Install project: `pip install -e .`
- [ ] Install dev dependencies: `pip install -e ".[dev]"`
- [ ] Set environment variables (if needed)
- [ ] Install Docker (if using container features)
- [ ] Install Node.js (if using web features)

---

## 🚀 Verify Setup

### Quick Verification

```bash
# 1. Check environment
python3 tools/devops/unified_environment.py

# 2. Test Unified Analyzer
python3 tools/analysis/unified_analyzer.py --help

# 3. Test Unified Validator
python3 tools/validation/unified_validator.py --help

# 4. Test Unified Monitor
python3 tools/monitoring/unified_monitor.py --help
```

### Expected Output

If setup is correct, you should see:
- ✅ Help messages from all tools
- ✅ No import errors
- ✅ Tools execute successfully

---

## 🔍 Troubleshooting

### Issue: "Module not found"

**Solution:**
```bash
# Ensure you're in project root
cd /home/dream/Development/projects/personal/AgentTools

# Add project to PYTHONPATH (if needed)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in dev mode
pip install -e .
```

### Issue: "Command not found: python"

**Solution:**
```bash
# Use python3 explicitly
python3 tools/analysis/unified_analyzer.py --help

# Or create alias
alias python=python3
```

### Issue: "Permission denied"

**Solution:**
```bash
# Make scripts executable (if needed)
chmod +x tools/analysis/unified_analyzer.py
chmod +x tools/validation/unified_validator.py
chmod +x tools/monitoring/unified_monitor.py
```

### Issue: Import errors in tools

**Solution:**
```bash
# Check Python version (needs 3.10+)
python3 --version

# Install in development mode
pip install -e .

# Check for missing dependencies
python3 tools/devops/unified_environment.py
```

---

## 📚 Tool Dependencies

### Standard Library Only (No Installation Needed)

The unified tools use **only Python standard library**:
- `argparse` - Command-line parsing
- `ast` - Abstract syntax tree parsing
- `json` - JSON handling
- `os`, `sys` - System operations
- `pathlib` - Path handling
- `subprocess` - Running external commands
- `collections` - Data structures
- `datetime` - Date/time handling
- `re` - Regular expressions
- `typing` - Type hints

**No external dependencies required!**

### Optional Dependencies

Some tools may use optional dependencies (with graceful fallbacks):

| Package | Used By | Required? |
|---------|---------|-----------|
| `python-dotenv` | Environment variable loading | No (optional) |
| `requests` | HTTP requests | No (only for specific tools) |
| `paramiko` | SSH connections | No (only for deployment) |

---

## 🎯 Phase 0A Specific Setup

### Minimal Setup for Phase 0A

**You only need:**
1. Python 3.10+ ✅
2. Git ✅
3. Project directory ✅

**No installation, no dependencies, no configuration needed!**

### Test Phase 0A Tools

```bash
# Create reports directory
mkdir -p phase0a_reports

# Run analysis (generates JSON)
python3 tools/analysis/unified_analyzer.py --category all --json > phase0a_reports/analysis.json

# Run validation (generates JSON)
python3 tools/validation/unified_validator.py --all --json > phase0a_reports/validation.json

# Check environment
python3 tools/devops/unified_environment.py > phase0a_reports/environment.json
```

---

## 🔄 Keeping Tools Updated

### Update from Git

```bash
# Pull latest changes
git pull origin main

# Tools update automatically (no reinstall needed)
```

### Reinstall (If Needed)

```bash
# Uninstall
pip uninstall swarm-mcp

# Reinstall
pip install -e .
```

---

## 📝 Configuration Files

### Optional Configuration

Some tools may use configuration files (optional):

| File | Purpose | Required? |
|------|---------|-----------|
| `.env` | Environment variables | No |
| `tools/audit_config.json` | Audit configuration | No |
| `integration/cursor_config.json` | Cursor MCP config | No |
| `integration/claude_desktop_config.json` | Claude Desktop config | No |

**For Phase 0A:** None of these are required!

---

## ✅ Setup Verification Script

Create a quick verification script:

```bash
#!/bin/bash
# verify_setup.sh

echo "🔍 Verifying Setup..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3: $(python3 --version)"
else
    echo "❌ Python 3: NOT FOUND"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version)"
else
    echo "❌ Git: NOT FOUND"
    exit 1
fi

# Test tools
echo ""
echo "🧪 Testing Tools..."
python3 tools/analysis/unified_analyzer.py --help > /dev/null 2>&1 && echo "✅ Unified Analyzer: OK" || echo "❌ Unified Analyzer: FAILED"
python3 tools/validation/unified_validator.py --help > /dev/null 2>&1 && echo "✅ Unified Validator: OK" || echo "❌ Unified Validator: FAILED"
python3 tools/monitoring/unified_monitor.py --help > /dev/null 2>&1 && echo "✅ Unified Monitor: OK" || echo "❌ Unified Monitor: FAILED"

echo ""
echo "✅ Setup verification complete!"
```

---

## 🎯 Quick Start Commands

```bash
# 1. Navigate to project
cd /home/dream/Development/projects/personal/AgentTools

# 2. Check environment
python3 tools/devops/unified_environment.py

# 3. Test a tool
python3 tools/analysis/unified_analyzer.py --help

# 4. Start Phase 0A
mkdir -p phase0a_reports
python3 tools/analysis/unified_analyzer.py --category all --json > phase0a_reports/analysis.json
```

---

## 📚 Related Documentation

- **Tools Usage Guide**: `TOOLS_USAGE_GUIDE.md`
- **Quick Start Phase 0A**: `QUICK_START_PHASE0A.md`
- **Phase 0A Plan**: `PHASE_0A_ORGANIZATION_PLAN.md`
- **Environment Tool**: `tools/devops/unified_environment.py`

---

## 🐺 WE ARE SWARM

**Setup is simple - just Python 3.10+ and Git!**

*"The strength of the pack is the wolf, and the strength of the wolf is the pack."*


