"""
Sites Registry CLI
==================

Manages the control-plane sites registry with list/validate/seed/add operations.
This is read-focused and avoids touching deploy/post behaviors. Credentials are
not stored here; the registry only references their source (e.g., sites.json).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

REGISTRY_PATH = Path("runtime/control_plane/sites_registry.json")
SITES_JSON_PATH = Path(".deploy_credentials/sites.json")


# ----------------- Models -----------------

@dataclass
class SiteEntry:
    id: str
    domain: str
    base_url: str
    type: str  # wp | static
    adapter: str
    creds_source: str
    health_path: str = "/"
    capabilities: Optional[Dict[str, bool]] = None
    env: str = "prod"
    notes: str = ""


# ----------------- Registry helpers -----------------

def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"schema_version": "1.0", "sites": []}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(registry: Dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=False), encoding="utf-8")


# ----------------- Validation -----------------

def validate_registry(registry: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if "sites" not in registry or not isinstance(registry["sites"], list):
        errors.append("registry.sites must be a list")
        return errors
    for idx, site in enumerate(registry["sites"]):
        prefix = f"sites[{idx}]"
        for field in ("id", "domain", "base_url", "type", "adapter", "creds_source"):
            if field not in site or not site[field]:
                errors.append(f"{prefix}.{field} missing or empty")
        if site.get("type") not in {"wp", "static"}:
            errors.append(f"{prefix}.type must be 'wp' or 'static'")
        health_path = site.get("health_path")
        if health_path is None or not str(health_path).startswith("/"):
            errors.append(f"{prefix}.health_path must start with '/'")
        caps = site.get("capabilities", {})
        if not isinstance(caps, dict):
            errors.append(f"{prefix}.capabilities must be an object")
        if caps and caps.get("blog") and site.get("type") != "wp":
            errors.append(f"{prefix}.blog=true requires type='wp'")
    return errors


# ----------------- Commands -----------------

def cmd_list(registry: Dict[str, Any]) -> int:
    sites = registry.get("sites", [])
    if not sites:
        print("No sites registered.")
        return 0
    for s in sites:
        caps = s.get("capabilities", {})
        print(
            f"- {s.get('id')} ({s.get('domain')}) "
            f"type={s.get('type')} adapter={s.get('adapter')} "
            f"blog={caps.get('blog', False)} deploy={caps.get('deploy', False)}"
        )
    return 0


def cmd_validate(registry: Dict[str, Any]) -> int:
    errors = validate_registry(registry)
    if errors:
        print("❌ Validation failed:")
        for e in errors:
            print(f" - {e}")
        return 1
    print("✅ Registry is valid.")
    return 0


def cmd_seed_from_sites_json(registry: Dict[str, Any]) -> int:
    if not SITES_JSON_PATH.exists():
        print("No .deploy_credentials/sites.json found; nothing to seed.")
        return 1
    try:
        sites_json = json.loads(SITES_JSON_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        print(f"Failed to read sites.json: {exc}")
        return 1

    existing_ids = {s["id"] for s in registry.get("sites", []) if "id" in s}
    new_sites: List[Dict[str, Any]] = []

    for domain, info in sites_json.items():
        site_id = domain.split(".")[0].replace(" ", "_").lower()
        if site_id in existing_ids:
            continue
        entry = SiteEntry(
            id=site_id,
            domain=domain.lower(),
            base_url=f"https://{domain.lower()}",
            type="wp",
            adapter=f"hostinger.{site_id}",
            creds_source="sites.json",
            health_path="/wp-json",
            capabilities={
                "blog": False,
                "deploy": False,
                "cache_flush": False,
                "health_check": True,
            },
            env="prod",
            notes="Seeded from sites.json; enable capabilities manually.",
        )
        new_sites.append(asdict(entry))

    if not new_sites:
        print("No new sites to seed.")
        return 0

    registry.setdefault("sites", []).extend(new_sites)
    save_registry(registry)
    print(f"Seeded {len(new_sites)} site(s) from sites.json into registry.")
    return 0


def cmd_add(registry: Dict[str, Any], args: argparse.Namespace) -> int:
    site_id = args.id or args.domain.split(".")[0].replace(" ", "_").lower()
    # Ensure unique id
    if any(s.get("id") == site_id for s in registry.get("sites", [])):
        print(f"Site id '{site_id}' already exists; aborting.")
        return 1
    caps = {c: True for c in (args.allow or [])}
    entry = SiteEntry(
        id=site_id,
        domain=args.domain.lower(),
        base_url=args.base_url.rstrip("/"),
        type=args.type,
        adapter=args.adapter,
        creds_source=args.creds_source,
        health_path=args.health_path or ("/wp-json" if args.type == "wp" else "/"),
        capabilities={
            "blog": caps.get("blog", False),
            "deploy": caps.get("deploy", False),
            "cache_flush": caps.get("cache_flush", False),
            "health_check": True,
        },
        env=args.env,
        notes=args.notes or "",
    )
    registry.setdefault("sites", []).append(asdict(entry))
    save_registry(registry)
    print(f"Added site '{site_id}' to registry.")
    return 0


# ----------------- CLI -----------------

def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage sites registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List sites in registry")
    sub.add_parser("validate", help="Validate registry schema")
    sub.add_parser("seed-from-sites-json", help="Seed registry entries from .deploy_credentials/sites.json")

    add_p = sub.add_parser("add", help="Add a site entry")
    add_p.add_argument("--id", help="Stable site id (default: slug of domain)")
    add_p.add_argument("--domain", required=True, help="Domain, e.g., example.com")
    add_p.add_argument("--base-url", required=True, help="Base URL, e.g., https://example.com")
    add_p.add_argument("--type", choices=["wp", "static"], required=True)
    add_p.add_argument("--adapter", required=True, help="Adapter key, e.g., hostinger.freerideinvestor")
    add_p.add_argument("--creds-source", default="sites.json", help="Where creds live (label only)")
    add_p.add_argument("--health-path", help="Health path, default /wp-json for wp, / for static")
    add_p.add_argument("--allow", nargs="*", choices=["blog", "deploy", "cache_flush"], help="Enable capabilities")
    add_p.add_argument("--env", default="prod", help="Environment label")
    add_p.add_argument("--notes", help="Notes")

    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    registry = load_registry()

    if args.command == "list":
        return cmd_list(registry)
    if args.command == "validate":
        return cmd_validate(registry)
    if args.command == "seed-from-sites-json":
        return cmd_seed_from_sites_json(registry)
    if args.command == "add":
        return cmd_add(registry, args)

    print("Unknown command")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

