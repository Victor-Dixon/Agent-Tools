#!/usr/bin/env python3
"""
Database Operations Server - MCP server for database lifecycle management.

Tools:
- run_migration: Execute pending migrations
- rollback_migration: Revert last migration
- seed_database: Load seed/test data
- backup_database: Create database backup
- reset_database: Drop and recreate database
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def detect_orm(project_path: Path) -> str | None:
    """Detect the ORM/database tool used in the project."""
    if (project_path / "prisma").exists() or (project_path / "prisma" / "schema.prisma").exists():
        return "prisma"
    if (project_path / "drizzle.config.ts").exists() or (project_path / "drizzle.config.js").exists():
        return "drizzle"
    if (project_path / "alembic.ini").exists():
        return "alembic"
    if (project_path / "manage.py").exists() and (project_path / "migrations").exists():
        return "django"
    if (project_path / "db" / "migrate").exists():
        return "rails"
    if (project_path / "knexfile.js").exists() or (project_path / "knexfile.ts").exists():
        return "knex"
    if (project_path / "typeorm.config.ts").exists() or (project_path / "ormconfig.json").exists():
        return "typeorm"
    if (project_path / "sequelize.config.js").exists() or (project_path / ".sequelizerc").exists():
        return "sequelize"
    if (project_path / "migrations").exists():
        # Check for golang-migrate
        if any((project_path / "migrations").glob("*.up.sql")):
            return "golang-migrate"
        # Check for flyway
        if any((project_path / "migrations").glob("V*.sql")):
            return "flyway"
    return None


def run_migration(
    project_path: str = ".",
    orm: str = "auto",
    target: str | None = None
) -> dict[str, Any]:
    """Execute pending database migrations."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    if orm == "auto":
        orm = detect_orm(project_path)
        if not orm:
            return {"success": False, "error": "Could not auto-detect ORM/migration tool"}
    
    commands = {
        "prisma": ["npx", "prisma", "migrate", "deploy"],
        "drizzle": ["npx", "drizzle-kit", "push"],
        "alembic": ["alembic", "upgrade", target or "head"],
        "django": ["python", "manage.py", "migrate"],
        "rails": ["rails", "db:migrate"],
        "knex": ["npx", "knex", "migrate:latest"],
        "typeorm": ["npx", "typeorm", "migration:run"],
        "sequelize": ["npx", "sequelize-cli", "db:migrate"],
        "golang-migrate": ["migrate", "-path", "migrations", "-database", "${DATABASE_URL}", "up"],
        "flyway": ["flyway", "migrate"],
    }
    
    if orm not in commands:
        return {"success": False, "error": f"Unknown ORM: {orm}", "supported": list(commands.keys())}
    
    cmd = commands[orm]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ}
        )
        
        return {
            "success": result.returncode == 0,
            "orm": orm,
            "command": " ".join(cmd),
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Migration timed out after 120 seconds"}
    except FileNotFoundError as e:
        return {"success": False, "error": f"Command not found: {e}"}


def rollback_migration(
    project_path: str = ".",
    orm: str = "auto",
    steps: int = 1
) -> dict[str, Any]:
    """Revert the last migration(s)."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    if orm == "auto":
        orm = detect_orm(project_path)
        if not orm:
            return {"success": False, "error": "Could not auto-detect ORM/migration tool"}
    
    commands = {
        "prisma": {
            "cmd": ["npx", "prisma", "migrate", "reset", "--skip-seed"],
            "warning": "Prisma doesn't support single-step rollback. This will reset all migrations."
        },
        "drizzle": {
            "cmd": ["npx", "drizzle-kit", "drop"],
            "warning": "Drizzle doesn't have built-in rollback. Use drop with caution."
        },
        "alembic": {
            "cmd": ["alembic", "downgrade", f"-{steps}"]
        },
        "django": {
            "cmd": ["python", "manage.py", "migrate", "--fake"],  # Need app name for proper rollback
            "warning": "Django rollback requires specifying the app and migration to rollback to"
        },
        "rails": {
            "cmd": ["rails", "db:rollback", f"STEP={steps}"]
        },
        "knex": {
            "cmd": ["npx", "knex", "migrate:rollback"] if steps == 1 else ["npx", "knex", "migrate:rollback", "--all"]
        },
        "typeorm": {
            "cmd": ["npx", "typeorm", "migration:revert"]
        },
        "sequelize": {
            "cmd": ["npx", "sequelize-cli", "db:migrate:undo"] if steps == 1 else ["npx", "sequelize-cli", "db:migrate:undo:all"]
        },
        "golang-migrate": {
            "cmd": ["migrate", "-path", "migrations", "-database", "${DATABASE_URL}", "down", str(steps)]
        },
        "flyway": {
            "cmd": ["flyway", "undo"]
        },
    }
    
    if orm not in commands:
        return {"success": False, "error": f"Unknown ORM: {orm}"}
    
    cmd_info = commands[orm]
    cmd = cmd_info if isinstance(cmd_info, list) else cmd_info["cmd"]
    warning = cmd_info.get("warning") if isinstance(cmd_info, dict) else None
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ}
        )
        
        response = {
            "success": result.returncode == 0,
            "orm": orm,
            "steps": steps,
            "command": " ".join(cmd),
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "exit_code": result.returncode
        }
        
        if warning:
            response["warning"] = warning
        
        return response
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Rollback timed out after 120 seconds"}
    except FileNotFoundError as e:
        return {"success": False, "error": f"Command not found: {e}"}


def seed_database(
    project_path: str = ".",
    orm: str = "auto",
    seed_file: str | None = None
) -> dict[str, Any]:
    """Load seed or test data into the database."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    if orm == "auto":
        orm = detect_orm(project_path)
        if not orm:
            return {"success": False, "error": "Could not auto-detect ORM/migration tool"}
    
    commands = {
        "prisma": ["npx", "prisma", "db", "seed"],
        "drizzle": None,  # Drizzle doesn't have built-in seeding
        "alembic": None,  # Alembic doesn't have built-in seeding
        "django": ["python", "manage.py", "loaddata", seed_file or "initial_data"],
        "rails": ["rails", "db:seed"],
        "knex": ["npx", "knex", "seed:run"],
        "typeorm": None,  # TypeORM doesn't have built-in seeding
        "sequelize": ["npx", "sequelize-cli", "db:seed:all"],
    }
    
    if orm not in commands:
        return {"success": False, "error": f"Unknown ORM: {orm}"}
    
    cmd = commands.get(orm)
    
    if cmd is None:
        # Try to find custom seed script
        possible_seeds = [
            project_path / "seed.ts",
            project_path / "seed.js",
            project_path / "scripts" / "seed.ts",
            project_path / "scripts" / "seed.js",
            project_path / "db" / "seed.ts",
            project_path / "db" / "seed.js",
            project_path / "seeds" / "seed.py",
        ]
        
        for seed_path in possible_seeds:
            if seed_path.exists():
                if seed_path.suffix in ['.ts', '.js']:
                    cmd = ["npx", "tsx", str(seed_path)]
                elif seed_path.suffix == '.py':
                    cmd = ["python", str(seed_path)]
                break
        
        if cmd is None:
            return {
                "success": False,
                "error": f"{orm} doesn't have built-in seeding",
                "hint": "Create a seed script at scripts/seed.ts or scripts/seed.js"
            }
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ}
        )
        
        return {
            "success": result.returncode == 0,
            "orm": orm,
            "command": " ".join(cmd),
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Seeding timed out after 120 seconds"}
    except FileNotFoundError as e:
        return {"success": False, "error": f"Command not found: {e}"}


def backup_database(
    project_path: str = ".",
    database_type: str = "auto",
    output_path: str | None = None,
    database_url: str | None = None
) -> dict[str, Any]:
    """Create a database backup."""
    project_path = Path(project_path).resolve()
    
    # Generate timestamp for backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Try to get database URL from environment or .env file
    db_url = database_url or os.environ.get("DATABASE_URL")
    
    if not db_url:
        env_file = project_path / ".env"
        if env_file.exists():
            content = env_file.read_text()
            for line in content.split('\n'):
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=", 1)[1].strip().strip('"\'')
                    break
    
    # Auto-detect database type from URL
    if database_type == "auto" and db_url:
        if db_url.startswith("postgres"):
            database_type = "postgresql"
        elif db_url.startswith("mysql"):
            database_type = "mysql"
        elif db_url.startswith("mongodb"):
            database_type = "mongodb"
        elif "sqlite" in db_url or db_url.endswith(".db"):
            database_type = "sqlite"
    
    if database_type == "auto":
        return {"success": False, "error": "Could not auto-detect database type. Provide database_type or DATABASE_URL"}
    
    backup_dir = project_path / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    if database_type == "postgresql":
        output_path = output_path or str(backup_dir / f"backup_{timestamp}.sql")
        
        # Parse connection string or use pg_dump with DATABASE_URL
        cmd = ["pg_dump", "-f", output_path]
        if db_url:
            cmd = ["pg_dump", db_url, "-f", output_path]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "DATABASE_URL": db_url} if db_url else os.environ
            )
            
            if result.returncode == 0:
                file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
                return {
                    "success": True,
                    "database_type": database_type,
                    "backup_path": output_path,
                    "size_bytes": file_size,
                    "size_human": f"{file_size / 1024 / 1024:.2f} MB"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except FileNotFoundError:
            return {"success": False, "error": "pg_dump not found. Install PostgreSQL client tools."}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Backup timed out"}
    
    elif database_type == "mysql":
        output_path = output_path or str(backup_dir / f"backup_{timestamp}.sql")
        
        cmd = ["mysqldump", "--result-file", output_path]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                file_size = Path(output_path).stat().st_size if Path(output_path).exists() else 0
                return {
                    "success": True,
                    "database_type": database_type,
                    "backup_path": output_path,
                    "size_bytes": file_size
                }
            else:
                return {"success": False, "error": result.stderr}
                
        except FileNotFoundError:
            return {"success": False, "error": "mysqldump not found. Install MySQL client tools."}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Backup timed out"}
    
    elif database_type == "mongodb":
        output_path = output_path or str(backup_dir / f"backup_{timestamp}")
        
        cmd = ["mongodump", "--out", output_path]
        if db_url:
            cmd = ["mongodump", "--uri", db_url, "--out", output_path]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "database_type": database_type,
                    "backup_path": output_path
                }
            else:
                return {"success": False, "error": result.stderr}
                
        except FileNotFoundError:
            return {"success": False, "error": "mongodump not found. Install MongoDB database tools."}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Backup timed out"}
    
    elif database_type == "sqlite":
        # Find SQLite database file
        sqlite_files = list(project_path.glob("*.db")) + list(project_path.glob("*.sqlite"))
        if not sqlite_files:
            return {"success": False, "error": "No SQLite database file found"}
        
        db_file = sqlite_files[0]
        output_path = output_path or str(backup_dir / f"{db_file.stem}_backup_{timestamp}.db")
        
        import shutil
        try:
            shutil.copy2(db_file, output_path)
            file_size = Path(output_path).stat().st_size
            return {
                "success": True,
                "database_type": database_type,
                "source": str(db_file),
                "backup_path": output_path,
                "size_bytes": file_size
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    else:
        return {"success": False, "error": f"Unknown database type: {database_type}"}


def reset_database(
    project_path: str = ".",
    orm: str = "auto",
    confirm: bool = False
) -> dict[str, Any]:
    """Drop and recreate the database."""
    if not confirm:
        return {
            "success": False,
            "error": "Database reset requires confirmation",
            "hint": "Set confirm=true to proceed. WARNING: This will delete all data!"
        }
    
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    if orm == "auto":
        orm = detect_orm(project_path)
        if not orm:
            return {"success": False, "error": "Could not auto-detect ORM/migration tool"}
    
    commands = {
        "prisma": ["npx", "prisma", "migrate", "reset", "--force"],
        "drizzle": ["npx", "drizzle-kit", "drop"],
        "alembic": [["alembic", "downgrade", "base"], ["alembic", "upgrade", "head"]],
        "django": ["python", "manage.py", "flush", "--no-input"],
        "rails": ["rails", "db:reset"],
        "knex": [["npx", "knex", "migrate:rollback", "--all"], ["npx", "knex", "migrate:latest"]],
        "typeorm": ["npx", "typeorm", "schema:drop"],
        "sequelize": [["npx", "sequelize-cli", "db:drop"], ["npx", "sequelize-cli", "db:create"], ["npx", "sequelize-cli", "db:migrate"]],
    }
    
    if orm not in commands:
        return {"success": False, "error": f"Unknown ORM: {orm}"}
    
    cmd = commands[orm]
    
    try:
        # Handle single command or sequence of commands
        if isinstance(cmd[0], list):
            results = []
            for c in cmd:
                result = subprocess.run(
                    c,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env={**os.environ}
                )
                results.append({
                    "command": " ".join(c),
                    "exit_code": result.returncode,
                    "stdout": result.stdout[-500:],
                    "stderr": result.stderr[-500:]
                })
                if result.returncode != 0:
                    return {
                        "success": False,
                        "orm": orm,
                        "steps": results,
                        "error": f"Step failed: {' '.join(c)}"
                    }
            
            return {
                "success": True,
                "orm": orm,
                "steps": results,
                "message": "Database reset complete"
            }
        else:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ}
            )
            
            return {
                "success": result.returncode == 0,
                "orm": orm,
                "command": " ".join(cmd),
                "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
                "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
                "exit_code": result.returncode
            }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Reset timed out after 120 seconds"}
    except FileNotFoundError as e:
        return {"success": False, "error": f"Command not found: {e}"}


# MCP Server Implementation
TOOLS = [
    {
        "name": "run_migration",
        "description": "Execute pending database migrations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "orm": {
                    "type": "string",
                    "description": "ORM/migration tool (auto, prisma, drizzle, alembic, django, rails, knex, typeorm, sequelize)",
                    "default": "auto"
                },
                "target": {
                    "type": "string",
                    "description": "Target migration (for alembic: revision, for others: usually ignored)"
                }
            }
        }
    },
    {
        "name": "rollback_migration",
        "description": "Revert the last migration(s)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "orm": {
                    "type": "string",
                    "description": "ORM/migration tool",
                    "default": "auto"
                },
                "steps": {
                    "type": "integer",
                    "description": "Number of migrations to rollback",
                    "default": 1
                }
            }
        }
    },
    {
        "name": "seed_database",
        "description": "Load seed or test data into the database",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "orm": {
                    "type": "string",
                    "description": "ORM/migration tool",
                    "default": "auto"
                },
                "seed_file": {
                    "type": "string",
                    "description": "Specific seed file to load (for Django)"
                }
            }
        }
    },
    {
        "name": "backup_database",
        "description": "Create a database backup",
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
                    "description": "Database type (auto, postgresql, mysql, mongodb, sqlite)",
                    "default": "auto"
                },
                "output_path": {
                    "type": "string",
                    "description": "Path for the backup file"
                },
                "database_url": {
                    "type": "string",
                    "description": "Database connection URL (overrides DATABASE_URL env)"
                }
            }
        }
    },
    {
        "name": "reset_database",
        "description": "Drop and recreate the database (DESTRUCTIVE)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "orm": {
                    "type": "string",
                    "description": "ORM/migration tool",
                    "default": "auto"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirm database reset (required to prevent accidental data loss)",
                    "default": False
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "run_migration":
        return run_migration(**arguments)
    elif name == "rollback_migration":
        return rollback_migration(**arguments)
    elif name == "seed_database":
        return seed_database(**arguments)
    elif name == "backup_database":
        return backup_database(**arguments)
    elif name == "reset_database":
        return reset_database(**arguments)
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
                            "name": "database-operations-server",
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
