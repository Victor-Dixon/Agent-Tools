#!/usr/bin/env python3
"""
Performance Profiler Server - MCP server to identify performance bottlenecks.

Tools:
- profile_startup: Measure application startup time
- find_slow_tests: Identify slow test cases
- analyze_bundle: Bundle size analysis
- memory_snapshot: Memory usage report
- benchmark_function: Run micro-benchmarks
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def profile_startup(
    project_path: str = ".",
    command: str | None = None,
    runs: int = 3,
    warmup: int = 1
) -> dict[str, Any]:
    """Measure application startup time."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect startup command
    if command is None:
        if (project_path / "package.json").exists():
            pkg = json.loads((project_path / "package.json").read_text())
            scripts = pkg.get("scripts", {})
            
            # Try to find a start script that exits quickly
            if "start" in scripts:
                command = "npm run start"
            elif "dev" in scripts:
                # For dev servers, we'll measure time to first output
                command = "npm run dev"
        elif (project_path / "main.py").exists():
            command = "python main.py --help"
        elif (project_path / "app.py").exists():
            command = "python app.py --help"
        elif (project_path / "Cargo.toml").exists():
            command = "cargo run --release -- --help"
        elif (project_path / "go.mod").exists():
            command = "go run . --help"
    
    if not command:
        return {"success": False, "error": "Could not detect startup command. Provide command parameter."}
    
    # Warmup runs
    for _ in range(warmup):
        subprocess.run(
            command,
            shell=True,
            cwd=project_path,
            capture_output=True,
            timeout=30
        )
    
    # Timed runs
    times = []
    for i in range(runs):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                timeout=60
            )
            end = time.perf_counter()
            elapsed = (end - start) * 1000  # Convert to ms
            times.append({
                "run": i + 1,
                "time_ms": round(elapsed, 2),
                "exit_code": result.returncode
            })
        except subprocess.TimeoutExpired:
            times.append({
                "run": i + 1,
                "time_ms": None,
                "error": "Timeout"
            })
    
    # Calculate statistics
    valid_times = [t["time_ms"] for t in times if t["time_ms"] is not None]
    
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        min_time = min(valid_times)
        max_time = max(valid_times)
    else:
        avg_time = min_time = max_time = None
    
    return {
        "success": True,
        "command": command,
        "runs": times,
        "statistics": {
            "average_ms": round(avg_time, 2) if avg_time else None,
            "min_ms": round(min_time, 2) if min_time else None,
            "max_ms": round(max_time, 2) if max_time else None,
            "successful_runs": len(valid_times),
            "total_runs": runs
        },
        "warmup_runs": warmup
    }


def find_slow_tests(
    project_path: str = ".",
    test_framework: str = "auto",
    threshold_ms: int = 1000,
    max_results: int = 20
) -> dict[str, Any]:
    """Identify slow test cases."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect test framework
    if test_framework == "auto":
        if (project_path / "package.json").exists():
            pkg = json.loads((project_path / "package.json").read_text())
            if "jest" in str(pkg):
                test_framework = "jest"
            elif "vitest" in str(pkg):
                test_framework = "vitest"
            elif "mocha" in str(pkg):
                test_framework = "mocha"
        elif (project_path / "pytest.ini").exists() or \
             (project_path / "pyproject.toml").exists() or \
             (project_path / "conftest.py").exists():
            test_framework = "pytest"
        elif (project_path / "Cargo.toml").exists():
            test_framework = "cargo"
        elif (project_path / "go.mod").exists():
            test_framework = "go"
    
    if test_framework == "auto":
        return {"success": False, "error": "Could not detect test framework"}
    
    slow_tests = []
    
    if test_framework == "jest":
        try:
            result = subprocess.run(
                ["npx", "jest", "--json", "--testTimeout=60000"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            try:
                jest_output = json.loads(result.stdout)
                for test_result in jest_output.get("testResults", []):
                    for assertion in test_result.get("assertionResults", []):
                        duration = assertion.get("duration", 0)
                        if duration >= threshold_ms:
                            slow_tests.append({
                                "file": test_result.get("name", "").replace(str(project_path) + "/", ""),
                                "test": assertion.get("fullName", assertion.get("title", "")),
                                "duration_ms": duration,
                                "status": assertion.get("status")
                            })
            except json.JSONDecodeError:
                pass
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}
    
    elif test_framework == "vitest":
        try:
            result = subprocess.run(
                ["npx", "vitest", "run", "--reporter=json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            try:
                vitest_output = json.loads(result.stdout)
                for file_result in vitest_output.get("testResults", []):
                    for test in file_result.get("assertionResults", []):
                        duration = test.get("duration", 0)
                        if duration >= threshold_ms:
                            slow_tests.append({
                                "file": file_result.get("name", "").replace(str(project_path) + "/", ""),
                                "test": test.get("fullName", ""),
                                "duration_ms": duration
                            })
            except json.JSONDecodeError:
                pass
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}
    
    elif test_framework == "pytest":
        try:
            result = subprocess.run(
                ["pytest", "--durations=0", "-q", "--tb=no"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse pytest durations output
            duration_pattern = r'(\d+\.?\d*)s (call|setup|teardown)\s+(.+)'
            for line in result.stdout.split('\n'):
                match = re.search(duration_pattern, line)
                if match:
                    duration_s = float(match.group(1))
                    duration_ms = duration_s * 1000
                    if duration_ms >= threshold_ms:
                        slow_tests.append({
                            "test": match.group(3).strip(),
                            "phase": match.group(2),
                            "duration_ms": round(duration_ms, 2)
                        })
                        
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}
    
    elif test_framework == "cargo":
        try:
            result = subprocess.run(
                ["cargo", "test", "--", "-Z", "unstable-options", "--report-time"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse cargo test output
            time_pattern = r'test (.+) \.\.\. ok <(\d+\.?\d*)s>'
            for line in result.stdout.split('\n'):
                match = re.search(time_pattern, line)
                if match:
                    duration_s = float(match.group(2))
                    duration_ms = duration_s * 1000
                    if duration_ms >= threshold_ms:
                        slow_tests.append({
                            "test": match.group(1),
                            "duration_ms": round(duration_ms, 2)
                        })
                        
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}
    
    elif test_framework == "go":
        try:
            result = subprocess.run(
                ["go", "test", "-v", "-json", "./..."],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            test_times = {}
            for line in result.stdout.split('\n'):
                if line.strip():
                    try:
                        event = json.loads(line)
                        if event.get("Action") == "pass" and event.get("Test"):
                            elapsed = event.get("Elapsed", 0) * 1000  # Convert to ms
                            if elapsed >= threshold_ms:
                                slow_tests.append({
                                    "package": event.get("Package", ""),
                                    "test": event.get("Test", ""),
                                    "duration_ms": round(elapsed, 2)
                                })
                    except json.JSONDecodeError:
                        continue
                        
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"success": False, "error": str(e)}
    
    # Sort by duration and limit results
    slow_tests.sort(key=lambda x: x.get("duration_ms", 0), reverse=True)
    slow_tests = slow_tests[:max_results]
    
    return {
        "success": True,
        "test_framework": test_framework,
        "threshold_ms": threshold_ms,
        "slow_tests": slow_tests,
        "total_slow_tests": len(slow_tests)
    }


def analyze_bundle(
    project_path: str = ".",
    bundler: str = "auto"
) -> dict[str, Any]:
    """Analyze bundle size for JavaScript/TypeScript projects."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Check for package.json
    if not (project_path / "package.json").exists():
        return {"success": False, "error": "Not a JavaScript/TypeScript project (no package.json)"}
    
    pkg = json.loads((project_path / "package.json").read_text())
    
    # Auto-detect bundler
    if bundler == "auto":
        all_deps = str(pkg.get("dependencies", {})) + str(pkg.get("devDependencies", {}))
        
        if "next" in all_deps:
            bundler = "next"
        elif "vite" in all_deps:
            bundler = "vite"
        elif "webpack" in all_deps:
            bundler = "webpack"
        elif "esbuild" in all_deps:
            bundler = "esbuild"
        elif "rollup" in all_deps:
            bundler = "rollup"
    
    bundle_info = {
        "success": True,
        "bundler": bundler
    }
    
    # Try source-map-explorer or bundle-analyzer
    try:
        # First, try to get package sizes
        result = subprocess.run(
            ["npx", "size-limit", "--json"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            try:
                size_data = json.loads(result.stdout)
                bundle_info["size_limit"] = size_data
            except json.JSONDecodeError:
                pass
    except FileNotFoundError:
        pass
    
    # Check built files
    dist_dirs = [
        project_path / "dist",
        project_path / ".next",
        project_path / "build",
        project_path / "out"
    ]
    
    for dist_dir in dist_dirs:
        if dist_dir.exists():
            files = []
            total_size = 0
            
            for f in dist_dir.rglob("*"):
                if f.is_file():
                    size = f.stat().st_size
                    total_size += size
                    
                    # Only include JS/CSS files in details
                    if f.suffix in ['.js', '.css', '.mjs']:
                        files.append({
                            "file": str(f.relative_to(dist_dir)),
                            "size_bytes": size,
                            "size_human": f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / 1024 / 1024:.2f} MB"
                        })
            
            # Sort by size
            files.sort(key=lambda x: x["size_bytes"], reverse=True)
            
            bundle_info["dist_directory"] = str(dist_dir)
            bundle_info["total_size_bytes"] = total_size
            bundle_info["total_size_human"] = f"{total_size / 1024 / 1024:.2f} MB"
            bundle_info["largest_files"] = files[:20]
            bundle_info["total_files"] = len(files)
            break
    
    # Try to run webpack-bundle-analyzer or similar
    if bundler == "next":
        bundle_info["analyze_command"] = "ANALYZE=true npm run build"
        bundle_info["hint"] = "Install @next/bundle-analyzer and set ANALYZE=true"
    elif bundler == "vite":
        bundle_info["analyze_command"] = "npx vite-bundle-visualizer"
    elif bundler == "webpack":
        bundle_info["analyze_command"] = "npx webpack-bundle-analyzer stats.json"
    
    return bundle_info


def memory_snapshot(
    project_path: str = ".",
    command: str | None = None,
    duration_seconds: int = 5
) -> dict[str, Any]:
    """Get memory usage report for an application."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect command
    if command is None:
        if (project_path / "package.json").exists():
            pkg = json.loads((project_path / "package.json").read_text())
            scripts = pkg.get("scripts", {})
            if "start" in scripts:
                command = "node -e 'require(\"./node_modules/.bin/\" + process.argv[1])' start"
        elif (project_path / "main.py").exists():
            command = "python main.py"
    
    if not command:
        # Use system memory snapshot instead
        try:
            import resource
            
            # Get current process memory
            rusage = resource.getrusage(resource.RUSAGE_SELF)
            
            return {
                "success": True,
                "type": "process_memory",
                "memory": {
                    "max_rss_bytes": rusage.ru_maxrss * 1024,  # Convert to bytes
                    "max_rss_human": f"{rusage.ru_maxrss / 1024:.2f} MB",
                    "shared_memory_size": rusage.ru_ixrss,
                    "unshared_data_size": rusage.ru_idrss,
                    "unshared_stack_size": rusage.ru_isrss,
                    "page_faults": rusage.ru_minflt + rusage.ru_majflt
                }
            }
        except ImportError:
            return {"success": False, "error": "Could not detect command and resource module not available"}
    
    # Run command and measure memory
    try:
        # Use /usr/bin/time for memory measurement on Linux
        if sys.platform == "linux":
            timed_command = f"/usr/bin/time -v {command}"
            result = subprocess.run(
                timed_command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=duration_seconds + 30
            )
            
            # Parse time output
            memory_info = {}
            for line in result.stderr.split('\n'):
                if "Maximum resident set size" in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        rss_kb = int(match.group(1))
                        memory_info["max_rss_kb"] = rss_kb
                        memory_info["max_rss_human"] = f"{rss_kb / 1024:.2f} MB"
                elif "Minor (reclaiming a frame) page faults" in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        memory_info["minor_page_faults"] = int(match.group(1))
                elif "Major (requiring I/O) page faults" in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        memory_info["major_page_faults"] = int(match.group(1))
            
            return {
                "success": True,
                "type": "timed_execution",
                "command": command,
                "memory": memory_info,
                "exit_code": result.returncode
            }
        else:
            # For other platforms, just run and report basic info
            result = subprocess.run(
                command,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=duration_seconds + 30
            )
            
            return {
                "success": True,
                "type": "basic_execution",
                "command": command,
                "exit_code": result.returncode,
                "hint": "For detailed memory profiling on macOS, use Instruments or heaptrack"
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {duration_seconds + 30} seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def benchmark_function(
    project_path: str = ".",
    language: str = "auto",
    function_name: str | None = None,
    iterations: int = 1000
) -> dict[str, Any]:
    """Run micro-benchmarks for functions."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    # Auto-detect language
    if language == "auto":
        if (project_path / "package.json").exists():
            language = "javascript"
        elif (project_path / "pyproject.toml").exists() or list(project_path.glob("*.py")):
            language = "python"
        elif (project_path / "Cargo.toml").exists():
            language = "rust"
        elif (project_path / "go.mod").exists():
            language = "go"
    
    if language == "javascript" or language == "typescript":
        # Check for existing benchmarks
        bench_files = list(project_path.glob("**/*.bench.js")) + \
                     list(project_path.glob("**/*.bench.ts")) + \
                     list(project_path.glob("**/benchmark*.js"))
        
        if bench_files:
            try:
                # Try running with vitest bench or similar
                result = subprocess.run(
                    ["npx", "vitest", "bench", "--run"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                return {
                    "success": result.returncode == 0,
                    "language": language,
                    "tool": "vitest",
                    "benchmark_files": [str(f.relative_to(project_path)) for f in bench_files],
                    "output": result.stdout[-3000:] if result.stdout else result.stderr[-3000:],
                    "exit_code": result.returncode
                }
            except FileNotFoundError:
                pass
        
        return {
            "success": True,
            "language": language,
            "message": "No benchmark files found",
            "hint": "Create *.bench.ts files and use vitest bench, or install benny/benchmark.js",
            "example": """
// benchmark.bench.ts
import { bench, describe } from 'vitest'

describe('myFunction', () => {
  bench('baseline', () => {
    myFunction()
  })
})
"""
        }
    
    elif language == "python":
        if function_name:
            # Run a simple timeit benchmark
            timeit_code = f"""
import timeit
import sys
sys.path.insert(0, '.')

# Try to import the function
try:
    from {function_name.rsplit('.', 1)[0]} import {function_name.rsplit('.', 1)[-1]}
    
    result = timeit.timeit('{function_name.rsplit(".", 1)[-1]}()', 
                          globals=globals(), 
                          number={iterations})
    print(f'{{"success": true, "total_time": {{result}}, "iterations": {iterations}, "per_iteration_ns": {{result/{iterations}*1e9}}}}')
except Exception as e:
    print(f'{{"success": false, "error": "{{str(e)}}"}}'')
"""
            try:
                result = subprocess.run(
                    ["python", "-c", timeit_code],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.stdout:
                    try:
                        return json.loads(result.stdout)
                    except:
                        pass
                
                return {
                    "success": False,
                    "error": result.stderr or "Failed to run benchmark"
                }
                
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Benchmark timed out"}
        
        # Check for pytest-benchmark
        try:
            result = subprocess.run(
                ["pytest", "--benchmark-only", "--benchmark-json=benchmark.json"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            bench_file = project_path / "benchmark.json"
            if bench_file.exists():
                bench_data = json.loads(bench_file.read_text())
                bench_file.unlink()  # Clean up
                
                return {
                    "success": True,
                    "language": language,
                    "tool": "pytest-benchmark",
                    "benchmarks": bench_data.get("benchmarks", [])[:20]
                }
                
        except FileNotFoundError:
            pass
        
        return {
            "success": True,
            "language": language,
            "message": "Provide function_name parameter or install pytest-benchmark",
            "hint": "pip install pytest-benchmark"
        }
    
    elif language == "rust":
        try:
            result = subprocess.run(
                ["cargo", "bench"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "language": language,
                "tool": "cargo bench",
                "output": result.stdout[-3000:] if result.stdout else result.stderr[-3000:],
                "exit_code": result.returncode
            }
            
        except FileNotFoundError:
            return {"success": False, "error": "cargo not found"}
    
    elif language == "go":
        try:
            result = subprocess.run(
                ["go", "test", "-bench=.", "-benchmem"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse Go benchmark output
            benchmarks = []
            for line in result.stdout.split('\n'):
                match = re.match(r'Benchmark(\w+)-\d+\s+(\d+)\s+([\d.]+)\s+ns/op', line)
                if match:
                    benchmarks.append({
                        "name": match.group(1),
                        "iterations": int(match.group(2)),
                        "ns_per_op": float(match.group(3))
                    })
            
            return {
                "success": result.returncode == 0,
                "language": language,
                "tool": "go test -bench",
                "benchmarks": benchmarks,
                "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
            
        except FileNotFoundError:
            return {"success": False, "error": "go not found"}
    
    return {"success": False, "error": f"Benchmarking not supported for: {language}"}


# MCP Server Implementation
TOOLS = [
    {
        "name": "profile_startup",
        "description": "Measure application startup time",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "command": {
                    "type": "string",
                    "description": "Command to profile (auto-detected if not provided)"
                },
                "runs": {
                    "type": "integer",
                    "description": "Number of runs to average",
                    "default": 3
                },
                "warmup": {
                    "type": "integer",
                    "description": "Number of warmup runs",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "find_slow_tests",
        "description": "Identify slow test cases",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "test_framework": {
                    "type": "string",
                    "description": "Test framework (auto, jest, vitest, pytest, cargo, go)",
                    "default": "auto"
                },
                "threshold_ms": {
                    "type": "integer",
                    "description": "Minimum duration in ms to consider a test slow",
                    "default": 1000
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 20
                }
            }
        }
    },
    {
        "name": "analyze_bundle",
        "description": "Analyze JavaScript/TypeScript bundle size",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "bundler": {
                    "type": "string",
                    "description": "Bundler (auto, next, vite, webpack, esbuild, rollup)",
                    "default": "auto"
                }
            }
        }
    },
    {
        "name": "memory_snapshot",
        "description": "Get memory usage report for an application",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "command": {
                    "type": "string",
                    "description": "Command to profile (auto-detected if not provided)"
                },
                "duration_seconds": {
                    "type": "integer",
                    "description": "Duration to run the command",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "benchmark_function",
        "description": "Run micro-benchmarks for functions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "language": {
                    "type": "string",
                    "description": "Project language (auto, javascript, typescript, python, rust, go)",
                    "default": "auto"
                },
                "function_name": {
                    "type": "string",
                    "description": "Fully qualified function name to benchmark (for Python)"
                },
                "iterations": {
                    "type": "integer",
                    "description": "Number of iterations for the benchmark",
                    "default": 1000
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "profile_startup":
        return profile_startup(**arguments)
    elif name == "find_slow_tests":
        return find_slow_tests(**arguments)
    elif name == "analyze_bundle":
        return analyze_bundle(**arguments)
    elif name == "memory_snapshot":
        return memory_snapshot(**arguments)
    elif name == "benchmark_function":
        return benchmark_function(**arguments)
    else:
        return {"error": f"Unknown tool: {name}"}


def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {
                            "name": "performance-profiler-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})
                result = handle_tool_call(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            elif method == "notifications/initialized":
                continue
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
