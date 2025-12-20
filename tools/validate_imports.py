#!/usr/bin/env python3
"""
Import Validator
================

Validate import statements and dependencies.

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_validator import UnifiedValidator


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import Validator")
    parser.add_argument(
        "file",
        nargs="?",
        help="File to validate imports for (optional, validates all if not specified)",
    )
    parser.add_argument(
        "--output",
        help="Output file for results (JSON)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    validator = UnifiedValidator()
    
    if args.file:
        print(f"🔍 Validating imports for: {args.file}")
        result = validator.validate_imports(args.file)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return 1
        
        imports = result.get("imports", [])
        print(f"\n📊 Found {len(imports)} imports")
        
        if args.verbose:
            for imp in imports:
                print(f"   - {imp}")
        
        if args.output:
            import json
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {output_path}")
    else:
        print("🔍 Validating imports for all Python files...")
        # Run comprehensive validation
        result = validator.validate_all()
        
        import_results = result.get("validations", {}).get("imports", {})
        print(f"\n📊 Import validation complete")
        print(f"   Files checked: {import_results.get('files_checked', 0)}")
        print(f"   Issues found: {import_results.get('issues', 0)}")
        
        if args.output:
            import json
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

