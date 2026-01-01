#!/usr/bin/env python3
"""
Dependency Resolver
===================

Resolves mod dependencies with conflict detection and version constraints.
Handles circular dependencies and provides resolution strategies.

Author: Mod Deployment Automation Pipeline
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .thunderstore_client import ThunderstoreClient, ModPackage

logger = logging.getLogger(__name__)


class ResolutionStrategy(Enum):
    """Strategy for resolving version conflicts."""
    LATEST = "latest"           # Always use latest version
    OLDEST = "oldest"           # Use oldest compatible version
    REQUESTED = "requested"     # Prefer explicitly requested versions
    CONSERVATIVE = "conservative"  # Prefer stable/older versions


@dataclass
class DependencyNode:
    """Represents a dependency in the resolution graph."""
    identifier: str
    version: str
    dependents: Set[str] = field(default_factory=set)  # Mods that depend on this
    dependencies: Set[str] = field(default_factory=set)  # Mods this depends on
    is_root: bool = False
    
    @property
    def full_name(self) -> str:
        return f"{self.identifier}-{self.version}"


@dataclass
class ResolutionResult:
    """Result of dependency resolution."""
    success: bool
    resolved: Dict[str, str]  # identifier -> version
    install_order: List[str]  # Order to install mods
    conflicts: List[Dict[str, Any]]  # List of conflicts found
    warnings: List[str]
    missing: List[str]  # Dependencies not found in repository
    
    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "resolved": self.resolved,
            "install_order": self.install_order,
            "conflicts": self.conflicts,
            "warnings": self.warnings,
            "missing": self.missing,
        }


class DependencyResolver:
    """
    Resolves mod dependencies with support for:
    - Transitive dependencies
    - Version conflict detection
    - Circular dependency handling
    - Install order calculation
    """
    
    def __init__(
        self,
        client: ThunderstoreClient,
        strategy: ResolutionStrategy = ResolutionStrategy.LATEST,
    ):
        """
        Initialize the dependency resolver.
        
        Args:
            client: ThunderstoreClient for fetching mod info
            strategy: Version resolution strategy
        """
        self.client = client
        self.strategy = strategy
        self._nodes: Dict[str, DependencyNode] = {}
        self._version_requirements: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    
    def _parse_dependency(self, dep_string: str) -> Tuple[str, str, str]:
        """
        Parse a dependency string into owner, name, and version.
        
        Format: Owner-ModName-Version (e.g., "BepInEx-BepInExPack-5.4.2100")
        
        Returns:
            Tuple of (owner, name, version)
        """
        parts = dep_string.split("-")
        if len(parts) >= 3:
            owner = parts[0]
            name = parts[1]
            version = "-".join(parts[2:])  # Handle versions with dashes
            return owner, name, version
        elif len(parts) == 2:
            return parts[0], parts[1], "latest"
        else:
            return dep_string, "", "latest"
    
    def _get_identifier(self, dep_string: str) -> str:
        """Get the identifier (Owner-ModName) from a dependency string."""
        owner, name, _ = self._parse_dependency(dep_string)
        return f"{owner}-{name}"
    
    def resolve(
        self,
        mods: List[str],
        installed: Optional[Dict[str, str]] = None,
        max_depth: int = 10,
    ) -> ResolutionResult:
        """
        Resolve dependencies for a list of mods.
        
        Args:
            mods: List of mod identifiers or full dependency strings
            installed: Currently installed mods (identifier -> version)
            max_depth: Maximum dependency depth to prevent infinite loops
            
        Returns:
            ResolutionResult with resolved dependencies and install order
        """
        self._nodes.clear()
        self._version_requirements.clear()
        
        installed = installed or {}
        conflicts = []
        warnings = []
        missing = []
        
        # Queue for BFS traversal
        to_process = []
        processed = set()
        
        # Add root mods to queue
        for mod in mods:
            identifier = self._get_identifier(mod)
            _, _, version = self._parse_dependency(mod)
            to_process.append((identifier, version, 0, None))  # (id, version, depth, dependent)
        
        logger.info(f"Resolving dependencies for {len(mods)} mods")
        
        # BFS through dependency tree
        while to_process:
            identifier, requested_version, depth, dependent = to_process.pop(0)
            
            if depth > max_depth:
                warnings.append(f"Max depth exceeded for {identifier}")
                continue
            
            process_key = f"{identifier}:{requested_version}"
            if process_key in processed:
                continue
            processed.add(process_key)
            
            # Track version requirement
            if dependent:
                self._version_requirements[identifier].append((dependent, requested_version))
            
            # Get package info
            package = self.client.get_package(identifier)
            if not package:
                missing.append(identifier)
                logger.warning(f"Package not found: {identifier}")
                continue
            
            # Determine version to use
            if identifier in installed:
                version = installed[identifier]
            elif requested_version != "latest":
                version = requested_version
            else:
                latest = package.latest_version
                version = latest.version_number if latest else "0.0.0"
            
            # Create or update node
            if identifier not in self._nodes:
                self._nodes[identifier] = DependencyNode(
                    identifier=identifier,
                    version=version,
                    is_root=(dependent is None),
                )
            
            node = self._nodes[identifier]
            if dependent:
                node.dependents.add(dependent)
            
            # Get dependencies for this mod
            deps = self.client.get_mod_dependencies(identifier, version)
            
            for dep in deps:
                dep_identifier = self._get_identifier(dep)
                _, _, dep_version = self._parse_dependency(dep)
                
                node.dependencies.add(dep_identifier)
                
                # Add to processing queue
                if dep_identifier not in processed:
                    to_process.append((dep_identifier, dep_version, depth + 1, identifier))
        
        # Detect version conflicts
        conflicts = self._detect_conflicts()
        
        # Apply resolution strategy
        if conflicts and self.strategy != ResolutionStrategy.REQUESTED:
            self._resolve_conflicts(conflicts)
            conflicts = self._detect_conflicts()  # Re-check after resolution
        
        # Calculate install order (topological sort)
        install_order = self._calculate_install_order()
        
        # Build final resolved dict
        resolved = {node.identifier: node.version for node in self._nodes.values()}
        
        success = not conflicts and not missing
        
        result = ResolutionResult(
            success=success,
            resolved=resolved,
            install_order=install_order,
            conflicts=conflicts,
            warnings=warnings,
            missing=missing,
        )
        
        logger.info(f"Resolution complete: {len(resolved)} mods, {len(conflicts)} conflicts")
        return result
    
    def _detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect version conflicts in resolved dependencies."""
        conflicts = []
        
        for identifier, requirements in self._version_requirements.items():
            if len(requirements) < 2:
                continue
            
            versions = set(req[1] for req in requirements if req[1] != "latest")
            
            if len(versions) > 1:
                conflict = {
                    "mod": identifier,
                    "required_versions": list(versions),
                    "requested_by": {req[0]: req[1] for req in requirements},
                    "resolved_version": self._nodes[identifier].version if identifier in self._nodes else None,
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def _resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> None:
        """Apply resolution strategy to conflicts."""
        for conflict in conflicts:
            identifier = conflict["mod"]
            versions = conflict["required_versions"]
            
            if identifier not in self._nodes:
                continue
            
            if self.strategy == ResolutionStrategy.LATEST:
                # Sort versions and pick newest (simple string compare for semver)
                resolved_version = sorted(versions, reverse=True)[0]
            elif self.strategy == ResolutionStrategy.OLDEST:
                resolved_version = sorted(versions)[0]
            elif self.strategy == ResolutionStrategy.CONSERVATIVE:
                # Pick the middle version
                sorted_versions = sorted(versions)
                resolved_version = sorted_versions[len(sorted_versions) // 2]
            else:
                resolved_version = self._nodes[identifier].version
            
            self._nodes[identifier].version = resolved_version
            logger.info(f"Resolved {identifier} to version {resolved_version}")
    
    def _calculate_install_order(self) -> List[str]:
        """
        Calculate installation order using topological sort.
        Dependencies are installed before dependents.
        """
        if not self._nodes:
            return []
        
        # Kahn's algorithm for topological sort
        in_degree = {node.identifier: 0 for node in self._nodes.values()}
        
        for node in self._nodes.values():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[node.identifier] += 1
        
        # Start with nodes that have no dependencies
        queue = [
            identifier for identifier, degree in in_degree.items()
            if degree == 0
        ]
        
        order = []
        while queue:
            # Sort queue to ensure deterministic order
            queue.sort()
            current = queue.pop(0)
            order.append(current)
            
            # Reduce in-degree for dependents
            for node in self._nodes.values():
                if current in node.dependencies:
                    in_degree[node.identifier] -= 1
                    if in_degree[node.identifier] == 0:
                        queue.append(node.identifier)
        
        # Check for cycles (if order doesn't contain all nodes)
        if len(order) != len(self._nodes):
            remaining = set(self._nodes.keys()) - set(order)
            logger.warning(f"Circular dependencies detected: {remaining}")
            # Add remaining nodes at the end
            order.extend(sorted(remaining))
        
        return order
    
    def get_dependency_tree(
        self,
        mod: str,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        """
        Get a visual dependency tree for a mod.
        
        Args:
            mod: Mod identifier
            max_depth: Maximum tree depth
            
        Returns:
            Nested dict representing the dependency tree
        """
        identifier = self._get_identifier(mod)
        visited = set()
        
        def build_tree(ident: str, depth: int) -> Dict[str, Any]:
            if depth > max_depth or ident in visited:
                return {"name": ident, "truncated": True}
            
            visited.add(ident)
            deps = self.client.get_mod_dependencies(ident)
            
            children = []
            for dep in deps:
                dep_ident = self._get_identifier(dep)
                _, _, version = self._parse_dependency(dep)
                child = build_tree(dep_ident, depth + 1)
                child["required_version"] = version
                children.append(child)
            
            package = self.client.get_package(ident)
            latest = package.latest_version.version_number if package and package.latest_version else "unknown"
            
            return {
                "name": ident,
                "latest_version": latest,
                "dependencies": children,
            }
        
        return build_tree(identifier, 0)
    
    def check_compatibility(
        self,
        mod: str,
        installed: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Check if a mod is compatible with currently installed mods.
        
        Args:
            mod: Mod to check
            installed: Currently installed mods
            
        Returns:
            Compatibility report
        """
        identifier = self._get_identifier(mod)
        deps = self.client.get_mod_dependencies(identifier)
        
        issues = []
        compatible = []
        missing = []
        
        for dep in deps:
            dep_ident = self._get_identifier(dep)
            _, _, required_version = self._parse_dependency(dep)
            
            if dep_ident in installed:
                installed_version = installed[dep_ident]
                if required_version != "latest" and installed_version != required_version:
                    issues.append({
                        "dependency": dep_ident,
                        "required": required_version,
                        "installed": installed_version,
                    })
                else:
                    compatible.append(dep_ident)
            else:
                missing.append({
                    "dependency": dep_ident,
                    "required": required_version,
                })
        
        return {
            "mod": identifier,
            "is_compatible": len(issues) == 0,
            "has_missing_deps": len(missing) > 0,
            "compatible": compatible,
            "issues": issues,
            "missing": missing,
        }
