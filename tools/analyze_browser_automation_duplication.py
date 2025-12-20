#!/usr/bin/env python3
"""
Analyze Browser Automation Duplication
=======================================

Analyzes browser automation implementations to identify duplication patterns.
Low priority consolidation task from technical debt analysis.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


def find_browser_automation_files() -> List[Path]:
    """Find all files related to browser automation."""
    browser_files = []
    
    # Search patterns
    patterns = [
        "browser",
        "webdriver",
        "selenium",
        "pyautogui",
        "undetected"
    ]
    
    # Directories to search
    search_dirs = [
        PROJECT_ROOT / "src" / "infrastructure",
        PROJECT_ROOT / "src" / "core",
        PROJECT_ROOT / "src" / "services",
        PROJECT_ROOT / "tools"
    ]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        
        for py_file in search_dir.rglob("*.py"):
            # Skip certain directories
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'node_modules', 'venv', 'htmlcov', 'temp_repos']):
                continue
            
            file_content = py_file.read_text(encoding='utf-8', errors='ignore').lower()
            
            # Check if file contains browser automation keywords
            if any(pattern in file_content for pattern in patterns):
                browser_files.append(py_file)
    
    return browser_files


def analyze_file_patterns(file_path: Path) -> Dict:
    """Analyze a file for browser automation patterns."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        tree = ast.parse(content, filename=str(file_path))
        
        patterns = {
            "imports": [],
            "classes": [],
            "functions": [],
            "webdriver_usage": False,
            "selenium_usage": False,
            "pyautogui_usage": False,
            "undetected_usage": False
        }
        
        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    patterns["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                patterns["imports"].append(module)
                for alias in node.names:
                    patterns["imports"].append(f"{module}.{alias.name}")
            
            # Check classes
            if isinstance(node, ast.ClassDef):
                patterns["classes"].append(node.name)
            
            # Check functions
            if isinstance(node, ast.FunctionDef):
                patterns["functions"].append(node.name)
        
        # Check for specific library usage
        imports_str = " ".join(patterns["imports"]).lower()
        patterns["webdriver_usage"] = "webdriver" in imports_str or "webdriver" in content.lower()
        patterns["selenium_usage"] = "selenium" in imports_str or "selenium" in content.lower()
        patterns["pyautogui_usage"] = "pyautogui" in imports_str or "pyautogui" in content.lower()
        patterns["undetected_usage"] = "undetected" in imports_str or "undetected" in content.lower()
        
        return patterns
    
    except Exception as e:
        return {"error": str(e)}


def identify_duplication_patterns(files: List[Path]) -> Dict:
    """Identify duplication patterns across browser automation files."""
    analysis = {
        "files": {},
        "patterns": defaultdict(list),
        "duplicates": [],
        "recommendations": []
    }
    
    # Analyze each file
    for file_path in files:
        relative_path = str(file_path.relative_to(PROJECT_ROOT))
        file_patterns = analyze_file_patterns(file_path)
        analysis["files"][relative_path] = file_patterns
    
    # Group by patterns
    webdriver_files = []
    selenium_files = []
    pyautogui_files = []
    undetected_files = []
    
    for file_path, patterns in analysis["files"].items():
        if patterns.get("webdriver_usage"):
            webdriver_files.append(file_path)
        if patterns.get("selenium_usage"):
            selenium_files.append(file_path)
        if patterns.get("pyautogui_usage"):
            pyautogui_files.append(file_path)
        if patterns.get("undetected_usage"):
            undetected_files.append(file_path)
    
    analysis["patterns"]["webdriver"] = webdriver_files
    analysis["patterns"]["selenium"] = selenium_files
    analysis["patterns"]["pyautogui"] = pyautogui_files
    analysis["patterns"]["undetected"] = undetected_files
    
    # Identify potential duplicates
    # Files with similar class/function names
    class_names = defaultdict(list)
    function_names = defaultdict(list)
    
    for file_path, patterns in analysis["files"].items():
        for class_name in patterns.get("classes", []):
            if "browser" in class_name.lower() or "webdriver" in class_name.lower():
                class_names[class_name].append(file_path)
        for func_name in patterns.get("functions", []):
            if "browser" in func_name.lower() or "driver" in func_name.lower():
                function_names[func_name].append(file_path)
    
    # Find duplicates
    for class_name, files in class_names.items():
        if len(files) > 1:
            analysis["duplicates"].append({
                "type": "class",
                "name": class_name,
                "files": files,
                "count": len(files)
            })
    
    for func_name, files in function_names.items():
        if len(files) > 1:
            analysis["duplicates"].append({
                "type": "function",
                "name": func_name,
                "files": files,
                "count": len(files)
            })
    
    # Generate recommendations
    if len(webdriver_files) > 1:
        analysis["recommendations"].append({
            "issue": f"Multiple WebDriver implementations ({len(webdriver_files)} files)",
            "files": webdriver_files,
            "action": "Consolidate into unified WebDriver service"
        })
    
    if len(pyautogui_files) > 1:
        analysis["recommendations"].append({
            "issue": f"Multiple PyAutoGUI implementations ({len(pyautogui_files)} files)",
            "files": pyautogui_files,
            "action": "Consolidate GUI automation into unified service"
        })
    
    return analysis


def main():
    """Analyze browser automation duplication."""
    print("🔍 Analyzing Browser Automation Duplication...")
    print()
    
    # Find browser automation files
    browser_files = find_browser_automation_files()
    
    print(f"📊 Found {len(browser_files)} browser automation files")
    print()
    
    # Analyze patterns
    print("🔍 Analyzing patterns...")
    analysis = identify_duplication_patterns(browser_files)
    
    # Print summary
    print("📋 Pattern Summary:")
    print(f"   WebDriver files: {len(analysis['patterns']['webdriver'])}")
    print(f"   Selenium files: {len(analysis['patterns']['selenium'])}")
    print(f"   PyAutoGUI files: {len(analysis['patterns']['pyautogui'])}")
    print(f"   Undetected files: {len(analysis['patterns']['undetected'])}")
    print()
    
    # Print duplicates
    if analysis["duplicates"]:
        print("⚠️  Potential Duplicates:")
        for dup in analysis["duplicates"]:
            print(f"   {dup['type']}: {dup['name']} ({dup['count']} files)")
            for file_path in dup["files"]:
                print(f"      - {file_path}")
        print()
    
    # Print recommendations
    if analysis["recommendations"]:
        print("💡 Recommendations:")
        for rec in analysis["recommendations"]:
            print(f"   {rec['issue']}")
            print(f"   Action: {rec['action']}")
            print(f"   Files: {len(rec['files'])} files")
            for file_path in rec["files"][:5]:  # Show first 5
                print(f"      - {file_path}")
            if len(rec["files"]) > 5:
                print(f"      ... and {len(rec['files']) - 5} more")
            print()
    
    # Save analysis
    output_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "browser_automation_duplication_analysis.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Analysis saved to: {output_file}")
    print()
    print("📊 Summary:")
    print(f"   Total files analyzed: {len(browser_files)}")
    print(f"   Duplicate patterns found: {len(analysis['duplicates'])}")
    print(f"   Recommendations: {len(analysis['recommendations'])}")


if __name__ == "__main__":
    main()

