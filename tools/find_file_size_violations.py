#!/usr/bin/env python3
"""Find all Python files exceeding size limits."""

import os
from pathlib import Path

MAX_LINES = 600
WARNING_LINES = 500

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def scan_violations():
    violations = []
    warnings = []
    
    for root, dirs, files in os.walk('.'):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                line_count = count_lines(filepath)
                
                if line_count > MAX_LINES:
                    violations.append((filepath, line_count))
                elif line_count > WARNING_LINES:
                    warnings.append((filepath, line_count))
    
    return sorted(violations, key=lambda x: x[1], reverse=True), sorted(warnings, key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    violations, warnings = scan_violations()
    
    print("\n🔴 CRITICAL VIOLATIONS (>600 lines):")
    print("=" * 80)
    for filepath, line_count in violations:
        print(f"  {filepath}: {line_count} lines (EXCEEDS by {line_count - MAX_LINES})")
    
    print(f"\n  Total Critical: {len(violations)} files")
    
    print("\n\n🟡 WARNINGS (500-600 lines):")
    print("=" * 80)
    for filepath, line_count in warnings[:10]:  # Top 10
        print(f"  {filepath}: {line_count} lines (approaching limit)")
    
    if len(warnings) > 10:
        print(f"  ... and {len(warnings) - 10} more files")
    
    print(f"\n  Total Warnings: {len(warnings)} files")
    print(f"\n📊 TOTAL FILES TO REFACTOR: {len(violations) + len(warnings)}")

