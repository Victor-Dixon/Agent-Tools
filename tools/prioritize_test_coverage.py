#!/usr/bin/env python3
"""
Prioritize Test Coverage - Critical Systems First
==================================================

Analyzes test coverage gaps and prioritizes critical systems for testing.
Target: Increase from 7.4% to 25%+ coverage for critical systems.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


def load_analysis_files() -> Tuple[Dict, Dict]:
    """Load project and test analysis files."""
    project_analysis = {}
    test_analysis = {}
    
    try:
        with open(PROJECT_ROOT / "project_analysis.json", 'r', encoding='utf-8') as f:
            project_analysis = json.load(f)
    except Exception:
        pass
    
    try:
        with open(PROJECT_ROOT / "test_analysis.json", 'r', encoding='utf-8') as f:
            test_analysis = json.load(f)
    except Exception:
        pass
    
    return project_analysis, test_analysis


def identify_critical_systems(project_analysis: Dict) -> List[Tuple[str, int, str]]:
    """Identify critical systems based on complexity and domain."""
    critical_systems = []
    
    # Critical domains
    critical_domains = [
        'core/error_handling',
        'core/messaging',
        'core/file_locking',
        'discord_commander',
        'services/contract_service',
        'services/agent_management',
        'web',
        'core/managers'
    ]
    
    for file_path, file_data in project_analysis.items():
        if not isinstance(file_data, dict):
            continue
        
        complexity = file_data.get('complexity', 0)
        file_path_str = str(file_path).replace('\\', '/')
        
        # Check if in critical domain
        is_critical = any(domain in file_path_str for domain in critical_domains)
        
        # High complexity = critical
        is_high_complexity = complexity >= 15
        
        # Has classes = likely important
        has_classes = len(file_data.get('classes', {})) > 0
        
        if is_critical or (is_high_complexity and has_classes):
            priority = 'HIGH' if is_critical else 'MEDIUM'
            critical_systems.append((file_path, complexity, priority))
    
    # Sort by priority and complexity
    critical_systems.sort(key=lambda x: (x[2] == 'HIGH', x[1]), reverse=True)
    
    return critical_systems


def find_test_gaps(project_analysis: Dict, test_analysis: Dict) -> Dict:
    """Find files without tests."""
    test_files = set(test_analysis.keys())
    project_files = set(project_analysis.keys())
    
    files_without_tests = []
    for file_path in project_files:
        if not isinstance(file_path, str):
            continue
        
        # Check if test exists
        has_test = any(
            test_file for test_file in test_files
            if file_path.replace('src/', '').replace('tools/', '') in test_file or
               Path(file_path).stem in test_file
        )
        
        if not has_test:
            file_data = project_analysis.get(file_path, {})
            if isinstance(file_data, dict):
                complexity = file_data.get('complexity', 0)
                has_classes = len(file_data.get('classes', {})) > 0
                files_without_tests.append({
                    'file': file_path,
                    'complexity': complexity,
                    'has_classes': has_classes
                })
    
    return {
        'total_files': len(project_files),
        'files_with_tests': len(project_files) - len(files_without_tests),
        'files_without_tests': files_without_tests,
        'coverage_percentage': (len(project_files) - len(files_without_tests)) / len(project_files) * 100 if project_files else 0
    }


def generate_test_priority_plan(critical_systems: List[Tuple], test_gaps: Dict) -> Dict:
    """Generate prioritized test coverage plan."""
    # Prioritize critical systems without tests
    high_priority = []
    medium_priority = []
    
    critical_file_paths = {file_path for file_path, _, _ in critical_systems}
    
    for file_info in test_gaps['files_without_tests']:
        file_path = file_info['file']
        if file_path in critical_file_paths:
            high_priority.append(file_info)
        elif file_info['complexity'] >= 10 or file_info['has_classes']:
            medium_priority.append(file_info)
    
    plan = {
        'current_coverage': test_gaps['coverage_percentage'],
        'target_coverage': 25.0,
        'coverage_gap': 25.0 - test_gaps['coverage_percentage'],
        'priority_breakdown': {
            'high_priority': {
                'count': len(high_priority),
                'files': high_priority[:50]  # Top 50
            },
            'medium_priority': {
                'count': len(medium_priority),
                'files': medium_priority[:50]  # Top 50
            }
        },
        'recommended_approach': {
            'phase_1': 'Test critical systems (error_handling, messaging, file_locking)',
            'phase_2': 'Test high-complexity files (complexity >= 15)',
            'phase_3': 'Test files with classes but no tests',
            'phase_4': 'Test remaining files to reach 25% coverage'
        },
        'estimated_effort': {
            'high_priority': len(high_priority) * 2,  # 2 hours per test file
            'medium_priority': len(medium_priority) * 1.5,  # 1.5 hours per test file
            'total_hours': len(high_priority) * 2 + len(medium_priority) * 1.5
        }
    }
    
    return plan


def main():
    """Analyze test coverage and generate priority plan."""
    print("🔍 Analyzing test coverage gaps...")
    print()
    
    project_analysis, test_analysis = load_analysis_files()
    
    if not project_analysis:
        print("❌ No project analysis data found")
        return
    
    # Find test gaps
    test_gaps = find_test_gaps(project_analysis, test_analysis)
    
    print(f"📊 Test Coverage Analysis:")
    print(f"   Current coverage: {test_gaps['coverage_percentage']:.1f}%")
    print(f"   Files with tests: {test_gaps['files_with_tests']}")
    print(f"   Files without tests: {len(test_gaps['files_without_tests'])}")
    print()
    
    # Identify critical systems
    critical_systems = identify_critical_systems(project_analysis)
    
    print(f"🎯 Critical Systems Identified: {len(critical_systems)}")
    print(f"   High priority: {sum(1 for _, _, p in critical_systems if p == 'HIGH')}")
    print(f"   Medium priority: {sum(1 for _, _, p in critical_systems if p == 'MEDIUM')}")
    print()
    
    # Generate plan
    plan = generate_test_priority_plan(critical_systems, test_gaps)
    
    print("📋 Test Coverage Priority Plan:")
    print(f"   Target coverage: {plan['target_coverage']}%")
    print(f"   Coverage gap: {plan['coverage_gap']:.1f}%")
    print(f"   High priority files: {plan['priority_breakdown']['high_priority']['count']}")
    print(f"   Medium priority files: {plan['priority_breakdown']['medium_priority']['count']}")
    print(f"   Estimated effort: {plan['estimated_effort']['total_hours']:.0f} hours")
    print()
    
    # Save plan
    plan_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "test_coverage_priority_plan.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2)
    
    print(f"✅ Test coverage plan saved to: {plan_file}")
    print()
    print("🎯 Recommended Approach:")
    for phase, description in plan['recommended_approach'].items():
        print(f"   {phase}: {description}")


if __name__ == "__main__":
    main()

