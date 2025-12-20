"""
Captain's Tool: Quick ROI Calculator
=====================================

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt captain.calculate_roi' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/captain_coordination_tools.py → ROICalculatorTool
Registry: captain.calculate_roi

Quickly calculate ROI for a task to decide priority.

Usage: python tools/captain_roi_quick_calc.py --points 1000 --complexity 50 --autonomy 2

Author: Agent-4 (Captain)
Date: 2025-10-13
Deprecated: 2025-01-27 (Agent-6 - V2 Tools Flattening)
"""

import warnings

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt captain.calculate_roi' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy compatibility - delegate to tools_v2
# For migration path, use: python -m tools_v2.toolbelt captain.calculate_roi

import argparse


def calculate_task_roi(points: int, complexity: int, v2_impact: int = 0, autonomy_impact: int = 0):
    """
    Calculate ROI for a task.

    ROI = (Reward) / (Difficulty)

    Reward = points + (v2_impact * 100) + (autonomy_impact * 200)
    Difficulty = complexity

    Autonomy weighted 2x because long-term goal!
    """
    # Delegate to tools_v2 adapter
    try:
        from tools_v2.categories.captain_coordination_tools import ROICalculatorTool
        
        tool = ROICalculatorTool()
        result = tool.execute({
            "points": points,
            "complexity": complexity,
            "v2_impact": v2_impact,
            "autonomy_impact": autonomy_impact
        }, None)
        
        if result.success:
            roi = result.output.get("roi", 0)
            reward = result.output.get("reward", 0)
            
            print(f"\n{'='*60}")
            print("ROI CALCULATION")
            print(f"{'='*60}")
            print(f"\n📊 INPUTS:")
            print(f"  Base Points: {points}")
            print(f"  Complexity: {complexity}")
            print(f"  V2 Impact: {v2_impact} violations fixed")
            print(f"  Autonomy Impact: {autonomy_impact}/3")
            print(f"\n💰 REWARD: {reward}")
            print(f"📈 ROI: {roi:.2f}\n")
            
            return roi
        else:
            print(f"❌ Error: {result.error_message}")
            return 0.0
    except ImportError:
        # Fallback to original implementation
        reward = points + (v2_impact * 100) + (autonomy_impact * 200)
        difficulty = max(complexity, 1)
        roi = reward / difficulty

        print(f"\n{'='*60}")
        print("ROI CALCULATION")
        print(f"{'='*60}")
        print("\n📊 INPUTS:")
        print(f"  Base Points: {points}")
        print(f"  Complexity: {complexity}")
        print(f"  V2 Impact: {v2_impact} violations fixed")
        print(f"  Autonomy Impact: {autonomy_impact}/3")

        print("\n💰 REWARD CALCULATION:")
        print(f"  Base: {points}")
        if v2_impact > 0:
            print(f"  + V2 bonus: {v2_impact * 100} ({v2_impact} × 100)")
        if autonomy_impact > 0:
            print(f"  + Autonomy bonus: {autonomy_impact * 200} ({autonomy_impact} × 200)")
        print(f"  = Total Reward: {reward}")

        print("\n📈 ROI:")
        print(f"  ROI = {reward} / {difficulty}")
        print(f"  ROI = {roi:.2f}")

        if roi > 30:
            print("\n🔥 HIGH ROI - Prioritize this task!")
        elif roi > 15:
            print("\n✅ GOOD ROI - Worth doing")
        else:
            print("\n⚠️  LOW ROI - Consider deprioritizing")

        return roi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate task ROI")
    parser.add_argument("--points", "-p", type=int, required=True, help="Base points")
    parser.add_argument("--complexity", "-c", type=int, required=True, help="Complexity score")
    parser.add_argument("--v2", "-v", type=int, default=0, help="V2 violations fixed")
    parser.add_argument("--autonomy", "-a", type=int, default=0, help="Autonomy impact (0-3)")

    args = parser.parse_args()

    calculate_task_roi(args.points, args.complexity, args.v2, args.autonomy)
