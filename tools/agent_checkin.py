import argparse
import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Import unified utilities with fallback
try:
    from src.utils.unified_utilities import (
        get_logger,
        get_unified_utility,
    )
except ImportError:
    # Fallback if unified utilities not available
    import logging
    from pathlib import Path
    
    def get_logger(name: str):
        return logging.getLogger(name)
    
    class UnifiedUtilityFallback:
        Path = Path
        def remove(self, path):
            Path(path).unlink(missing_ok=True)
    
    def get_unified_utility():
        return UnifiedUtilityFallback()

# Fallback functions
def get_unified_validator():
    """Fallback validator."""
    class Validator:
        def raise_validation_error(self, msg):
            raise ValueError(msg)
    return Validator()

def write_json(data, file_handle, **kwargs):
    """Fallback JSON writer."""
    import json
    json.dump(data, file_handle, **kwargs)

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime"
LOGS_DIR = RUNTIME / "agent_logs"
INDEX_FILE = RUNTIME / "agents_index.json"
SCHEMA_VER = "1.0"


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


def ensure_dirs() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("{}", encoding="utf-8")


def load_json_arg(src: str) -> dict[str, Any]:
    """Load JSON from a file path or stdin ('-')."""
    if src == "-":
        return json.loads(sys.stdin.read())
    path = Path(src)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_minimum(payload: dict[str, Any]) -> None:
    required = ["agent_id", "agent_name", "status", "current_phase"]
    missing = [k for k in required if k not in payload]
    if missing:
        get_unified_validator().raise_validation_error(
            f"missing required keys: {', '.join(missing)}"
        )
    if "last_updated" not in payload:
        payload["last_updated"] = _iso_now()
    payload.setdefault("version", SCHEMA_VER)


def append_jsonl(agent_id: str, obj: dict[str, Any]) -> None:
    log_path = LOGS_DIR / f"{agent_id}.log.jsonl"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as tmp_fh:
            write_json(data, tmp_fh, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def update_index(obj: dict[str, Any]) -> None:
    try:
        current = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        current = {}
    current[obj["agent_id"]] = obj
    atomic_write(INDEX_FILE, current)


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-agent check-in (append + index).")
    parser.add_argument("json", help="Path to JSON payload or '-' for stdin")
    args = parser.parse_args()

    ensure_dirs()
    payload = load_json_arg(args.json)
    validate_minimum(payload)

    agent_id = payload["agent_id"]
    append_jsonl(agent_id, payload)
    update_index(payload)

    get_logger(__name__).info(f"OK: stored check-in for {agent_id} @ {payload['last_updated']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
