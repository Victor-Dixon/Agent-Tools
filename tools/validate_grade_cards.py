#!/usr/bin/env python3
"""
Sales Funnel Ecosystem Grade Card Validator
===========================================

Validates grade card YAML files for:
- Required structure and fields
- Scoring ranges (0-5)
- Category weights sum to 100
- Top 10 fixes format
- File completeness

Author: Agent-4
V2 Compliant: <300 lines
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Grade card file locations
GRADE_CARD_PATHS = [
    Path("D:/websites/crosbyultimateevents.com/GRADE_CARD_SALES_FUNNEL.yaml"),
    Path("D:/websites/dadudekc.com/GRADE_CARD_SALES_FUNNEL.yaml"),
    Path("D:/websites/FreeRideInvestor/GRADE_CARD_SALES_FUNNEL.yaml"),
    Path("D:/websites/houstonsipqueen.com/GRADE_CARD_SALES_FUNNEL.yaml"),
    Path("D:/websites/TradingRobotPlugWeb/GRADE_CARD_SALES_FUNNEL.yaml"),
]


def validate_structure(data: Dict) -> Tuple[bool, List[str]]:
    """Validate grade card structure."""
    errors = []
    
    # Check top-level structure
    if "gradecard" not in data:
        errors.append("Missing 'gradecard' root key")
        return False, errors
    
    gc = data["gradecard"]
    
    # Required top-level fields
    required_fields = ["version", "site", "date", "total_points", "scoring_scale", "categories", "final"]
    for field in required_fields:
        if field not in gc:
            errors.append(f"Missing required field: {field}")
    
    # Validate scoring_scale
    if "scoring_scale" in gc:
        expected_scores = ["0", "1", "2", "3", "4", "5"]
        for score in expected_scores:
            if score not in gc["scoring_scale"]:
                errors.append(f"Missing scoring_scale value: {score}")
    
    # Validate categories
    if "categories" in gc:
        total_weight = 0
        for cat in gc["categories"]:
            if "name" not in cat or "weight_points" not in cat:
                errors.append(f"Category missing name or weight_points")
            else:
                total_weight += cat.get("weight_points", 0)
            
            # Validate criteria
            if "criteria" in cat:
                for crit in cat["criteria"]:
                    required_crit_fields = ["id", "name", "score_0_to_5", "evidence", "gap", "fix", "priority", "owner", "eta"]
                    for field in required_crit_fields:
                        if field not in crit:
                            errors.append(f"Criteria {crit.get('id', 'unknown')} missing field: {field}")
                    
                    # Validate score range
                    score = crit.get("score_0_to_5", -1)
                    if not (0 <= score <= 5):
                        errors.append(f"Criteria {crit.get('id', 'unknown')} has invalid score: {score} (must be 0-5)")
        
        # Validate total weight
        if total_weight != 100:
            errors.append(f"Total category weight is {total_weight}, expected 100")
    
    # Validate final section
    if "final" in gc:
        final = gc["final"]
        if "weighted_score_out_of_100" not in final:
            errors.append("Missing final.weighted_score_out_of_100")
        if "letter_grade" not in final:
            errors.append("Missing final.letter_grade")
        if "top_10_fixes" not in final:
            errors.append("Missing final.top_10_fixes")
        else:
            fixes = final["top_10_fixes"]
            if len(fixes) != 10:
                errors.append(f"top_10_fixes has {len(fixes)} items, expected 10")
            for i, fix in enumerate(fixes, 1):
                required_fix_fields = ["priority", "item", "owner", "eta"]
                for field in required_fix_fields:
                    if field not in fix:
                        errors.append(f"Fix #{i} missing field: {field}")
    
    return len(errors) == 0, errors


def validate_file(file_path: Path) -> Tuple[bool, Dict]:
    """Validate a single grade card file."""
    if not file_path.exists():
        return False, {"error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if data is None:
            return False, {"error": "File is empty or invalid YAML"}
        
        is_valid, errors = validate_structure(data)
        
        result = {
            "file": str(file_path.name),
            "path": str(file_path),
            "valid": is_valid,
            "errors": errors,
            "site": data.get("gradecard", {}).get("site", "unknown"),
            "score": data.get("gradecard", {}).get("final", {}).get("weighted_score_out_of_100", "N/A"),
            "grade": data.get("gradecard", {}).get("final", {}).get("letter_grade", "N/A"),
        }
        
        return is_valid, result
        
    except yaml.YAMLError as e:
        return False, {"error": f"YAML parsing error: {e}"}
    except Exception as e:
        return False, {"error": f"Validation error: {e}"}


def main():
    """Run validation on all grade cards."""
    print("=" * 70)
    print("Sales Funnel Ecosystem Grade Card Validator")
    print("=" * 70)
    print()
    
    results = []
    all_valid = True
    
    for file_path in GRADE_CARD_PATHS:
        is_valid, result = validate_file(file_path)
        results.append(result)
        if not is_valid:
            all_valid = False
    
    # Print results
    for result in results:
        status = "✅ VALID" if result.get("valid") else "❌ INVALID"
        print(f"{status}: {result.get('site', 'unknown')}")
        print(f"  File: {result.get('file', 'unknown')}")
        print(f"  Score: {result.get('score', 'N/A')}/100")
        print(f"  Grade: {result.get('grade', 'N/A')}")
        
        if "error" in result:
            print(f"  Error: {result['error']}")
        elif result.get("errors"):
            print(f"  Errors ({len(result['errors'])}):")
            for error in result["errors"][:5]:  # Show first 5 errors
                print(f"    - {error}")
            if len(result["errors"]) > 5:
                print(f"    ... and {len(result['errors']) - 5} more")
        print()
    
    # Summary
    valid_count = sum(1 for r in results if r.get("valid"))
    total_count = len(results)
    
    print("=" * 70)
    print(f"Summary: {valid_count}/{total_count} grade cards valid")
    print("=" * 70)
    
    if all_valid:
        print("✅ All grade cards are valid!")
        return 0
    else:
        print("❌ Some grade cards have validation errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())

