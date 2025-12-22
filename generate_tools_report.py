import os
from pathlib import Path
from collections import defaultdict

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def get_category(filepath, root_dir):
    parts = filepath.parts
    
    # Handle tools_v2/categories
    if 'tools_v2' in parts and 'categories' in parts:
        idx = parts.index('categories')
        if idx + 1 < len(parts):
            return parts[idx+1].replace('.py', '')
    
    # Handle tools/ subdirectories
    rel_path = filepath.relative_to(root_dir)
    if len(rel_path.parts) > 1:
        return rel_path.parts[0]
    
    # Handle tools/ root files heuristics
    name = filepath.name.lower()
    if name.startswith('agent'): return 'agent_ops'
    if name.startswith('analyze') or name.startswith('analysis'): return 'analysis'
    if name.startswith('auto'): return 'automation'
    if name.startswith('captain'): return 'captain'
    if name.startswith('check'): return 'checks'
    if name.startswith('cleanup'): return 'cleanup'
    if name.startswith('debug'): return 'debug'
    if name.startswith('deploy'): return 'deployment'
    if name.startswith('find'): return 'discovery'
    if name.startswith('fix'): return 'fixes'
    if name.startswith('generate'): return 'generators'
    if name.startswith('monitor'): return 'monitoring'
    if name.startswith('scan'): return 'scanning'
    if name.startswith('setup'): return 'setup'
    if name.startswith('test'): return 'testing'
    if name.startswith('validate') or name.startswith('verify'): return 'verification'
    if name.startswith('wordpress'): return 'wordpress'
    
    return 'misc'

def generate_report():
    tools_dirs = ['tools', 'tools_v2']
    tools_data = []
    
    print("Scanning tools...")
    
    for d in tools_dirs:
        root = Path(d)
        if not root.exists():
            continue
            
        for path in root.rglob('*.py'):
            if path.name == '__init__.py' or 'test' in path.name.lower():
                continue
                
            loc = count_lines(path)
            if loc == 0: continue
            
            category = get_category(path, root)
            tools_data.append({
                'name': path.name,
                'path': str(path),
                'loc': loc,
                'category': category
            })

    # Group by category
    by_category = defaultdict(list)
    for tool in tools_data:
        by_category[tool['category']].append(tool)
        
    # Sort categories by total LOC
    cat_stats = []
    for cat, tools in by_category.items():
        total_loc = sum(t['loc'] for t in tools)
        avg_loc = total_loc / len(tools)
        # Sort tools in category by LOC descending
        tools.sort(key=lambda x: x['loc'], reverse=True)
        cat_stats.append({
            'name': cat,
            'total_loc': total_loc,
            'avg_loc': avg_loc,
            'count': len(tools),
            'tools': tools
        })
    
    cat_stats.sort(key=lambda x: x['total_loc'], reverse=True)
    
    # Generate Markdown
    md = ["# 🛠️ Inventory of Tools Ranked by Value (LOC)\n"]
    md.append(f"**Total Tools:** {len(tools_data)}")
    md.append(f"**Total Lines of Code:** {sum(t['loc'] for t in tools_data)}\n")
    
    md.append("## 📊 Category Summary\n")
    md.append("| Category | Tools | Total LOC | Avg LOC |")
    md.append("|----------|-------|-----------|---------|")
    for cat in cat_stats:
        md.append(f"| {cat['name']} | {cat['count']} | {cat['total_loc']} | {cat['avg_loc']:.0f} |")
    md.append("\n---\n")
    
    for cat in cat_stats:
        md.append(f"## 📂 {cat['name']} ({cat['count']} tools)\n")
        md.append(f"*Total Value (LOC): {cat['total_loc']}*\n")
        
        # Table for tools
        md.append("| Rank | Tool Name | Value (LOC) | Path |")
        md.append("|------|-----------|-------------|------|")
        for i, tool in enumerate(cat['tools'], 1):
            md.append(f"| {i} | `{tool['name']}` | {tool['loc']} | `{tool['path']}` |")
        md.append("\n")
        
    with open('TOOLS_RANKING_REPORT.md', 'w') as f:
        f.write('\n'.join(md))
        
    print(f"Report generated: TOOLS_RANKING_REPORT.md with {len(tools_data)} tools")

if __name__ == "__main__":
    generate_report()
