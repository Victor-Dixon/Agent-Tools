"""
CLI Toolbelt Package Entry Point
=================================

Enables running toolbelt as: python -m tools.toolbelt

Author: Agent-1 - Code Integration & Testing Specialist
Date: 2025-10-11
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run toolbelt main
from tools.toolbelt import main

if __name__ == "__main__":
    sys.exit(main())
