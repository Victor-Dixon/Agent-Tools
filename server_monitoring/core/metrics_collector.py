#!/usr/bin/env python3
"""
Metrics Collector
=================

Collects performance metrics from game servers.
Supports multiple game types and collection methods.
"""

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import socket

logger = logging.getLogger(__name__)


@dataclass
class ServerMetrics:
    """Snapshot of server performance metrics."""
    timestamp: str
    
    # System metrics
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_percent: float = 0.0
    
    # Game metrics
    player_count: int = 0
    max_players: int = 0
    tick_rate: float = 0.0
    target_tick_rate: float = 60.0
    
    # Network metrics
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    
    # Process metrics
    process_uptime_seconds: int = 0
    thread_count: int = 0
    open_files: int = 0
    
    # Custom metrics
    custom: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def tick_rate_percent(self) -> float:
        """Tick rate as percentage of target."""
        if self.target_tick_rate > 0:
            return (self.tick_rate / self.target_tick_rate) * 100
        return 100.0
    
    @property
    def is_healthy(self) -> bool:
        """Quick health check based on metrics."""
        return (
            self.cpu_percent < 90 and
            self.memory_percent < 90 and
            self.tick_rate_percent > 80
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "system": {
                "cpu_percent": self.cpu_percent,
                "memory_mb": self.memory_mb,
                "memory_percent": self.memory_percent,
                "disk_used_gb": self.disk_used_gb,
                "disk_percent": self.disk_percent,
            },
            "game": {
                "player_count": self.player_count,
                "max_players": self.max_players,
                "tick_rate": self.tick_rate,
                "target_tick_rate": self.target_tick_rate,
                "tick_rate_percent": self.tick_rate_percent,
            },
            "network": {
                "bytes_sent": self.bytes_sent,
                "bytes_recv": self.bytes_recv,
                "packets_sent": self.packets_sent,
                "packets_recv": self.packets_recv,
            },
            "process": {
                "uptime_seconds": self.process_uptime_seconds,
                "thread_count": self.thread_count,
                "open_files": self.open_files,
            },
            "custom": self.custom,
            "is_healthy": self.is_healthy,
        }


class MetricsCollector:
    """
    Collects server performance metrics from multiple sources.
    
    Supports:
    - System metrics (CPU, RAM, disk)
    - Process metrics (for specific game server process)
    - Game-specific metrics (RCON, log parsing)
    - Network metrics
    """
    
    def __init__(
        self,
        game_path: Path,
        process_name: str = "",
        rcon_host: str = "localhost",
        rcon_port: int = 25575,
        rcon_password: str = "",
    ):
        self.game_path = Path(game_path)
        self.process_name = process_name
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        
        self._history: List[ServerMetrics] = []
        self._max_history = 1000
    
    def collect(self) -> ServerMetrics:
        """Collect all metrics and return a snapshot."""
        metrics = ServerMetrics(timestamp=datetime.now().isoformat())
        
        # Collect system metrics
        self._collect_system_metrics(metrics)
        
        # Collect process metrics
        if self.process_name:
            self._collect_process_metrics(metrics)
        
        # Collect game metrics from logs
        self._collect_game_metrics(metrics)
        
        # Store in history
        self._history.append(metrics)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        return metrics
    
    def _collect_system_metrics(self, metrics: ServerMetrics) -> None:
        """Collect system-level metrics."""
        try:
            # Try psutil first
            import psutil
            
            # CPU
            metrics.cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            mem = psutil.virtual_memory()
            metrics.memory_mb = mem.used / (1024 * 1024)
            metrics.memory_percent = mem.percent
            
            # Disk
            disk = psutil.disk_usage(str(self.game_path))
            metrics.disk_used_gb = disk.used / (1024 ** 3)
            metrics.disk_percent = disk.percent
            
            # Network
            net = psutil.net_io_counters()
            metrics.bytes_sent = net.bytes_sent
            metrics.bytes_recv = net.bytes_recv
            metrics.packets_sent = net.packets_sent
            metrics.packets_recv = net.packets_recv
            
        except ImportError:
            # Fallback to command-line tools
            self._collect_system_metrics_fallback(metrics)
    
    def _collect_system_metrics_fallback(self, metrics: ServerMetrics) -> None:
        """Fallback system metrics collection using shell commands."""
        try:
            # CPU from /proc/stat or top
            result = subprocess.run(
                ["grep", "-c", "^processor", "/proc/cpuinfo"],
                capture_output=True, text=True, timeout=5
            )
            cpu_count = int(result.stdout.strip()) if result.returncode == 0 else 1
            
            result = subprocess.run(
                ["cat", "/proc/loadavg"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                load = float(result.stdout.split()[0])
                metrics.cpu_percent = (load / cpu_count) * 100
            
            # Memory from /proc/meminfo
            result = subprocess.run(
                ["cat", "/proc/meminfo"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                meminfo = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, val = line.split(':')
                        meminfo[key.strip()] = int(val.strip().split()[0])
                
                total = meminfo.get('MemTotal', 1)
                avail = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
                used = total - avail
                metrics.memory_mb = used / 1024
                metrics.memory_percent = (used / total) * 100
            
            # Disk from df
            result = subprocess.run(
                ["df", str(self.game_path)],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        metrics.disk_used_gb = int(parts[2]) / (1024 * 1024)
                        metrics.disk_percent = int(parts[4].rstrip('%'))
                        
        except Exception as e:
            logger.warning(f"Fallback metrics collection failed: {e}")
    
    def _collect_process_metrics(self, metrics: ServerMetrics) -> None:
        """Collect metrics for the game server process."""
        try:
            import psutil
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if self.process_name.lower() in proc.info['name'].lower():
                        # Found the process
                        metrics.process_uptime_seconds = int(
                            time.time() - proc.create_time()
                        )
                        metrics.thread_count = proc.num_threads()
                        
                        try:
                            metrics.open_files = len(proc.open_files())
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass
                        
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except ImportError:
            # Try pgrep fallback
            try:
                result = subprocess.run(
                    ["pgrep", "-f", self.process_name],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    pid = result.stdout.strip().split('\n')[0]
                    
                    # Get uptime from /proc
                    stat_result = subprocess.run(
                        ["stat", "-c", "%Y", f"/proc/{pid}"],
                        capture_output=True, text=True, timeout=5
                    )
                    if stat_result.returncode == 0:
                        start_time = int(stat_result.stdout.strip())
                        metrics.process_uptime_seconds = int(time.time() - start_time)
            except Exception:
                pass
    
    def _collect_game_metrics(self, metrics: ServerMetrics) -> None:
        """Collect game-specific metrics from logs."""
        # Look for common log patterns
        log_files = [
            self.game_path / "logs" / "latest.log",
            self.game_path / "BepInEx" / "LogOutput.log",
            self.game_path / "server.log",
        ]
        
        for log_file in log_files:
            if log_file.exists():
                self._parse_game_log(log_file, metrics)
                break
    
    def _parse_game_log(self, log_file: Path, metrics: ServerMetrics) -> None:
        """Parse game log for metrics."""
        try:
            # Read last 100 lines
            with open(log_file, 'r', errors='ignore') as f:
                lines = f.readlines()[-100:]
            
            for line in reversed(lines):
                # Player count patterns
                player_match = re.search(
                    r'(\d+)\s*/\s*(\d+)\s*players?',
                    line, re.IGNORECASE
                )
                if player_match and metrics.player_count == 0:
                    metrics.player_count = int(player_match.group(1))
                    metrics.max_players = int(player_match.group(2))
                
                # Tick rate patterns
                tick_match = re.search(
                    r'(?:tick|tps|tickrate)[:\s]+(\d+\.?\d*)',
                    line, re.IGNORECASE
                )
                if tick_match and metrics.tick_rate == 0:
                    metrics.tick_rate = float(tick_match.group(1))
                
        except Exception as e:
            logger.debug(f"Log parsing failed: {e}")
    
    def get_history(
        self,
        minutes: int = 60,
    ) -> List[ServerMetrics]:
        """Get metrics history for the specified duration."""
        if not self._history:
            return []
        
        cutoff = datetime.now().timestamp() - (minutes * 60)
        
        return [
            m for m in self._history
            if datetime.fromisoformat(m.timestamp).timestamp() > cutoff
        ]
    
    def get_averages(self, minutes: int = 60) -> Dict[str, float]:
        """Get average metrics over the specified duration."""
        history = self.get_history(minutes)
        
        if not history:
            return {}
        
        return {
            "cpu_percent": sum(m.cpu_percent for m in history) / len(history),
            "memory_percent": sum(m.memory_percent for m in history) / len(history),
            "tick_rate": sum(m.tick_rate for m in history) / len(history),
            "player_count": sum(m.player_count for m in history) / len(history),
        }
    
    def check_rcon(self) -> Optional[Dict[str, Any]]:
        """Query server via RCON if available."""
        if not self.rcon_password:
            return None
        
        try:
            # Simple RCON query (Minecraft-style)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.rcon_host, self.rcon_port))
            
            # Basic RCON auth and query would go here
            # This is a placeholder - real implementation needs RCON protocol
            
            sock.close()
            return {"rcon_available": True}
            
        except Exception as e:
            return {"rcon_available": False, "error": str(e)}
