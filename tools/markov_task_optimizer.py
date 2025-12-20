"""
Markov Chain Task Optimizer - Proof of Concept
==============================================

Uses Markov Chain analysis to help the Captain select optimal next tasks
based on current project state, dependencies, agent availability, and strategic value.

Author: Agent-4 (Captain)
Date: 2025-10-12
"""

from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass
class OptimizationTask:
    """Optimization task definition for Markov optimizer (optimization domain-specific, not to be confused with domain entity Task)."""

    id: str
    name: str
    points: int
    specialty_required: str
    complexity: int  # 1-100
    unblocks: list[str]  # Task IDs this unblocks
    requires_files: set[str]
    v2_violations_fixed: int = 0
    files_consolidated: int = 0


@dataclass
class ProjectState:
    """Current state of the project."""

    completed_tasks: set[str]
    active_agents: dict[str, str]  # agent_id: task_id
    available_agents: set[str]
    blocked_tasks: set[str]
    available_tasks: set[str]
    v2_compliance: float  # 0.0 to 1.0
    points_earned: int
    locked_files: set[str]


class MarkovTaskOptimizer:
    """
    Markov Chain-based task optimizer for intelligent task selection.

    Uses weighted scoring across multiple dimensions:
    - Dependency impact (unblocking other tasks)
    - Agent availability and specialization match
    - Strategic value (points, V2 compliance, consolidation)
    - Risk assessment (complexity, success rate)
    - Resource availability (file conflicts)
    """

    def __init__(
        self,
        tasks: list[OptimizationTask],
        agents: dict[str, str],  # agent_id: specialty
        weights: tuple[float, float, float, float, float] | None = None,
    ):
        """
        Initialize Markov task optimizer.

        Args:
            tasks: List of all tasks
            agents: Dictionary of agents and their specialties
            weights: (α, β, γ, δ, ε) for dependency, agent, strategic, risk, resource
        """
        self.tasks = {task.id: task for task in tasks}
        self.agents = agents
        self.weights = weights or (0.2, 0.3, 0.3, 0.1, 0.1)  # Default weights
        self.historical_data = []

        # Validate weights sum to 1
        if abs(sum(self.weights) - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {sum(self.weights)}")

    def select_next_task(
        self, state: ProjectState, return_scores: bool = False
    ) -> tuple[OptimizationTask | None, dict[str, float]]:
        """
        Select optimal next task using Markov analysis.

        Args:
            state: Current project state
            return_scores: If True, return detailed scores for all tasks

        Returns:
            (best_task, probabilities_dict)
        """
        if not state.available_tasks:
            return None, {}

        # Calculate transition probabilities for all available tasks
        probabilities = {}
        detailed_scores = {}

        for task_id in state.available_tasks:
            task = self.tasks[task_id]
            prob, scores = self._calculate_transition_probability(task, state)
            probabilities[task_id] = prob
            detailed_scores[task_id] = scores

        # Normalize probabilities
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {t: p / total for t, p in probabilities.items()}

        # Select best task
        if probabilities:
            best_task_id = max(probabilities, key=probabilities.get)
            best_task = self.tasks[best_task_id]

            # Update historical data
            self._update_history(state, best_task)

            if return_scores:
                return best_task, detailed_scores
            else:
                return best_task, probabilities

        return None, {}

    def _calculate_transition_probability(
        self, task: OptimizationTask, state: ProjectState
    ) -> tuple[float, dict[str, float]]:
        """
        Calculate Markov transition probability for a task.

        Returns:
            (total_probability, component_scores)
        """
        α, β, γ, δ, ε = self.weights

        # Calculate component scores
        dep_score = self._dependency_score(task, state)
        agent_score = self._agent_match_score(task, state)
        strat_score = self._strategic_value(task, state)
        risk_score = 1 - self._risk_score(task, state)
        resource_score = self._resource_availability(task, state)

        # Weighted combination
        probability = (
            α * dep_score + β * agent_score + γ *
            strat_score + δ * risk_score + ε * resource_score
        )

        scores = {
            "dependency": dep_score,
            "agent_match": agent_score,
            "strategic_value": strat_score,
            "risk": risk_score,
            "resource": resource_score,
            "total": probability,
        }

        return probability, scores

    def _dependency_score(self, task: OptimizationTask, state: ProjectState) -> float:
        """Score based on how many blocked tasks this will unblock."""
        if not state.blocked_tasks:
            return 0.0

        unblocked_count = len(
            [t for t in task.unblocks if t in state.blocked_tasks])

        max_possible = len(state.blocked_tasks)
        return unblocked_count / max(max_possible, 1)

    def _agent_match_score(self, task: OptimizationTask, state: ProjectState) -> float:
        """Score based on agent availability and specialization match."""
        if not state.available_agents:
            return 0.0

        # Check if specialist is available
        for agent_id in state.available_agents:
            agent_specialty = self.agents.get(agent_id, "")

            if agent_specialty == task.specialty_required:
                return 1.0  # Perfect match

        # Check if any capable agent available
        if state.available_agents:
            return 0.6  # Capable but not specialist

        return 0.2  # Must wait

    def _strategic_value(self, task: OptimizationTask, state: ProjectState) -> float:
        """Score based on strategic value (points, V2 impact, consolidation)."""
        # Normalize each component
        MAX_POINTS = 1000
        MAX_V2_IMPACT = 5
        MAX_CONSOLIDATION = 20

        points_norm = min(task.points / MAX_POINTS, 1.0)
        v2_norm = min(task.v2_violations_fixed / MAX_V2_IMPACT, 1.0)
        consol_norm = min(task.files_consolidated / MAX_CONSOLIDATION, 1.0)

        # Weighted combination (prioritize V2 and points)
        value = 0.4 * points_norm + 0.4 * v2_norm + 0.2 * consol_norm

        return min(value, 1.0)

    def _risk_score(self, task: OptimizationTask, state: ProjectState) -> float:
        """Score based on risk (complexity and historical success)."""
        MAX_COMPLEXITY = 100

        # Complexity risk
        complexity_risk = task.complexity / MAX_COMPLEXITY

        # Historical success (simplified - would use real historical data)
        historical_success = self._get_historical_success_rate(task)
        history_risk = 1 - historical_success

        # Combined risk
        risk = 0.6 * complexity_risk + 0.4 * history_risk

        return min(risk, 1.0)

    def _resource_availability(self, task: OptimizationTask, state: ProjectState) -> float:
        """Score based on resource conflicts (file locks)."""
        if not task.requires_files:
            return 1.0

        conflicts = len(task.requires_files.intersection(state.locked_files))
        total_required = len(task.requires_files)

        return 1.0 - (conflicts / total_required)

    def _get_historical_success_rate(self, task: OptimizationTask) -> float:
        """Get historical success rate for similar tasks."""
        # Simplified - would query actual historical data
        # For now, use complexity as inverse proxy
        return max(0.5, 1.0 - (task.complexity / 200))

    def _update_history(self, state: ProjectState, task: OptimizationTask):
        """Update historical data for learning."""
        self.historical_data.append(
            {
                "state": {
                    "completed": len(state.completed_tasks),
                    "available_agents": len(state.available_agents),
                    "v2_compliance": state.v2_compliance,
                    "points": state.points_earned,
                },
                "task_chosen": task.id,
                "task_complexity": task.complexity,
                "task_points": task.points,
                "timestamp": datetime.now(),
            }
        )

    def build_transition_matrix(self) -> np.ndarray:
        """Build complete transition matrix for all tasks."""
        task_ids = list(self.tasks.keys())
        n_tasks = len(task_ids)
        matrix = np.zeros((n_tasks, n_tasks))

        for i, task_i_id in enumerate(task_ids):
            # Simulate state after completing task_i
            dummy_state = self._create_dummy_state_after(task_i_id)

            for j, task_j_id in enumerate(task_ids):
                if i != j:  # Can't transition to same task
                    task_j = self.tasks[task_j_id]
                    prob, _ = self._calculate_transition_probability(
                        task_j, dummy_state)
                    matrix[i][j] = prob

        # Normalize rows to sum to 1
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        matrix = matrix / row_sums

        return matrix

    def _create_dummy_state_after(self, task_id: str) -> ProjectState:
        """Create a dummy state for transition matrix calculation."""
        task = self.tasks[task_id]

        return ProjectState(
            completed_tasks={task_id},
            active_agents={},
            available_agents=set(self.agents.keys()),
            blocked_tasks=set(),
            available_tasks=set(self.tasks.keys()) - {task_id},
            v2_compliance=0.85,
            points_earned=task.points,
            locked_files=set(),
        )

    def find_optimal_sequence(
        self, start_state: ProjectState, max_steps: int = 10
    ) -> list[tuple[OptimizationTask, float]]:
        """
        Find optimal task sequence using Markov analysis.

        Args:
            start_state: Starting project state
            max_steps: Maximum number of tasks in sequence

        Returns:
            List of (task, probability) tuples
        """
        sequence = []
        current_state = start_state

        for _ in range(max_steps):
            if not current_state.available_tasks:
                break

            # Select next task
            task, probs = self.select_next_task(current_state)
            if not task:
                break

            sequence.append((task, probs.get(task.id, 0.0)))

            # Update state (simplified)
            current_state = self._simulate_state_after_task(
                task, current_state)

        return sequence

    def _simulate_state_after_task(self, task: OptimizationTask, state: ProjectState) -> ProjectState:
        """Simulate project state after completing a task."""
        new_state = ProjectState(
            completed_tasks=state.completed_tasks | {task.id},
            active_agents={},
            available_agents=state.available_agents.copy(),
            blocked_tasks=state.blocked_tasks - set(task.unblocks),
            available_tasks=state.available_tasks -
            {task.id} | set(task.unblocks),
            v2_compliance=min(state.v2_compliance + 0.02 *
                              task.v2_violations_fixed, 1.0),
            points_earned=state.points_earned + task.points,
            locked_files=state.locked_files - task.requires_files,
        )

        return new_state

    def explain_recommendation(self, task: OptimizationTask, state: ProjectState) -> str:
        """Generate human-readable explanation of task recommendation."""
        _, scores = self._calculate_transition_probability(task, state)

        explanation = f"**Recommendation: {task.name}**\n\n"
        explanation += f"**Overall Score: {scores['total']:.3f}**\n\n"
        explanation += "**Component Scores:**\n"
        explanation += f"- Dependency Impact: {scores['dependency']:.3f} "
        explanation += f"(unblocks {len(task.unblocks)} tasks)\n"
        explanation += f"- Agent Match: {scores['agent_match']:.3f} "
        explanation += f"(requires {task.specialty_required})\n"
        explanation += f"- Strategic Value: {scores['strategic_value']:.3f} "
        explanation += f"({task.points} pts, {task.v2_violations_fixed} V2 fixes)\n"
        explanation += f"- Risk (inverse): {scores['risk']:.3f} "
        explanation += f"(complexity {task.complexity}/100)\n"
        explanation += f"- Resource Availability: {scores['resource']:.3f} "
        explanation += f"({len(task.requires_files)} files needed)\n"

        return explanation


def demo_markov_optimizer():
    """Demonstration of Markov task optimizer."""

    # Define some sample tasks
    tasks = [
        OptimizationTask(
            id="task1",
            name="shared_utilities_split",
            points=200,
            specialty_required="Agent-1",
            complexity=30,
            unblocks=["task3", "task4"],
            requires_files={"shared_utilities.py"},
            v2_violations_fixed=1,
            files_consolidated=6,
        ),
        OptimizationTask(
            id="task2",
            name="messaging_cli_refactor",
            points=350,
            specialty_required="Agent-2",
            complexity=40,
            unblocks=["task5"],
            requires_files={"messaging_cli.py"},
            v2_violations_fixed=1,
            files_consolidated=4,
        ),
        OptimizationTask(
            id="task3",
            name="error_handling_consolidation",
            points=400,
            specialty_required="Agent-3",
            complexity=50,
            unblocks=[],
            requires_files={"coordination_error_handler.py"},
            v2_violations_fixed=2,
            files_consolidated=4,
        ),
    ]

    # Define agents
    agents = {"Agent-1": "Agent-1", "Agent-2": "Agent-2", "Agent-3": "Agent-3"}

    # Create current state
    state = ProjectState(
        completed_tasks={"messaging_core_refactor"},
        active_agents={},
        available_agents={"Agent-1", "Agent-3"},
        blocked_tasks={"task3", "task4", "task5"},
        available_tasks={"task1", "task2"},
        v2_compliance=0.85,
        points_earned=300,
        locked_files=set(),
    )

    # Initialize optimizer
    optimizer = MarkovTaskOptimizer(tasks, agents)

    # Select next task
    best_task, scores = optimizer.select_next_task(state, return_scores=True)

    if best_task:
        print("\n" + "=" * 60)
        print("MARKOV TASK OPTIMIZER - DEMONSTRATION")
        print("=" * 60)
        print(f"\n{optimizer.explain_recommendation(best_task, state)}")

        print("\n" + "-" * 60)
        print("ALL TASK SCORES:")
        print("-" * 60)
        for task_id, score_dict in scores.items():
            task = optimizer.tasks[task_id]
            print(f"\n{task.name}:")
            print(f"  Total: {score_dict['total']:.3f}")
            print(f"  Dependency: {score_dict['dependency']:.3f}")
            print(f"  Agent Match: {score_dict['agent_match']:.3f}")
            print(f"  Strategic: {score_dict['strategic_value']:.3f}")
            print(f"  Risk: {score_dict['risk']:.3f}")
            print(f"  Resource: {score_dict['resource']:.3f}")

    print("\n" + "=" * 60)
    print("🧠 Markov Chain Task Optimization Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    demo_markov_optimizer()
