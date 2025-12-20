#!/usr/bin/env python3
"""
Extract All 75 Repos from GitHub Book
======================================

Extracts comprehensive data for all 75 repos from the GitHub book
to enable full consolidation analysis.

Author: Agent-5
Date: 2025-01-27
"""

import re
from pathlib import Path
from typing import Dict, List, Any


def extract_repos_from_book(book_path: Path) -> Dict[int, Dict[str, Any]]:
    """Extract all repo information from the GitHub book."""
    repos = {}
    
    content = book_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    current_repo_num = None
    current_repo_data = {}
    
    for i, line in enumerate(lines):
        # Match chapter headers
        match = re.search(r'Chapter (\d+):\s*Repo #(\d+)\s*-\s*([^\n]+)', line)
        if match:
            # Save previous repo if exists
            if current_repo_num:
                repos[current_repo_num] = current_repo_data
            
            # Start new repo
            current_repo_num = int(match.group(2))
            repo_name = match.group(3).strip()
            current_repo_data = {
                'repo_num': current_repo_num,
                'name': repo_name,
                'chapter': int(match.group(1)),
            }
            continue
        
        # Extract agent
        if '**Analyzed By:**' in line and current_repo_num:
            agent_match = re.search(r'\*\*Analyzed By:\*\*\s*([^\n]+)', line)
            if agent_match:
                current_repo_data['agent'] = agent_match.group(1).strip()
        
        # Extract purpose
        if '**Purpose:**' in line and current_repo_num:
            purpose_match = re.search(r'\*\*Purpose:\*\*\s*([^\n]+)', line)
            if purpose_match:
                current_repo_data['purpose'] = purpose_match.group(1).strip()
        
        # Extract ROI
        if '**ROI:**' in line and current_repo_num:
            roi_match = re.search(r'\*\*ROI:\*\*\s*([^\n]+)', line)
            if roi_match:
                current_repo_data['roi'] = roi_match.group(1).strip()
        
        # Extract recommendation
        if '**Recommendation:**' in line and current_repo_num:
            rec_match = re.search(r'\*\*Recommendation:\*\*\s*([^\n]+)', line)
            if rec_match:
                current_repo_data['recommendation'] = rec_match.group(1).strip()
        
        # Extract category from content
        if current_repo_num and 'trading' in line.lower() and 'category' not in current_repo_data:
            if any(word in line.lower() for word in ['trading', 'trade', 'stock', 'options']):
                current_repo_data['category'] = 'trading'
        elif current_repo_num and 'discord' in line.lower() and 'category' not in current_repo_data:
            if 'discord' in line.lower():
                current_repo_data['category'] = 'discord'
        elif current_repo_num and 'automation' in line.lower() and 'category' not in current_repo_data:
            if 'automation' in line.lower():
                current_repo_data['category'] = 'automation'
        elif current_repo_num and any(word in line.lower() for word in ['ml', 'machine learning', 'ai', 'neural']) and 'category' not in current_repo_data:
            current_repo_data['category'] = 'ml'
        elif current_repo_num and 'web' in line.lower() and 'category' not in current_repo_data:
            current_repo_data['category'] = 'web'
    
    # Save last repo
    if current_repo_num:
        repos[current_repo_num] = current_repo_data
    
    return repos


if __name__ == '__main__':
    book_path = Path('archive/status_updates/GITHUB_75_REPOS_COMPREHENSIVE_ANALYSIS_BOOK.md')
    repos = extract_repos_from_book(book_path)
    
    print(f"Extracted {len(repos)} repos from book")
    print(f"Repo numbers: {sorted(repos.keys())}")
    
    for num in sorted(repos.keys()):
        repo = repos[num]
        print(f"{num:2d}: {repo.get('name', 'Unknown')}")


