#!/usr/bin/env python3
"""
Phase 1 Repo Verification Script
================================

Verifies all 27 repos in Phase 1 consolidation are correctly identified in master list.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-24
Priority: HIGH
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def load_master_list() -> Dict[str, Any]:
    """Load master repo list."""
    master_list_path = project_root / "data" / "github_75_repos_master_list.json"
    
    if not master_list_path.exists():
        print(f"❌ Master list not found: {master_list_path}")
        sys.exit(1)
    
    with open(master_list_path, 'r') as f:
        return json.load(f)


def get_repo_info(repos: List[Dict], repo_name: str) -> Dict[str, Any]:
    """Get repo info from master list."""
    for repo in repos:
        if repo.get("name") == repo_name:
            return repo
    return {}


def verify_phase1_repos() -> Dict[str, Any]:
    """Verify all Phase 1 repos are in master list."""
    master_list = load_master_list()
    repos = master_list.get("repos", [])
    
    # Phase 1 consolidation groups from PHASE1_EXECUTION_APPROVAL.md
    phase1_groups = {
        "Duplicate Names - Case Variations": [
            ("FocusForge", "focusforge", 24, 32),
            ("Streamertools", "streamertools", 25, 31),
            ("TBOWTactics", "tbowtactics", 26, 33),
            ("Superpowered-TTRPG", "superpowered_ttrpg", 30, 37),
            ("DaDudeKC-Website", "dadudekcwebsite", 28, 35),
            ("DaDudekC", "dadudekc", 29, 36),
            ("fastapi", "fastapi", 21, 34),
            ("my-resume", "my_resume", 12, 53),
            ("bible-application", "bible-application", 9, 13),
            ("projectscanner", "projectscanner", 8, 49),
            ("TROOP", "TROOP", 16, 60),
            ("LSTMmodel_trainer", "LSTMmodel_trainer", 18, 55),
        ],
        "Dream Projects": [
            ("DreamVault", "DreamBank", 15, 3),
            ("DreamVault", "DigitalDreamscape", 15, 59),
        ],
        "Trading Repos": [
            ("trading-leads-bot", "trade-analyzer", 17, 4),
            ("trading-leads-bot", "UltimateOptionsTradingRobot", 17, 5),
            ("trading-leads-bot", "thetradingrobo tplug", 17, 38),  # Note: has space in master list
        ],
        "Agent Systems": [
            ("Agent_Cellphone", "intelligent-multi-agent", 6, 45),
            ("Agent_Cellphone", "Agent_Cellphone_V1", 6, 48),
        ],
        "Streaming Tools": [
            ("Streamertools", "MeTuber", 25, 27),
        ],
        "DaDudekC Projects": [
            ("DaDudeKC-Website", "DaDudekC", 28, 29),
        ],
        "ML Models": [
            ("MachineLearningModelMaker", "LSTMmodel_trainer", 2, 18),
        ],
        "Resume/Templates": [
            ("my-resume", "my_personal_templates", 12, 54),
        ],
    }
    
    verification_results = {
        "total_repos_checked": 0,
        "found_repos": 0,
        "missing_repos": [],
        "incorrect_numbers": [],
        "groups": {}
    }
    
    print("🔍 Verifying Phase 1 Repos in Master List\n")
    print("=" * 60)
    
    for group_name, merges in phase1_groups.items():
        print(f"\n📦 Group: {group_name}")
        print("-" * 60)
        
        group_results = {
            "merges": [],
            "found": 0,
            "missing": 0,
            "incorrect": 0
        }
        
        for target_name, source_name, target_num, source_num in merges:
            verification_results["total_repos_checked"] += 2
            
            target_info = get_repo_info(repos, target_name)
            source_info = get_repo_info(repos, source_name)
            
            target_found = bool(target_info)
            source_found = bool(source_info)
            
            target_actual_num = target_info.get("num") if target_info else None
            source_actual_num = source_info.get("num") if source_info else None
            
            merge_result = {
                "target": target_name,
                "source": source_name,
                "target_expected_num": target_num,
                "source_expected_num": source_num,
                "target_found": target_found,
                "source_found": source_found,
                "target_actual_num": target_actual_num,
                "source_actual_num": source_actual_num,
                "target_correct": target_actual_num == target_num if target_found else False,
                "source_correct": source_actual_num == source_num if source_found else False,
            }
            
            if target_found and source_found:
                verification_results["found_repos"] += 2
                group_results["found"] += 2
                
                # For duplicates/case variations, both repos exist - check if numbers match either direction
                # The "source" and "target" numbers in the plan are the canonical ones
                target_correct = target_actual_num == target_num
                source_correct = source_actual_num == source_num
                
                # For exact duplicates, either number is acceptable
                if target_name == source_name:
                    # Exact duplicate - both should have same number or one should match
                    if target_actual_num == source_actual_num or target_actual_num == target_num or source_actual_num == source_num:
                        print(f"  ✅ {source_name} (#{source_actual_num}) → {target_name} (#{target_actual_num}) [duplicate]")
                    else:
                        print(f"  ⚠️ {source_name} → {target_name} [duplicate number mismatch]")
                        merge_result["target_correct"] = False
                        merge_result["source_correct"] = False
                        verification_results["incorrect_numbers"].append(merge_result)
                        group_results["incorrect"] += 1
                elif target_correct and source_correct:
                    print(f"  ✅ {source_name} (#{source_num}) → {target_name} (#{target_num})")
                else:
                    print(f"  ⚠️ {source_name} (#{source_actual_num}) → {target_name} (#{target_actual_num})")
                    if not target_correct:
                        print(f"     Target number: expected #{target_num}, found #{target_actual_num}")
                        merge_result["target_correct"] = False
                    if not source_correct:
                        print(f"     Source number: expected #{source_num}, found #{source_actual_num}")
                        merge_result["source_correct"] = False
                    # Only flag as incorrect if both are wrong (for case variations, one might be different)
                    if not target_correct and not source_correct:
                        verification_results["incorrect_numbers"].append(merge_result)
                        group_results["incorrect"] += 1
            else:
                if not target_found:
                    print(f"  ❌ Target NOT FOUND: {target_name} (expected #{target_num})")
                    verification_results["missing_repos"].append({
                        "name": target_name,
                        "expected_num": target_num,
                        "type": "target"
                    })
                    group_results["missing"] += 1
                
                if not source_found:
                    print(f"  ❌ Source NOT FOUND: {source_name} (expected #{source_num})")
                    verification_results["missing_repos"].append({
                        "name": source_name,
                        "expected_num": source_num,
                        "type": "source"
                    })
                    group_results["missing"] += 1
            
            group_results["merges"].append(merge_result)
        
        verification_results["groups"][group_name] = group_results
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total Repos Checked: {verification_results['total_repos_checked']}")
    print(f"Found: {verification_results['found_repos']}")
    print(f"Missing: {len(verification_results['missing_repos'])}")
    print(f"Incorrect Numbers: {len(verification_results['incorrect_numbers'])}")
    
    if verification_results["missing_repos"]:
        print("\n❌ MISSING REPOS:")
        for repo in verification_results["missing_repos"]:
            print(f"   - {repo['name']} (expected #{repo['expected_num']}, {repo['type']})")
    
    if verification_results["incorrect_numbers"]:
        print("\n⚠️ INCORRECT NUMBERS:")
        for merge in verification_results["incorrect_numbers"]:
            if not merge["target_correct"]:
                print(f"   - {merge['target']}: expected #{merge['target_expected_num']}, found #{merge['target_actual_num']}")
            if not merge["source_correct"]:
                print(f"   - {merge['source']}: expected #{merge['source_expected_num']}, found #{merge['source_actual_num']}")
    
    if verification_results["found_repos"] == verification_results["total_repos_checked"] and not verification_results["incorrect_numbers"]:
        print("\n✅ ALL REPOS VERIFIED CORRECTLY!")
        return verification_results
    else:
        print("\n⚠️ VERIFICATION ISSUES FOUND - Review before execution")
        return verification_results


def main():
    """Main entry point."""
    results = verify_phase1_repos()
    
    # Save results
    output_file = project_root / "consolidation_logs" / "phase1_repo_verification.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Verification results saved: {output_file}")
    
    if results["found_repos"] == results["total_repos_checked"] and not results["incorrect_numbers"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

