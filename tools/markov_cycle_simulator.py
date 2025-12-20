"""
Markov Cycle Simulator - 4-Cycle Efficiency Demonstration
=========================================================

Uses real project scanner data and Markov optimizer to demonstrate
efficient task sequencing over multiple cycles.

Author: Agent-4 (Captain)
Date: 2025-10-12
"""

import json

from markov_task_optimizer import MarkovTaskOptimizer, ProjectState, OptimizationTask as Task


def load_real_violations_from_scanner():
    """Load actual violations from project_analysis.json"""
    with open("project_analysis.json") as f:
        data = json.load(f)

    # Find files with function/class violations
    violations = []

    for filepath, info in data.items():
        if info.get("language") != ".py":
            continue

        num_functions = len(info.get("functions", []))
        num_classes = len(info.get("classes", {}))
        complexity = info.get("complexity", 0)

        if num_functions > 10 or num_classes > 5:
            violations.append(
                {
                    "file": filepath,
                    "functions": num_functions,
                    "classes": num_classes,
                    "complexity": complexity,
                    "priority": "HIGH" if (num_functions > 30 or num_classes > 10) else "MEDIUM",
                }
            )

    # Sort by severity
    violations.sort(
        key=lambda x: (x["functions"] + x["classes"] * 2, x["complexity"]), reverse=True
    )

    return violations[:20]  # Top 20 violations


def create_tasks_from_violations(violations):
    """Convert violations into Task objects"""
    tasks = []

    # Map violations to agent specialties
    specialty_map = {
        "core": "Agent-1",
        "services": "Agent-2",
        "infrastructure": "Agent-3",
        "error_handling": "Agent-3",
        "gaming": "Agent-1",
        "utils": "Agent-1",
        "manager": "Agent-5",
        "orchestrat": "Agent-6",
        "vision": "Agent-7",
        "gui": "Agent-7",
        "web": "Agent-7",
        "docs": "Agent-8",
    }

    for i, v in enumerate(violations):
        file = v["file"]

        # Determine specialty
        specialty = "Agent-1"  # Default
        for key, agent in specialty_map.items():
            if key in file.lower():
                specialty = agent
                break

        # Calculate points based on severity
        base_points = 100
        if v["functions"] > 30:
            base_points += 200
        if v["classes"] > 10:
            base_points += 200
        if v["complexity"] > 50:
            base_points += 100

        # Determine what this unblocks
        unblocks = []
        if "shared_utilities" in file or "error_handling" in file:
            unblocks = [f"dependent_task_{i}_1", f"dependent_task_{i}_2"]
        elif "core" in file or "manager" in file:
            unblocks = [f"dependent_task_{i}_1"]

        # Files required
        requires_files = {file}

        # Create task
        filename = file.split("\\")[-1]
        task = Task(
            id=f"task_{i}",
            name=f"Refactor {filename}",
            points=base_points,
            specialty_required=specialty,
            complexity=min(v["complexity"], 100),
            unblocks=unblocks,
            requires_files=requires_files,
            v2_violations_fixed=1 if (v["functions"] > 10 or v["classes"] > 5) else 0,
            files_consolidated=max(1, v["functions"] // 10),
        )

        tasks.append(task)

    return tasks


def simulate_cycle(
    cycle_num: int, state: ProjectState, optimizer: MarkovTaskOptimizer, agents: dict[str, str]
):
    """Simulate one cycle of work"""
    print(f"\n{'='*70}")
    print(f"CYCLE {cycle_num}")
    print(f"{'='*70}")

    cycle_assignments = []
    cycle_points = 0

    # Track state at start
    print("\n📊 CYCLE START STATE:")
    print(f"  Completed Tasks: {len(state.completed_tasks)}")
    print(f"  Available Agents: {len(state.available_agents)}")
    print(f"  Available Tasks: {len(state.available_tasks)}")
    print(f"  Blocked Tasks: {len(state.blocked_tasks)}")
    print(f"  V2 Compliance: {state.v2_compliance:.1%}")
    print(f"  Points Earned: {state.points_earned}")

    # Assign tasks to available agents
    print("\n🎯 MARKOV OPTIMIZER TASK ASSIGNMENTS:")
    print("-" * 70)

    for agent_id in list(state.available_agents):
        if not state.available_tasks:
            break

        # Filter tasks this agent can do
        agent_specialty = agents[agent_id]
        agent_tasks = [
            tid
            for tid in state.available_tasks
            if optimizer.tasks[tid].specialty_required == agent_specialty
        ]

        if not agent_tasks:
            # Agent can work on any task if none match specialty
            agent_tasks = list(state.available_tasks)

        if agent_tasks:
            # Update state to show agent is working
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

            # Get Markov recommendation
            best_task, scores = optimizer.select_next_task(temp_state, return_scores=True)

            if best_task:
                # Print recommendation
                score_details = scores[best_task.id]
                print(f"\n{agent_id} → {best_task.name}")
                print(f"  Score: {score_details['total']:.3f}")
                print(
                    f"  - Dependency: {score_details['dependency']:.3f} (unblocks {len(best_task.unblocks)})"
                )
                print(f"  - Agent Match: {score_details['agent_match']:.3f}")
                print(
                    f"  - Strategic: {score_details['strategic_value']:.3f} ({best_task.points} pts)"
                )
                print(f"  - Risk: {score_details['risk']:.3f} (complexity {best_task.complexity})")
                print(f"  - Resource: {score_details['resource']:.3f}")

                # Assign task
                state.active_agents[agent_id] = best_task.id
                state.available_agents.remove(agent_id)
                state.available_tasks.remove(best_task.id)
                state.locked_files.update(best_task.requires_files)

                cycle_assignments.append((agent_id, best_task))
                cycle_points += best_task.points

    # Simulate task completion
    print("\n✅ CYCLE COMPLETION:")
    print("-" * 70)

    for agent_id, task in cycle_assignments:
        # Mark task complete
        state.completed_tasks.add(task.id)
        state.active_agents.pop(agent_id, None)
        state.available_agents.add(agent_id)
        state.locked_files -= task.requires_files

        # Unblock dependent tasks
        for unblocked_id in task.unblocks:
            if unblocked_id in state.blocked_tasks:
                state.blocked_tasks.remove(unblocked_id)
                # Only add to available if it's a real task
                if unblocked_id in optimizer.tasks:
                    state.available_tasks.add(unblocked_id)

        # Update metrics
        state.points_earned += task.points
        if task.v2_violations_fixed > 0:
            state.v2_compliance = min(state.v2_compliance + 0.02, 1.0)

        print(f"  ✓ {agent_id} completed {task.name} (+{task.points} pts)")

    # Cycle summary
    print(f"\n📈 CYCLE {cycle_num} SUMMARY:")
    print(f"  Tasks Completed: {len(cycle_assignments)}")
    print(f"  Points Earned: {cycle_points}")
    print(f"  Tasks Unblocked: {sum(len(t.unblocks) for _, t in cycle_assignments)}")
    print(f"  New V2 Compliance: {state.v2_compliance:.1%}")
    print(f"  Total Points: {state.points_earned}")

    return state, cycle_points, len(cycle_assignments)


def run_4_cycle_simulation():
    """Run 4-cycle Markov optimization demonstration"""

    print("\n" + "=" * 70)
    print("🧠 MARKOV OPTIMIZER - 4 CYCLE EFFICIENCY DEMONSTRATION")
    print("=" * 70)
    print("\nLoading real violations from project scanner...")

    # Load real data
    violations = load_real_violations_from_scanner()
    print(f"  Found {len(violations)} violations to fix")

    # Create tasks
    tasks = create_tasks_from_violations(violations)
    print(f"  Created {len(tasks)} tasks")

    # Define agents
    agents = {
        "Agent-1": "Agent-1",
        "Agent-2": "Agent-2",
        "Agent-3": "Agent-3",
    }

    # Initialize optimizer with strategic weights
    # Prioritize: dependency (0.25), agent match (0.30), strategic (0.30)
    optimizer = MarkovTaskOptimizer(
        tasks,
        agents,
        weights=(0.25, 0.30, 0.30, 0.10, 0.05),  # More weight on dependency and strategic
    )

    # Initial state
    state = ProjectState(
        completed_tasks=set(),
        active_agents={},
        available_agents={"Agent-1", "Agent-2", "Agent-3"},
        blocked_tasks={f"dependent_task_{i}_{j}" for i in range(len(tasks)) for j in [1, 2]},
        available_tasks={t.id for t in tasks[:10]},  # Start with 10 tasks available
        v2_compliance=0.81,  # Current from scanner
        points_earned=0,
        locked_files=set(),
    )

    # Track metrics
    total_points = 0
    total_tasks = 0

    # Run 4 cycles
    for cycle in range(1, 5):
        state, points, tasks_done = simulate_cycle(cycle, state, optimizer, agents)
        total_points += points
        total_tasks += tasks_done

    # Final summary
    print(f"\n{'='*70}")
    print("🏆 4-CYCLE SIMULATION COMPLETE")
    print(f"{'='*70}")
    print("\n📊 OVERALL RESULTS:")
    print(f"  Total Tasks Completed: {total_tasks}")
    print(f"  Total Points Earned: {total_points}")
    print(f"  Average Points/Cycle: {total_points/4:.0f}")
    print(f"  Average Tasks/Cycle: {total_tasks/4:.1f}")
    print(f"  Final V2 Compliance: {state.v2_compliance:.1%} (started at 81.0%)")
    print(f"  Tasks Remaining: {len(state.available_tasks)}")
    print(
        f"  Tasks Unblocked: {len([t for t in state.blocked_tasks if t.startswith('dependent')])}"
    )

    # Efficiency analysis
    print("\n💡 EFFICIENCY ANALYSIS:")

    # Calculate theoretical maximum (if all agents work on highest point tasks)
    all_points = sorted([t.points for t in tasks], reverse=True)
    theoretical_max = sum(all_points[:total_tasks])
    efficiency = (total_points / theoretical_max * 100) if theoretical_max > 0 else 0

    print(f"  Theoretical Maximum: {theoretical_max} pts (if perfect selection)")
    print(f"  Actual Achievement: {total_points} pts")
    print(f"  Optimizer Efficiency: {efficiency:.1f}%")

    if efficiency > 90:
        print("  🏆 EXCELLENT! Near-optimal task selection!")
    elif efficiency > 80:
        print("  ✅ VERY GOOD! Efficient task selection!")
    elif efficiency > 70:
        print("  👍 GOOD! Decent task selection!")
    else:
        print("  ⚠️ Room for improvement in task selection")

    # Coordination efficiency
    agent_utilization = (total_tasks / (4 * len(agents))) * 100
    print("\n🤝 COORDINATION EFFICIENCY:")
    print(
        f"  Agent Utilization: {agent_utilization:.1f}% ({total_tasks}/{4 * len(agents)} agent-cycles)"
    )
    print(f"  Idle Agent-Cycles: {4 * len(agents) - total_tasks}")

    # V2 Compliance progress
    v2_improvement = (state.v2_compliance - 0.81) * 100
    print("\n📈 V2 COMPLIANCE PROGRESS:")
    print("  Starting: 81.0%")
    print(f"  Ending: {state.v2_compliance:.1%}")
    print(f"  Improvement: +{v2_improvement:.1f} percentage points")

    print(f"\n{'='*70}")
    print("🧠 MARKOV OPTIMIZER DEMONSTRATION COMPLETE!")
    print(f"{'='*70}\n")

    # Save results
    results = {
        "cycles": 4,
        "total_tasks": total_tasks,
        "total_points": total_points,
        "avg_points_per_cycle": total_points / 4,
        "avg_tasks_per_cycle": total_tasks / 4,
        "v2_improvement": v2_improvement,
        "optimizer_efficiency": efficiency,
        "agent_utilization": agent_utilization,
        "final_v2_compliance": state.v2_compliance,
    }

    with open("agent_workspaces/Agent-4/markov_4cycle_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("📁 Results saved to: agent_workspaces/Agent-4/markov_4cycle_results.json\n")

    return results


if __name__ == "__main__":
    run_4_cycle_simulation()
