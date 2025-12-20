#!/usr/bin/env python3
"""
Unified Test Analysis Tool - V2 Compliant
==========================================

<!-- SSOT Domain: qa -->

Consolidates test analysis capabilities.
Replaces: test_all_discord_commands.py

V2 Compliance: <300 lines, single responsibility
Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedTestAnalyzer:
    """Unified test analysis tool for comprehensive testing."""
    
    def __init__(self):
        """Initialize unified test analyzer."""
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tests_run': [],
            'passed': [],
            'failed': [],
            'summary': {}
        }
    
    def analyze_command_registration(self, bot_module: str = "unified_discord_bot") -> Dict[str, Any]:
        """Analyze command registration in bot module."""
        logger.info(f"🔍 Analyzing command registration in {bot_module}...")
        
        try:
            module_path = f"src.discord_commander.{bot_module}"
            module = __import__(module_path, fromlist=[''])
            
            # Try to get bot class
            bot_class = getattr(module, 'UnifiedDiscordBot', None)
            if not bot_class:
                return {'success': False, 'error': 'Bot class not found'}
            
            # Count commands (would need bot instance, simplified here)
            return {
                'success': True,
                'module': bot_module,
                'bot_class_found': True
            }
        except Exception as e:
            logger.error(f"❌ Error analyzing commands: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_error_handling(self, file_path: str) -> Dict[str, Any]:
        """Analyze error handling in test file."""
        logger.info(f"🛡️  Analyzing error handling in {file_path}...")
        
        try:
            path = Path(file_path)
            if not path.exists():
                return {'success': False, 'error': 'File not found'}
            
            content = path.read_text(encoding='utf-8')
            
            # Count try-except blocks
            try_count = content.count('try:')
            except_count = content.count('except')
            error_handling_ratio = (except_count / try_count * 100) if try_count > 0 else 0
            
            return {
                'success': True,
                'file': file_path,
                'try_blocks': try_count,
                'except_blocks': except_count,
                'error_handling_ratio': round(error_handling_ratio, 2)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_test_coverage(self, test_file: str, source_file: str) -> Dict[str, Any]:
        """Analyze test coverage for a source file."""
        logger.info(f"📊 Analyzing test coverage: {test_file} → {source_file}...")
        
        try:
            test_path = Path(test_file)
            source_path = Path(source_file)
            
            if not test_path.exists():
                return {'success': False, 'error': 'Test file not found'}
            if not source_path.exists():
                return {'success': False, 'error': 'Source file not found'}
            
            # Simple analysis: count test functions vs source functions
            test_content = test_path.read_text(encoding='utf-8')
            source_content = source_path.read_text(encoding='utf-8')
            
            test_functions = test_content.count('def test_')
            source_functions = source_content.count('def ')
            
            coverage_estimate = (test_functions / source_functions * 100) if source_functions > 0 else 0
            
            return {
                'success': True,
                'test_file': test_file,
                'source_file': source_file,
                'test_functions': test_functions,
                'source_functions': source_functions,
                'coverage_estimate': round(coverage_estimate, 2)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate test analysis report."""
        report = f"""# Test Analysis Report

**Generated**: {datetime.now().isoformat()}

## Summary

- **Tests Run**: {len(self.results['tests_run'])}
- **Passed**: {len(self.results['passed'])}
- **Failed**: {len(self.results['failed'])}

## Results

"""
        for test in self.results['tests_run']:
            status = "✅" if test.get('success') else "❌"
            report += f"- {status} {test.get('name', 'Unknown')}\n"
        
        if output_file:
            Path(output_file).write_text(report, encoding='utf-8')
            logger.info(f"✅ Report saved to: {output_file}")
        
        return report
    
    def run_analysis(self, analysis_type: str, **kwargs) -> Dict[str, Any]:
        """Run specified analysis type."""
        if analysis_type == "command_registration":
            return self.analyze_command_registration(kwargs.get('bot_module', 'unified_discord_bot'))
        elif analysis_type == "error_handling":
            return self.analyze_error_handling(kwargs.get('file_path', ''))
        elif analysis_type == "test_coverage":
            return self.analyze_test_coverage(
                kwargs.get('test_file', ''),
                kwargs.get('source_file', '')
            )
        else:
            return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}


def main():
    """CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified test analysis tool")
    parser.add_argument("--type", choices=["command_registration", "error_handling", "test_coverage"],
                       required=True, help="Analysis type")
    parser.add_argument("--bot-module", help="Bot module name (for command_registration)")
    parser.add_argument("--file", help="File path (for error_handling)")
    parser.add_argument("--test-file", help="Test file path (for test_coverage)")
    parser.add_argument("--source-file", help="Source file path (for test_coverage)")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    analyzer = UnifiedTestAnalyzer()
    
    kwargs = {}
    if args.bot_module:
        kwargs['bot_module'] = args.bot_module
    if args.file:
        kwargs['file_path'] = args.file
    if args.test_file:
        kwargs['test_file'] = args.test_file
    if args.source_file:
        kwargs['source_file'] = args.source_file
    
    result = analyzer.run_analysis(args.type, **kwargs)
    
    if args.json:
        output = json.dumps(result, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
        else:
            print(output)
    else:
        if result.get('success'):
            print(f"✅ Analysis complete: {args.type}")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    if args.output and not args.json:
        analyzer.generate_report(args.output)


if __name__ == "__main__":
    main()


