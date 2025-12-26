#!/usr/bin/env python3
"""
Environment Setup Server - MCP server for bootstrapping development environments.

Tools:
- install_dependencies: Install project dependencies (npm/pip/poetry/cargo)
- setup_env_file: Create .env file from template
- validate_environment: Check all required tools are installed
- setup_database: Run migrations and seed data
- health_check: Verify all services are running
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def install_dependencies(
    project_path: str = ".",
    package_manager: str = "auto",
    dev: bool = True,
    frozen: bool = False
) -> dict[str, Any]:
    """Install project dependencies using the appropriate package manager."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Project path does not exist: {project_path}"}
    
    # Auto-detect package manager
    if package_manager == "auto":
        if (project_path / "package-lock.json").exists():
            package_manager = "npm"
        elif (project_path / "yarn.lock").exists():
            package_manager = "yarn"
        elif (project_path / "pnpm-lock.yaml").exists():
            package_manager = "pnpm"
        elif (project_path / "poetry.lock").exists():
            package_manager = "poetry"
        elif (project_path / "Pipfile.lock").exists():
            package_manager = "pipenv"
        elif (project_path / "requirements.txt").exists():
            package_manager = "pip"
        elif (project_path / "Cargo.lock").exists():
            package_manager = "cargo"
        elif (project_path / "go.mod").exists():
            package_manager = "go"
        else:
            return {"success": False, "error": "Could not auto-detect package manager"}
    
    # Build command based on package manager
    commands = {
        "npm": ["npm", "ci" if frozen else "install"],
        "yarn": ["yarn", "install", "--frozen-lockfile"] if frozen else ["yarn", "install"],
        "pnpm": ["pnpm", "install", "--frozen-lockfile"] if frozen else ["pnpm", "install"],
        "pip": ["pip", "install", "-r", "requirements.txt"],
        "poetry": ["poetry", "install", "--no-interaction"],
        "pipenv": ["pipenv", "install", "--dev" if dev else ""],
        "cargo": ["cargo", "build"],
        "go": ["go", "mod", "download"],
    }
    
    if package_manager not in commands:
        return {"success": False, "error": f"Unknown package manager: {package_manager}"}
    
    cmd = commands[package_manager]
    # Remove empty strings from command
    cmd = [c for c in cmd if c]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for large installs
        )
        
        return {
            "success": result.returncode == 0,
            "package_manager": package_manager,
            "command": " ".join(cmd),
            "stdout": result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout,
            "stderr": result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Installation timed out after 10 minutes"}
    except FileNotFoundError:
        return {"success": False, "error": f"Package manager '{package_manager}' not found"}


def setup_env_file(
    project_path: str = ".",
    template: str = ".env.example",
    output: str = ".env",
    overwrite: bool = False,
    variables: dict[str, str] | None = None
) -> dict[str, Any]:
    """Create .env file from template, optionally setting variables."""
    project_path = Path(project_path).resolve()
    template_path = project_path / template
    output_path = project_path / output
    
    # Check if output already exists
    if output_path.exists() and not overwrite:
        return {
            "success": False,
            "error": f"{output} already exists. Use overwrite=true to replace it."
        }
    
    # Try to find template
    template_candidates = [
        template_path,
        project_path / ".env.template",
        project_path / ".env.sample",
        project_path / "env.example",
    ]
    
    found_template = None
    for candidate in template_candidates:
        if candidate.exists():
            found_template = candidate
            break
    
    if found_template:
        # Read template
        content = found_template.read_text()
        
        # Replace variables if provided
        if variables:
            for key, value in variables.items():
                # Replace KEY=value or KEY= patterns
                import re
                pattern = rf'^{re.escape(key)}=.*$'
                replacement = f'{key}={value}'
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                # If key wasn't found, append it
                if f'{key}=' not in content:
                    content += f'\n{key}={value}'
        
        output_path.write_text(content)
        
        return {
            "success": True,
            "created": str(output_path),
            "from_template": str(found_template),
            "variables_set": list(variables.keys()) if variables else []
        }
    else:
        # No template found, create minimal .env if variables provided
        if variables:
            content = '\n'.join(f'{k}={v}' for k, v in variables.items())
            output_path.write_text(content + '\n')
            return {
                "success": True,
                "created": str(output_path),
                "from_template": None,
                "variables_set": list(variables.keys())
            }
        else:
            return {
                "success": False,
                "error": "No template found and no variables provided",
                "searched": [str(c) for c in template_candidates]
            }


def validate_environment(
    project_path: str = ".",
    tools: list[str] | None = None
) -> dict[str, Any]:
    """Check that all required development tools are installed."""
    project_path = Path(project_path).resolve()
    
    # Default tools to check based on project type
    if tools is None:
        tools = []
        
        # Detect required tools based on project files
        if (project_path / "package.json").exists():
            tools.extend(["node", "npm"])
        if (project_path / "yarn.lock").exists():
            tools.append("yarn")
        if (project_path / "pnpm-lock.yaml").exists():
            tools.append("pnpm")
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            tools.extend(["python3", "pip"])
        if (project_path / "poetry.lock").exists():
            tools.append("poetry")
        if (project_path / "Cargo.toml").exists():
            tools.extend(["rustc", "cargo"])
        if (project_path / "go.mod").exists():
            tools.append("go")
        if (project_path / "docker-compose.yml").exists() or (project_path / "docker-compose.yaml").exists():
            tools.extend(["docker", "docker-compose"])
        if (project_path / ".git").exists():
            tools.append("git")
        
        # Remove duplicates while preserving order
        tools = list(dict.fromkeys(tools))
    
    results = {}
    all_available = True
    
    for tool in tools:
        # Check if tool is available
        path = shutil.which(tool)
        if path:
            # Get version
            version_cmd = {
                "node": ["node", "--version"],
                "npm": ["npm", "--version"],
                "yarn": ["yarn", "--version"],
                "pnpm": ["pnpm", "--version"],
                "python3": ["python3", "--version"],
                "python": ["python", "--version"],
                "pip": ["pip", "--version"],
                "poetry": ["poetry", "--version"],
                "rustc": ["rustc", "--version"],
                "cargo": ["cargo", "--version"],
                "go": ["go", "version"],
                "docker": ["docker", "--version"],
                "docker-compose": ["docker-compose", "--version"],
                "git": ["git", "--version"],
            }.get(tool, [tool, "--version"])
            
            try:
                version_result = subprocess.run(
                    version_cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                version = version_result.stdout.strip() or version_result.stderr.strip()
            except:
                version = "unknown"
            
            results[tool] = {
                "available": True,
                "path": path,
                "version": version
            }
        else:
            all_available = False
            results[tool] = {
                "available": False,
                "path": None,
                "version": None
            }
    
    return {
        "success": all_available,
        "all_tools_available": all_available,
        "tools": results,
        "missing": [t for t, r in results.items() if not r["available"]]
    }


def setup_database(
    project_path: str = ".",
    database_type: str = "auto",
    run_migrations: bool = True,
    seed_data: bool = False,
    reset: bool = False
) -> dict[str, Any]:
    """Set up database: run migrations and optionally seed data."""
    project_path = Path(project_path).resolve()
    steps = []
    
    # Auto-detect database/ORM type
    if database_type == "auto":
        if (project_path / "prisma").exists():
            database_type = "prisma"
        elif (project_path / "drizzle.config.ts").exists() or (project_path / "drizzle.config.js").exists():
            database_type = "drizzle"
        elif (project_path / "alembic.ini").exists():
            database_type = "alembic"
        elif (project_path / "migrations").exists() and (project_path / "manage.py").exists():
            database_type = "django"
        elif (project_path / "db" / "migrate").exists():
            database_type = "rails"
        elif (project_path / "knexfile.js").exists() or (project_path / "knexfile.ts").exists():
            database_type = "knex"
        elif (project_path / "sequelize.config.js").exists():
            database_type = "sequelize"
        else:
            return {"success": False, "error": "Could not auto-detect database type"}
    
    commands = {
        "prisma": {
            "reset": ["npx", "prisma", "migrate", "reset", "--force"],
            "migrate": ["npx", "prisma", "migrate", "deploy"],
            "seed": ["npx", "prisma", "db", "seed"],
            "generate": ["npx", "prisma", "generate"],
        },
        "drizzle": {
            "migrate": ["npx", "drizzle-kit", "push"],
            "generate": ["npx", "drizzle-kit", "generate"],
        },
        "alembic": {
            "migrate": ["alembic", "upgrade", "head"],
            "reset": ["alembic", "downgrade", "base"],
        },
        "django": {
            "migrate": ["python", "manage.py", "migrate"],
            "seed": ["python", "manage.py", "loaddata", "initial_data"],
        },
        "rails": {
            "reset": ["rails", "db:reset"],
            "migrate": ["rails", "db:migrate"],
            "seed": ["rails", "db:seed"],
        },
        "knex": {
            "migrate": ["npx", "knex", "migrate:latest"],
            "seed": ["npx", "knex", "seed:run"],
            "reset": ["npx", "knex", "migrate:rollback", "--all"],
        },
        "sequelize": {
            "migrate": ["npx", "sequelize-cli", "db:migrate"],
            "seed": ["npx", "sequelize-cli", "db:seed:all"],
            "reset": ["npx", "sequelize-cli", "db:migrate:undo:all"],
        },
    }
    
    if database_type not in commands:
        return {"success": False, "error": f"Unknown database type: {database_type}"}
    
    db_commands = commands[database_type]
    
    try:
        # Reset if requested
        if reset and "reset" in db_commands:
            result = subprocess.run(
                db_commands["reset"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            steps.append({
                "step": "reset",
                "success": result.returncode == 0,
                "output": result.stdout[-1000:] if result.stdout else result.stderr[-1000:]
            })
            if result.returncode != 0:
                return {"success": False, "steps": steps, "error": "Reset failed"}
        
        # Run migrations
        if run_migrations and "migrate" in db_commands:
            result = subprocess.run(
                db_commands["migrate"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            steps.append({
                "step": "migrate",
                "success": result.returncode == 0,
                "output": result.stdout[-1000:] if result.stdout else result.stderr[-1000:]
            })
            if result.returncode != 0:
                return {"success": False, "steps": steps, "error": "Migration failed"}
        
        # Generate client if applicable (Prisma)
        if database_type == "prisma" and "generate" in db_commands:
            result = subprocess.run(
                db_commands["generate"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            steps.append({
                "step": "generate",
                "success": result.returncode == 0,
                "output": result.stdout[-500:] if result.stdout else result.stderr[-500:]
            })
        
        # Seed data if requested
        if seed_data and "seed" in db_commands:
            result = subprocess.run(
                db_commands["seed"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            steps.append({
                "step": "seed",
                "success": result.returncode == 0,
                "output": result.stdout[-1000:] if result.stdout else result.stderr[-1000:]
            })
            if result.returncode != 0:
                return {"success": False, "steps": steps, "error": "Seeding failed"}
        
        return {
            "success": True,
            "database_type": database_type,
            "steps": steps
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Database operation timed out", "steps": steps}
    except FileNotFoundError as e:
        return {"success": False, "error": f"Command not found: {e}", "steps": steps}


def health_check(
    project_path: str = ".",
    services: list[dict[str, Any]] | None = None,
    timeout: int = 5
) -> dict[str, Any]:
    """Verify all services are running and healthy."""
    import socket
    import urllib.request
    import urllib.error
    
    project_path = Path(project_path).resolve()
    results = {}
    
    # Auto-detect services if not provided
    if services is None:
        services = []
        
        # Check docker-compose for services
        compose_file = project_path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = project_path / "docker-compose.yaml"
        
        if compose_file.exists():
            try:
                import re
                content = compose_file.read_text()
                # Simple port extraction from docker-compose
                port_matches = re.findall(r'"?(\d+):(\d+)"?', content)
                for host_port, container_port in port_matches:
                    services.append({
                        "name": f"docker-service-{host_port}",
                        "type": "tcp",
                        "host": "localhost",
                        "port": int(host_port)
                    })
            except:
                pass
        
        # Common development ports
        common_ports = [
            {"name": "frontend-dev", "type": "http", "url": "http://localhost:3000"},
            {"name": "backend-api", "type": "http", "url": "http://localhost:8000"},
            {"name": "database-postgres", "type": "tcp", "host": "localhost", "port": 5432},
            {"name": "database-mysql", "type": "tcp", "host": "localhost", "port": 3306},
            {"name": "redis", "type": "tcp", "host": "localhost", "port": 6379},
        ]
        
        if not services:
            services = common_ports
    
    all_healthy = True
    
    for service in services:
        name = service.get("name", "unknown")
        service_type = service.get("type", "tcp")
        
        try:
            if service_type == "http":
                url = service.get("url", f"http://localhost:{service.get('port', 80)}")
                try:
                    req = urllib.request.Request(url, method='HEAD')
                    with urllib.request.urlopen(req, timeout=timeout) as response:
                        results[name] = {
                            "healthy": True,
                            "type": "http",
                            "url": url,
                            "status_code": response.status
                        }
                except urllib.error.HTTPError as e:
                    # HTTP errors still mean the service is running
                    results[name] = {
                        "healthy": True,
                        "type": "http",
                        "url": url,
                        "status_code": e.code
                    }
                except urllib.error.URLError as e:
                    all_healthy = False
                    results[name] = {
                        "healthy": False,
                        "type": "http",
                        "url": url,
                        "error": str(e.reason)
                    }
            
            elif service_type == "tcp":
                host = service.get("host", "localhost")
                port = service.get("port")
                if port:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    
                    if result == 0:
                        results[name] = {
                            "healthy": True,
                            "type": "tcp",
                            "host": host,
                            "port": port
                        }
                    else:
                        all_healthy = False
                        results[name] = {
                            "healthy": False,
                            "type": "tcp",
                            "host": host,
                            "port": port,
                            "error": "Connection refused"
                        }
            
            elif service_type == "command":
                cmd = service.get("command", [])
                if cmd:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    if result.returncode == 0:
                        results[name] = {
                            "healthy": True,
                            "type": "command",
                            "command": cmd,
                            "output": result.stdout[:500]
                        }
                    else:
                        all_healthy = False
                        results[name] = {
                            "healthy": False,
                            "type": "command",
                            "command": cmd,
                            "error": result.stderr[:500]
                        }
                        
        except Exception as e:
            all_healthy = False
            results[name] = {
                "healthy": False,
                "error": str(e)
            }
    
    return {
        "success": True,
        "all_healthy": all_healthy,
        "services": results,
        "unhealthy": [name for name, r in results.items() if not r.get("healthy", False)]
    }


# MCP Server Implementation
TOOLS = [
    {
        "name": "install_dependencies",
        "description": "Install project dependencies using the appropriate package manager (npm, yarn, pip, poetry, cargo, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "package_manager": {
                    "type": "string",
                    "description": "Package manager to use (auto, npm, yarn, pnpm, pip, poetry, pipenv, cargo, go)",
                    "default": "auto"
                },
                "dev": {
                    "type": "boolean",
                    "description": "Include dev dependencies",
                    "default": True
                },
                "frozen": {
                    "type": "boolean",
                    "description": "Use frozen/locked versions (npm ci, yarn --frozen-lockfile)",
                    "default": False
                }
            }
        }
    },
    {
        "name": "setup_env_file",
        "description": "Create .env file from template (.env.example, .env.template, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "template": {
                    "type": "string",
                    "description": "Template file name",
                    "default": ".env.example"
                },
                "output": {
                    "type": "string",
                    "description": "Output file name",
                    "default": ".env"
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Overwrite existing .env file",
                    "default": False
                },
                "variables": {
                    "type": "object",
                    "description": "Variables to set in the .env file",
                    "additionalProperties": {"type": "string"}
                }
            }
        }
    },
    {
        "name": "validate_environment",
        "description": "Check that all required development tools are installed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of tools to check (auto-detected if not provided)"
                }
            }
        }
    },
    {
        "name": "setup_database",
        "description": "Set up database: run migrations and optionally seed data",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "database_type": {
                    "type": "string",
                    "description": "Database/ORM type (auto, prisma, drizzle, alembic, django, rails, knex, sequelize)",
                    "default": "auto"
                },
                "run_migrations": {
                    "type": "boolean",
                    "description": "Run pending migrations",
                    "default": True
                },
                "seed_data": {
                    "type": "boolean",
                    "description": "Seed the database with initial data",
                    "default": False
                },
                "reset": {
                    "type": "boolean",
                    "description": "Reset the database before migrating",
                    "default": False
                }
            }
        }
    },
    {
        "name": "health_check",
        "description": "Verify all services are running and healthy",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "services": {
                    "type": "array",
                    "description": "List of services to check. Each service has name, type (http/tcp/command), and type-specific fields",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["http", "tcp", "command"]},
                            "url": {"type": "string"},
                            "host": {"type": "string"},
                            "port": {"type": "integer"},
                            "command": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds for each check",
                    "default": 5
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "install_dependencies":
        return install_dependencies(**arguments)
    elif name == "setup_env_file":
        return setup_env_file(**arguments)
    elif name == "validate_environment":
        return validate_environment(**arguments)
    elif name == "setup_database":
        return setup_database(**arguments)
    elif name == "health_check":
        return health_check(**arguments)
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
                            "name": "environment-setup-server",
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
