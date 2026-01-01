#!/usr/bin/env python3
"""Legacy CLI module shim for tooling expecting tools/cli.py."""

from __future__ import annotations

from tools.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
