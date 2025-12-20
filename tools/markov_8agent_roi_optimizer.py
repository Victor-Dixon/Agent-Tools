"""
8-Agent ROI-Based Task Assignment using Markov Optimization
===========================================================

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use: python -m tools_v2.toolbelt bi.roi.optimize
See: tools_v2/categories/bi_tools.py for the adapter.

Assigns optimal tasks to ALL 8 agents based on:
1. ROI (Return on Investment) = Reward / Difficulty
2. Long-term goal alignment (efficient autonomous development)
3. Agent specialization matching
4. Dependency unblocking
5. Strategic value

Axiom: Maximize ROI while advancing autonomous development capability

Author: Agent-4 (Captain)
Date: 2025-10-12
"""

import json

from markov_task_optimizer import MarkovTaskOptimizer, ProjectState, OptimizationTask as Task


def calculate_roi(points: int, complexity: int, v2_impact: int, autonomy_impact: int) -> float:
    """
    Calculate ROI for a task.

    ROI = (Reward) / (Difficulty)

    Reward = points + (v2_impact * 100) + (autonomy_impact * 200)
    Difficulty = complexity

    Autonomy impact weighted 2x because it's our long-term goal!
    """
    reward = points + (v2_impact * 100) + (autonomy_impact * 200)
    difficulty = max(complexity, 1)  # Avoid division by zero
    return reward / difficulty


def load_top_violations():
    """Load top violations from project scanner."""
    with open("project_analysis.json") as f:
        data = json.load(f)

    violations = []
    for filepath, info in data.items():
        if info.get("language") != ".py":
            continue

        num_functions = len(info.get("functions", []))
        num_classes = len(info.get("classes", {}))
        complexity = info.get("complexity", 0)

        if num_functions > 10 or num_classes > 5 or complexity > 50:
            violations.append(
                {
                    "file": filepath,
                    "functions": num_functions,
                    "classes": num_classes,
                    "complexity": complexity,
                }
            )

    violations.sort(
        key=lambda x: (x["functions"] + x["classes"] * 2, x["complexity"]), reverse=True
    )
    return violations[:30]  # Top 30


def create_roi_optimized_tasks(violations):
    """Create tasks optimized for ROI and autonomous development."""
    tasks = []

    # Agent specialties
    specialty_map = {
        "shared_utilities": "Agent-1",
        "core": "Agent-1",
        "services": "Agent-2",
        "error_handling": "Agent-3",
        "infrastructure": "Agent-3",
        "manager": "Agent-5",
        "intelligent_context": "Agent-5",
        "orchestrat": "Agent-6",
        "quality": "Agent-6",
        "vision": "Agent-7",
        "gui": "Agent-7",
        "web": "Agent-7",
        "docs": "Agent-8",
        "leaderboard": "Agent-8",
        "markov": "Agent-4",  # Captain handles optimization systems!
        "autonomous": "Agent-4",
    }

    for i, v in enumerate(violations):
        file = v["file"].lower()
        filename = file.split("\\")[-1]

        # Determine specialty
        specialty = "Agent-1"
        for key, agent in specialty_map.items():
            if key in file:
                specialty = agent
                break

        # Calculate base points
        base_points = 100
        if v["functions"] > 30:
            base_points += 300
        elif v["functions"] > 20:
            base_points += 200
        elif v["functions"] > 10:
            base_points += 100

        if v["classes"] > 10:
            base_points += 300
        elif v["classes"] > 5:
            base_points += 150

        if v["complexity"] > 80:
            base_points += 200
        elif v["complexity"] > 50:
            base_points += 100

        # V2 impact
        v2_impact = 1 if (v["functions"] > 10 or v["classes"] > 5) else 0

        # Autonomy impact (critical for long-term goal!)
        autonomy_impact = 0
        if "autonomous" in file or "markov" in file:
            autonomy_impact = 3  # Very high
        elif "manager" in file or "orchestrat" in file:
            autonomy_impact = 2  # High
        elif "intelligent" in file or "optimization" in file:
            autonomy_impact = 2  # High
        elif "error_handling" in file or "quality" in file:
            autonomy_impact = 1  # Medium

        # Calculate ROI
        roi = calculate_roi(base_points, v["complexity"], v2_impact, autonomy_impact)

        # Unblocking
        unblocks = []
        if autonomy_impact > 1 or v["functions"] > 20:
            unblocks = [f"dep_{i}_1", f"dep_{i}_2"]
        elif v["functions"] > 10:
            unblocks = [f"dep_{i}_1"]

        task = Task(
            id=f"task_{i}",
            name=f"Refactor {filename}",
            points=base_points,
            specialty_required=specialty,
            complexity=min(v["complexity"], 100),
            unblocks=unblocks,
            requires_files={file},
            v2_violations_fixed=v2_impact,
            files_consolidated=max(1, v["functions"] // 10),
        )

        tasks.append(
            {"task": task, "roi": roi, "autonomy_impact": autonomy_impact, "file": filename}
        )

    # Sort by ROI (highest first)
    tasks.sort(key=lambda x: x["roi"], reverse=True)

    return tasks


def assign_tasks_to_8_agents():
    """Assign optimal tasks to all 8 agents using Markov + ROI."""

    print("\n" + "=" * 80)
    print("🧠 8-AGENT ROI-OPTIMIZED TASK ASSIGNMENT")
    print("=" * 80)
    print("\nAxiom: Maximize ROI + Advance Autonomous Development Capability\n")

    # Load violations and create tasks
    violations = load_top_violations()
    task_data = create_roi_optimized_tasks(violations)

    print(f"📊 Loaded {len(task_data)} high-ROI tasks from project scanner")
    print("\nTop 5 ROI Tasks:")
    for i, td in enumerate(task_data[:5], 1):
        print(f"  {i}. {td['file']}: ROI={td['roi']:.2f} (autonomy={td['autonomy_impact']})")

    # All 8 agents
    agents = {
        "Agent-1": "Agent-1",  # Integration & Core
        "Agent-2": "Agent-2",  # Architecture & Design
        "Agent-3": "Agent-3",  # Infrastructure & DevOps
        "Agent-4": "Agent-4",  # Captain & Strategic (autonomous systems!)
        "Agent-5": "Agent-5",  # Business Intelligence
        "Agent-6": "Agent-6",  # VSCode Forking & Quality
        "Agent-7": "Agent-7",  # Repository Cloning & Web
        "Agent-8": "Agent-8",  # SSOT & Documentation
    }

    # Create tasks list
    tasks = [td["task"] for td in task_data]

    # Initialize Markov optimizer with ROI-focused weights
    # Higher weight on strategic value (includes ROI) and dependency
    optimizer = MarkovTaskOptimizer(
        tasks,
        agents,
        weights=(0.30, 0.25, 0.35, 0.05, 0.05),  # Dependency, Agent, Strategic, Risk, Resource
    )

    # Initial state - all 8 agents available!
    state = ProjectState(
        completed_tasks=set(),
        active_agents={},
        available_agents=set(agents.keys()),
        blocked_tasks=set(),
        available_tasks={t.id for t in tasks[:20]},  # Top 20 available
        v2_compliance=0.81,
        points_earned=0,
        locked_files=set(),
    )

    # Assign tasks to all 8 agents
    assignments = []

    print("\n🎯 MARKOV + ROI TASK ASSIGNMENTS:")
    print("=" * 80)

    agent_order = [
        "Agent-4",
        "Agent-1",
        "Agent-2",
        "Agent-3",
        "Agent-5",
        "Agent-6",
        "Agent-7",
        "Agent-8",
    ]

    for agent_id in agent_order:
        if not state.available_tasks:
            print(f"\n⚠️ {agent_id}: No tasks available")
            continue

        # Filter tasks for this agent
        agent_tasks = [
            tid
            for tid in state.available_tasks
            if optimizer.tasks[tid].specialty_required == agent_id
        ]

        if not agent_tasks:
            agent_tasks = list(state.available_tasks)[:5]  # Can work on any if none match

        if agent_tasks:
            temp_state = ProjectState(
                completed_tasks=state.completed_tasks.copy(),
                active_agents=state.active_agents.copy(),
                available_agents={agent_id},
                blocked_tasks=state.blocked_tasks.copy(),
                available_tasks=set(agent_tasks),
                v2_compliance=state.v2_compliance,
                points_earned=state.points_earned,
                locked_files=state.locked_files.copy(),
            )

            best_task, scores = optimizer.select_next_task(temp_state, return_scores=True)

            if best_task:
                # Get ROI for this task
                task_roi = next((td["roi"] for td in task_data if td["task"].id == best_task.id), 0)
                autonomy = next(
                    (td["autonomy_impact"] for td in task_data if td["task"].id == best_task.id), 0
                )

                score_details = scores[best_task.id]

                print(f"\n{'🎯' if agent_id == 'Agent-4' else '🔧'} {agent_id} → {best_task.name}")
                print(f"   ROI: {task_roi:.2f} | Autonomy Impact: {autonomy}/3")
                print(f"   Points: {best_task.points} | Complexity: {best_task.complexity}")
                print(f"   Markov Score: {score_details['total']:.3f}")
                print(f"   - Dependency: {score_details['dependency']:.3f}")
                print(f"   - Agent Match: {score_details['agent_match']:.3f}")
                print(f"   - Strategic: {score_details['strategic_value']:.3f}")

                # Assign
                assignments.append(
                    {
                        "agent": agent_id,
                        "task": best_task,
                        "roi": task_roi,
                        "autonomy_impact": autonomy,
                        "score": score_details["total"],
                    }
                )

                state.active_agents[agent_id] = best_task.id
                state.available_agents.remove(agent_id)
                state.available_tasks.remove(best_task.id)
                state.locked_files.update(best_task.requires_files)

    # Summary
    print(f"\n{'='*80}")
    print("📊 ASSIGNMENT SUMMARY")
    print(f"{'='*80}")

    total_points = sum(a["task"].points for a in assignments)
    total_roi = sum(a["roi"] for a in assignments)
    avg_roi = total_roi / len(assignments) if assignments else 0
    autonomy_tasks = sum(1 for a in assignments if a["autonomy_impact"] > 0)

    print(f"\n✅ Agents Assigned: {len(assignments)}/8")
    print(f"💰 Total Points: {total_points}")
    print(f"📈 Total ROI: {total_roi:.2f}")
    print(f"📊 Average ROI: {avg_roi:.2f}")
    print(f"🤖 Autonomy-Advancing Tasks: {autonomy_tasks}/{len(assignments)}")

    print("\n🏆 TOP 3 ROI ASSIGNMENTS:")
    top_3 = sorted(assignments, key=lambda x: x["roi"], reverse=True)[:3]
    for i, a in enumerate(top_3, 1):
        print(f"   {i}. {a['agent']}: {a['task'].name} (ROI: {a['roi']:.2f})")

    print("\n🤖 AUTONOMY-FOCUSED ASSIGNMENTS:")
    auto_tasks = [a for a in assignments if a["autonomy_impact"] > 0]
    for a in auto_tasks:
        impact_str = "🔥" * a["autonomy_impact"]
        print(f"   {a['agent']}: {a['task'].name} {impact_str}")

    # Save results
    results = {
        "total_agents": len(assignments),
        "total_points": total_points,
        "total_roi": total_roi,
        "avg_roi": avg_roi,
        "autonomy_tasks": autonomy_tasks,
        "assignments": [
            {
                "agent": a["agent"],
                "task": a["task"].name,
                "points": a["task"].points,
                "roi": a["roi"],
                "autonomy_impact": a["autonomy_impact"],
                "complexity": a["task"].complexity,
            }
            for a in assignments
        ],
    }

    with open("agent_workspaces/Agent-4/8agent_roi_assignments.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n📁 Results saved to: agent_workspaces/Agent-4/8agent_roi_assignments.json")

    print(f"\n{'='*80}")
    print("🧠 8-AGENT ROI OPTIMIZATION COMPLETE!")
    print(f"{'='*80}\n")

    return assignments


if __name__ == "__main__":
    assign_tasks_to_8_agents()
