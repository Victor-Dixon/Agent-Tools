#!/usr/bin/env python3
"""
Tools V2 Ranking
================
Ranks tools in the V2 registry by estimated value (lines of code as proxy) and filters by category.

Usage:
    python tools_v2/rank_tools_v2.py

Author: Cloud Agent
Date: 2025-01-27
"""

import json
import os
from collections import defaultdict
from pathlib import Path

def main():
    registry_path = Path("tools_v2/tool_registry.lock.json")
    if not registry_path.exists():
        print("Error: Registry not found at tools_v2/tool_registry.lock.json")
        return

    with open(registry_path, "r") as f:
        registry = json.load(f)

    tools_data = registry.get("tools", {})
    
    # Store tools by category
    categories = defaultdict(list)
    
    # Cache file line counts to avoid re-reading
    file_lines_cache = {}

    print(f"# Tools Ranking Report (V2)\n")
    print(f"**Total Tools:** {len(tools_data)}\n")

    for tool_name, info in tools_data.items():
        module_path_str, class_name = info
        
        # Convert module path to file path
        # e.g., tools_v2.categories.vector_tools -> tools_v2/categories/vector_tools.py
        file_path_parts = module_path_str.split(".")
        file_path = Path(*file_path_parts).with_suffix(".py")
        
        # Determine Category from module path
        # e.g., tools_v2.categories.vector_tools -> vector_tools
        category = "other"
        if len(file_path_parts) >= 3 and file_path_parts[1] == "categories":
             category = file_path_parts[2]
        
        # Calculate Lines of Code (LOC)
        loc = 0
        if str(file_path) in file_lines_cache:
            loc = file_lines_cache[str(file_path)]
        elif file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                loc = len(content.splitlines())
                file_lines_cache[str(file_path)] = loc
            except Exception:
                loc = 0
        
        # Calculate Score (Value Proxy)
        # Base score = LOC
        # Bonus for description/metadata could be added here if available in registry
        score = loc
        
        tool_info = {
            "name": tool_name,
            "class": class_name,
            "path": str(file_path),
            "loc": loc,
            "score": score
        }
        
        categories[category].append(tool_info)

    # Sort categories alphabetically
    sorted_categories = sorted(categories.keys())

    for cat in sorted_categories:
        print(f"## Category: {cat}\n")
        
        # Rank tools in category by Score (Desc)
        ranked_tools = sorted(categories[cat], key=lambda x: x["score"], reverse=True)
        
        for idx, tool in enumerate(ranked_tools, 1):
            print(f"{idx}. **{tool['name']}**")
            print(f"   - Value (LOC): {tool['score']}")
            print(f"   - Class: {tool['class']}")
            print(f"   - Path: `{tool['path']}`")
        print("\n")

if __name__ == "__main__":
    main()
