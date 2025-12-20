#!/usr/bin/env python3
"""
Analyze Web Integration Gaps
=============================

Identifies files that need web layer wiring (routes/handlers).
Prioritizes high-value integrations.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Existing web routes/handlers
EXISTING_ROUTES = {
    'task': 'src/web/task_routes.py',
    'contract': 'src/web/contract_routes.py',
    'core': 'src/web/core_routes.py',
    'workflow': 'src/web/workflow_routes.py',
    'services': 'src/web/services_routes.py',
    'coordination': 'src/web/coordination_routes.py',
    'integrations': 'src/web/integrations_routes.py',
    'monitoring': 'src/web/monitoring_routes.py',
    'scheduler': 'src/web/scheduler_routes.py',
    'vision': 'src/web/vision_routes.py',
    'engines': 'src/web/engines_routes.py',
    'repository_merge': 'src/web/repository_merge_routes.py',
    'vector_database': 'src/web/vector_database/routes.py',
    'message': 'src/web/vector_database/message_routes.py',
}

# High-value integration priorities (based on feature access blocking)
HIGH_VALUE_PRIORITIES = {
    # Core Managers - Critical for system operations
    'src/core/managers/core_execution_manager.py': 10,
    'src/core/managers/core_service_manager.py': 10,
    'src/core/managers/core_resource_manager.py': 10,
    'src/core/managers/core_recovery_manager.py': 9,
    'src/core/managers/core_results_manager.py': 9,
    'src/core/managers/core_service_coordinator.py': 9,
    'src/core/managers/core_onboarding_manager.py': 8,
    
    # Execution Managers - High value for task management
    'src/core/managers/execution/execution_coordinator.py': 9,
    'src/core/managers/execution/task_manager.py': 9,
    'src/core/managers/execution/task_executor.py': 8,
    
    # Monitoring Managers - Critical for observability
    'src/core/managers/monitoring/metric_manager.py': 9,
    'src/core/managers/monitoring/alert_manager.py': 9,
    'src/core/managers/monitoring/widget_manager.py': 8,
    'src/core/managers/monitoring/metrics_manager.py': 8,
    
    # Results Managers - High value for analytics
    'src/core/managers/results/analysis_results_processor.py': 8,
    'src/core/managers/results/validation_results_processor.py': 8,
    
    # Services - Critical for feature access
    'src/services/agent_management.py': 10,
    'src/services/contract_service.py': 10,
    'src/services/swarm_intelligence_manager.py': 9,
    'src/services/portfolio_service.py': 8,
    'src/services/ai_service.py': 8,
    'src/services/vector_database_service_unified.py': 8,
    'src/services/message_batching_service.py': 7,
    'src/services/chat_presence/chat_presence_orchestrator.py': 7,
    'src/services/learning_recommender.py': 6,
    'src/services/recommendation_engine.py': 6,
    'src/services/performance_analyzer.py': 6,
    'src/services/work_indexer.py': 6,
    
    # Manager utilities
    'src/core/managers/manager_metrics.py': 7,
    'src/core/managers/manager_operations.py': 7,
    'src/core/managers/registry.py': 7,
}

# Files to check
FILES_TO_CHECK = [
    # Core Managers
    'src/core/managers/core_execution_manager.py',
    'src/core/managers/core_service_manager.py',
    'src/core/managers/core_resource_manager.py',
    'src/core/managers/core_recovery_manager.py',
    'src/core/managers/core_results_manager.py',
    'src/core/managers/core_service_coordinator.py',
    'src/core/managers/core_onboarding_manager.py',
    'src/core/managers/execution/execution_coordinator.py',
    'src/core/managers/execution/task_manager.py',
    'src/core/managers/monitoring/metric_manager.py',
    'src/core/managers/monitoring/alert_manager.py',
    'src/core/managers/monitoring/widget_manager.py',
    'src/core/managers/results/analysis_results_processor.py',
    'src/core/managers/results/validation_results_processor.py',
    
    # Services
    'src/services/agent_management.py',
    'src/services/contract_service.py',
    'src/services/swarm_intelligence_manager.py',
    'src/services/portfolio_service.py',
    'src/services/ai_service.py',
    'src/services/vector_database_service_unified.py',
    'src/services/message_batching_service.py',
    'src/services/chat_presence/chat_presence_orchestrator.py',
    'src/services/learning_recommender.py',
    'src/services/recommendation_engine.py',
    'src/services/performance_analyzer.py',
    'src/services/work_indexer.py',
    
    # Additional high-value files
    'src/core/managers/manager_metrics.py',
    'src/core/managers/manager_operations.py',
    'src/core/managers/registry.py',
]


def check_web_integration(file_path: Path) -> Tuple[bool, str]:
    """
    Check if file has web integration.
    
    Returns:
        (has_integration, route_name)
    """
    # Check if file exists
    if not file_path.exists():
        return False, "file_not_found"
    
    # Read file to check for web integration patterns
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception:
        return False, "read_error"
    
    # Check for web route references
    web_patterns = [
        'from src.web',
        'import.*web',
        '@app.route',
        '@blueprint.route',
        'Flask',
        'Blueprint',
    ]
    
    has_web_refs = any(pattern in content for pattern in web_patterns)
    
    # Check if corresponding route/handler exists
    file_name = file_path.stem
    route_name = None
    
    # Try to match with existing routes
    for route_key, route_path in EXISTING_ROUTES.items():
        if route_key in file_name.lower() or file_name.lower() in route_key:
            route_file = PROJECT_ROOT / route_path
            if route_file.exists():
                return True, route_key
    
    # Check for handler file
    handler_file = PROJECT_ROOT / f"src/web/{file_name}_handlers.py"
    if handler_file.exists():
        return True, f"{file_name}_handler"
    
    # Check for route file
    route_file = PROJECT_ROOT / f"src/web/{file_name}_routes.py"
    if route_file.exists():
        return True, f"{file_name}_route"
    
    return False, None


def analyze_integration_gaps() -> Dict:
    """Analyze integration gaps and generate report."""
    results = {
        'total_files': len(FILES_TO_CHECK),
        'integrated': [],
        'missing': [],
        'high_priority': [],
        'medium_priority': [],
        'low_priority': [],
    }
    
    for file_path_str in FILES_TO_CHECK:
        file_path = PROJECT_ROOT / file_path_str
        has_integration, route_name = check_web_integration(file_path)
        
        # Get priority
        relative_path = str(file_path.relative_to(PROJECT_ROOT))
        priority = HIGH_VALUE_PRIORITIES.get(relative_path, 5)
        
        file_info = {
            'file': file_path_str,
            'relative_path': relative_path,
            'has_integration': has_integration,
            'route_name': route_name,
            'priority': priority,
            'exists': file_path.exists(),
        }
        
        if has_integration:
            results['integrated'].append(file_info)
        else:
            results['missing'].append(file_info)
            
            if priority >= 8:
                results['high_priority'].append(file_info)
            elif priority >= 6:
                results['medium_priority'].append(file_info)
            else:
                results['low_priority'].append(file_info)
    
    # Sort by priority
    results['high_priority'].sort(key=lambda x: x['priority'], reverse=True)
    results['medium_priority'].sort(key=lambda x: x['priority'], reverse=True)
    results['low_priority'].sort(key=lambda x: x['priority'], reverse=True)
    
    return results


def generate_report(results: Dict) -> str:
    """Generate human-readable report."""
    total = results['total_files']
    integrated = len(results['integrated'])
    missing = len(results['missing'])
    completion = (integrated / total * 100) if total > 0 else 0
    
    report = f"""
{'='*60}
WEB INTEGRATION GAP ANALYSIS
{'='*60}

Summary:
  Total Files Checked: {total}
  Integrated: {integrated} ({completion:.1f}%)
  Missing: {missing} ({100-completion:.1f}%)

High Priority ({len(results['high_priority'])} files):
"""
    
    for item in results['high_priority']:
        report += f"  ⚠️  Priority {item['priority']}: {item['relative_path']}\n"
    
    report += f"\nMedium Priority ({len(results['medium_priority'])} files):\n"
    for item in results['medium_priority'][:10]:  # Show top 10
        report += f"  • Priority {item['priority']}: {item['relative_path']}\n"
    
    report += f"\nLow Priority ({len(results['low_priority'])} files):\n"
    for item in results['low_priority'][:5]:  # Show top 5
        report += f"  • Priority {item['priority']}: {item['relative_path']}\n"
    
    report += f"\n{'='*60}\n"
    
    return report


if __name__ == "__main__":
    print("🔍 Analyzing web integration gaps...")
    results = analyze_integration_gaps()
    
    # Print report
    print(generate_report(results))
    
    # Save JSON report
    report_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "web_integration_gaps.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f"✅ Report saved to: {report_file}")
    
    # Print completion status
    total = results['total_files']
    integrated = len(results['integrated'])
    print(f"\n📊 Status: {integrated}/{total} files integrated ({integrated/total*100:.1f}%)")
    print(f"🎯 High Priority Missing: {len(results['high_priority'])} files")

