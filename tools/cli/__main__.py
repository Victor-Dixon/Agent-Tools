"""Module entry point for `python -m tools.cli`."""

from __future__ import annotations

import sys

from tools.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
