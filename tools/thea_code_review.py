#!/usr/bin/env python3
"""
Thea Code Review Tool - Dream.OS Compliant
===========================================

Uses Thea (ChatGPT custom GPT) to perform V3-compliant code reviews.
Generates structured analysis with compliance checks, findings, and refactor plans.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.services.thea.thea_service import TheaService
    THEA_SERVICE_AVAILABLE = True
except ImportError:
    THEA_SERVICE_AVAILABLE = False
    print("⚠️ TheaService not available - install dependencies")
    print("💡 Install: pip install selenium undetected-chromedriver pyautogui pyperclip")


def generate_code_review_prompt(file_path: Path, context: Optional[str] = None) -> str:
    """Generate structured code review prompt for Thea."""
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    
    # Count lines
    line_count = len(code_content.split('\n'))
    
    # Generate prompt
    prompt = f"""# 🛰️ CODE REVIEW REQUEST - Dream.OS V3 Compliance

## File to Review
**Path**: `{file_path}`
**Lines**: {line_count}
**Context**: {context or "Standard code review"}

## Code Content
```python
{code_content}
```

## Review Requirements

Perform a **Dream.OS-compliant swarm code review** with:

1. **V3 Compliance Check**:
   - File length: < 400 lines
   - Class length: < 200 lines  
   - Function length: < 30 lines
   - Single Responsibility Principle per module
   - Type hints everywhere
   - SOLID principles adherence

2. **Architecture Analysis**:
   - Structural integrity
   - Dependency injection correctness
   - SSOT alignment
   - Hard boundaries
   - Error isolation

3. **Identify Violations**:
   - List all V3 compliance violations
   - Identify multi-responsibility violations
   - Flag missing features (e.g., terminal completion detection)

4. **Generate Refactor Plan**:
   - Module split recommendations
   - File organization
   - Integration points
   - Test requirements

5. **Output Format**:
   - Use structured YAML for refactor plan
   - Provide commit message
   - List next-step tasks for agents

## Expected Response Format

```yaml
findings:
  - type: "V3_COMPLIANCE"
    severity: "HIGH|MEDIUM|LOW"
    issue: "Description"
    location: "file:line"
  
refactor_plan:
  steps:
    - action: "split_module"
      target: "module_name.py"
      into: ["new_module1.py", "new_module2.py"]
  
commit_message: "Refactor: Description"
  
next_steps:
  - task: "Description"
    assigned_to: "Agent-X"
```

**Begin review now.**"""
    
    return prompt


def parse_thea_response(response_text: str) -> Dict:
    """Parse Thea's response into structured format."""
    
    result = {
        "raw_response": response_text,
        "findings": [],
        "refactor_plan": {},
        "commit_message": "",
        "next_steps": [],
        "parsed": False
    }
    
    # Try to extract structured content
    # Look for YAML blocks
    if "```yaml" in response_text:
        yaml_start = response_text.find("```yaml") + 7
        yaml_end = response_text.find("```", yaml_start)
        if yaml_end > yaml_start:
            yaml_content = response_text[yaml_start:yaml_end].strip()
            try:
                import yaml
                parsed = yaml.safe_load(yaml_content)
                if parsed:
                    if "findings" in parsed:
                        result["findings"] = parsed.get("findings", [])
                    if "refactor_plan" in parsed:
                        result["refactor_plan"] = parsed.get("refactor_plan", {})
                    if "commit_message" in parsed:
                        result["commit_message"] = parsed.get("commit_message", "")
                    if "next_steps" in parsed:
                        result["next_steps"] = parsed.get("next_steps", [])
                    result["parsed"] = True
            except ImportError:
                # yaml module not available
                pass
            except Exception as e:
                # YAML parsing failed, will use fallback
                pass
    
    # Extract findings from text if YAML parsing failed
    if not result["parsed"]:
        # Look for common patterns
        if "V3" in response_text or "compliance" in response_text.lower():
            result["findings"].append({
                "type": "V3_COMPLIANCE",
                "severity": "HIGH",
                "issue": "V3 compliance issues detected",
                "location": "file"
            })
    
    return result


def review_code_with_thea(
    file_path: Path,
    context: Optional[str] = None,
    headless: bool = False
) -> Dict:
    """Review code using Thea service."""
    
    if not THEA_SERVICE_AVAILABLE:
        return {
            "error": "TheaService not available",
            "suggestion": "Install dependencies: pip install selenium pyautogui"
        }
    
    print(f"🔍 Starting code review for: {file_path}")
    print("=" * 70)
    
    # Generate prompt
    prompt = generate_code_review_prompt(file_path, context)
    
    # Initialize Thea service
    try:
        thea = TheaService(headless=headless)
        
        # Check cookie freshness first
        print("🍪 Checking cookie freshness...")
        if not thea.are_cookies_fresh():
            print("⚠️ Cookies are stale or missing - refreshing...")
            if not thea.refresh_cookies():
                return {
                    "error": "Failed to refresh cookies",
                    "suggestion": "Run 'python tools/thea/setup_thea_cookies.py' to setup fresh cookies"
                }
        
        # Ensure login with fresh cookies
        print("🔐 Ensuring login with fresh cookies...")
        if not thea.ensure_login():
            return {
                "error": "Failed to login to Thea",
                "suggestion": "Run 'python tools/thea/setup_thea_cookies.py' to setup fresh cookies"
            }
        
        # Send prompt
        print("📤 Sending code review request to Thea...")
        response = thea.send_message(prompt)
        
        if not response:
            return {
                "error": "No response from Thea",
                "suggestion": "Check Thea service connection"
            }
        
        # Parse response
        print("📥 Parsing Thea response...")
        parsed = parse_thea_response(response)
        
        # Save response
        output_dir = Path("thea_code_reviews")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"review_{file_path.stem}_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                "file_path": str(file_path),
                "timestamp": timestamp,
                "review": parsed
            }, f, indent=2)
        
        print(f"✅ Review saved to: {output_file}")
        
        return parsed
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "error": str(e),
            "error_details": error_details,
            "suggestion": "Check Thea service configuration, browser setup, or cookies"
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Code review using Thea")
    parser.add_argument("file", type=Path, help="File to review")
    parser.add_argument("--context", type=str, help="Additional context")
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"❌ File not found: {args.file}")
        return 1
    
    result = review_code_with_thea(args.file, args.context, args.headless)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "suggestion" in result:
            print(f"💡 Suggestion: {result['suggestion']}")
        return 1
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 CODE REVIEW SUMMARY")
    print("=" * 70)
    
    if result.get("findings"):
        print(f"\n🔍 Findings: {len(result['findings'])}")
        for finding in result["findings"]:
            print(f"  - [{finding.get('severity', 'UNKNOWN')}] {finding.get('issue', 'N/A')}")
    
    if result.get("refactor_plan"):
        print(f"\n🔧 Refactor Plan: Available")
    
    if result.get("commit_message"):
        print(f"\n📝 Commit Message:")
        print(f"   {result['commit_message']}")
    
    if result.get("next_steps"):
        print(f"\n📋 Next Steps: {len(result['next_steps'])}")
        for step in result["next_steps"]:
            print(f"  - {step}")
    
    print("\n✅ Review complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

