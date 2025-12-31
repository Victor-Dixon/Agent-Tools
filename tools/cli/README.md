# Unified CLI Framework

## Overview

Unified CLI framework for consolidating 391 tools CLI files into organized structure.

## Structure

```
tools/cli/
├── dispatchers/
│   └── unified_dispatcher.py    # Main dispatcher
├── commands/
│   └── registry.py              # Command registry
└── __init__.py

src/core/cli/
└── __main__.py                  # Core system CLI

src/services/cli/
└── __main__.py                  # Services CLI
```

## Usage

### Tools CLI
```bash
python -m tools.cli.dispatchers.unified_dispatcher <command> [args...]
```

### Legacy entrypoint (shim)

The repository also includes a lightweight shim at `tools/cli.py` that forwards to
`tools.cli.main` to preserve older automation that still runs:

```bash
python tools/cli.py <command> [args...]
```

This shim is intentionally minimal and should be replaced with a full CLI wrapper
once the legacy path is retired.

### Core CLI
```bash
python -m src.core.cli <command> [args...]
```

### Services CLI
```bash
python -m src.services.cli <command> [args...]
```

## Migration Plan

1. Register commands in `tools/cli/commands/registry.py`
2. Update dispatcher to load registry
3. Migrate tool scripts to use unified dispatcher
4. Update documentation

## Status

🚧 **IN PROGRESS** - Framework created, migration pending
