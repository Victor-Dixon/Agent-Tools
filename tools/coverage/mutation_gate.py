#!/usr/bin/env python3
"""
Mutation testing gate to ensure test quality.
Usage:
  python tools/coverage/mutation_gate.py --min 60 --defer-on-failure
"""

import argparse
import subprocess
import sys


class MutationGate:
    """Gate for mutation testing results."""

    def __init__(self, min_score: float = 60.0):
        """Initialize mutation gate with minimum score threshold."""
        self.min_score = min_score
        self.results_file = "mutmut_results.json"

    def run_mutation_tests(self) -> bool:
        """Run mutation tests using mutmut."""
        try:
            print("🧬 Running mutation tests...")
            cmd = [
                "mutmut",
                "run",
                "--paths-to-mutate",
                "src",
                "--tests-dir",
                "tests",
                "--backup",
                "--runner",
                "python -m pytest -q",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print("⚠️  Mutation tests completed with warnings")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
            else:
                print("✅ Mutation tests completed successfully")

            return True

        except FileNotFoundError:
            print("❌ mutmut not found. Install with: pip install mutmut")
            return False
        except subprocess.CalledProcessError as e:
            print(f"❌ Mutation tests failed: {e}")
            return False

    def get_mutation_results(self) -> dict:
        """Get mutation testing results."""
        try:
            # Try to get results from mutmut
            result = subprocess.run(["mutmut", "results"], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"⚠️  Could not get mutation results: {result.stderr}")
                return {"killed": 0, "survived": 0, "timeout": 0}

            # Parse mutmut output
            lines = result.stdout.strip().split("\n")
            results = {"killed": 0, "survived": 0, "timeout": 0}

            for line in lines:
                if "killed" in line.lower():
                    try:
                        results["killed"] = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "survived" in line.lower():
                    try:
                        results["survived"] = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass
                elif "timeout" in line.lower():
                    try:
                        results["timeout"] = int(line.split()[0])
                    except (ValueError, IndexError):
                        pass

            return results

        except Exception as e:
            print(f"❌ Error getting mutation results: {e}")
            return {"killed": 0, "survived": 0, "timeout": 0}

    def calculate_mutation_score(self, results: dict) -> float:
        """Calculate mutation score percentage."""
        total = results["killed"] + results["survived"] + results["timeout"]
        if total == 0:
            return 0.0

        killed = results["killed"]
        return 100.0 * killed / total

    def check_threshold(self, score: float, defer_on_failure: bool = False) -> bool:
        """Check if mutation score meets threshold."""
        if score >= self.min_score:
            print(f"✅ Mutation score {score:.1f}% meets threshold {self.min_score}%")
            return True
        else:
            if defer_on_failure:
                print(f"⚠️  Mutation score {score:.1f}% below threshold {self.min_score}%")
                print("📝 Deferring with follow-up ticket (use --defer-on-failure)")
                return True
            else:
                print(f"❌ Mutation score {score:.1f}% below threshold {self.min_score}%")
                return False

    def print_detailed_report(self, results: dict, score: float) -> None:
        """Print detailed mutation testing report."""
        total = results["killed"] + results["survived"] + results["timeout"]

        print("\n📊 Mutation Testing Report")
        print("=" * 50)
        print(f"Total mutations:     {total}")
        print(f"Killed:              {results['killed']}")
        print(f"Survived:            {results['survived']}")
        print(f"Timeout:             {results['timeout']}")
        print(f"Mutation score:      {score:.1f}%")
        print(f"Threshold:           {self.min_score}%")
        print(f"Status:              {'✅ PASS' if score >= self.min_score else '❌ FAIL'}")

        if results["survived"] > 0:
            print(f"\n⚠️  {results['survived']} mutations survived - consider adding more tests")

        if results["timeout"] > 0:
            print(f"⏱️  {results['timeout']} mutations timed out - may indicate slow tests")


def main() -> int:
    """Main function for mutation testing gate."""
    ap = argparse.ArgumentParser(description="Mutation testing gate")
    ap.add_argument("--min", type=float, default=60.0, help="Minimum mutation score")
    ap.add_argument(
        "--defer-on-failure", action="store_true", help="Defer failure with follow-up ticket"
    )
    ap.add_argument("--run", action="store_true", help="Run mutation tests first")
    args = ap.parse_args()

    gate = MutationGate(args.min)

    # Run mutation tests if requested
    if args.run:
        if not gate.run_mutation_tests():
            return 1

    # Get results
    results = gate.get_mutation_results()
    score = gate.calculate_mutation_score(results)

    # Print report
    gate.print_detailed_report(results, score)

    # Check threshold
    if gate.check_threshold(score, args.defer_on_failure):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
