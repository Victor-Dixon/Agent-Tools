#!/usr/bin/env python3
"""
Mod Deployment Dashboard
========================

Simple FastAPI dashboard for mod management.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.thunderstore_client import ThunderstoreClient

app = FastAPI(
    title="Mod Deployment Dashboard",
    description="Game server mod management dashboard",
    version="1.0.0",
)


# HTML Templates
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Mod Deployment Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #00d9ff; margin-bottom: 30px; font-size: 2.5em; }
        h2 { color: #00d9ff; margin: 20px 0; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .status-healthy { color: #00ff88; }
        .status-degraded { color: #ffaa00; }
        .status-unhealthy { color: #ff4444; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .stat { text-align: center; padding: 20px; }
        .stat-value { font-size: 3em; font-weight: bold; color: #00d9ff; }
        .stat-label { color: #888; margin-top: 5px; }
        .mod-list { list-style: none; }
        .mod-item {
            background: rgba(0,217,255,0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .mod-name { font-weight: bold; }
        .mod-version { color: #00d9ff; font-family: monospace; }
        .btn {
            background: #00d9ff;
            color: #1a1a2e;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn:hover { background: #00b8d9; }
        .search-box {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid rgba(0,217,255,0.3);
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            margin-bottom: 20px;
        }
        .search-box:focus { outline: none; border-color: #00d9ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #00d9ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Mod Deployment Dashboard</h1>
        
        <div class="grid">
            <div class="card stat">
                <div class="stat-value" id="installed-count">-</div>
                <div class="stat-label">Installed Mods</div>
            </div>
            <div class="card stat">
                <div class="stat-value" id="updates-count">-</div>
                <div class="stat-label">Updates Available</div>
            </div>
            <div class="card stat">
                <div class="stat-value status-healthy" id="server-status">-</div>
                <div class="stat-label">Server Status</div>
            </div>
        </div>
        
        <h2>🔍 Search Thunderstore</h2>
        <div class="card">
            <input type="text" class="search-box" id="search-input" 
                   placeholder="Search for mods... (e.g., BiggerLobby, MoreCompany)">
            <div id="search-results"></div>
        </div>
        
        <h2>📦 Installed Mods</h2>
        <div class="card">
            <ul class="mod-list" id="mod-list">
                <li class="mod-item">Loading...</li>
            </ul>
        </div>
        
        <h2>🔄 Recent Activity</h2>
        <div class="card">
            <table id="activity-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Action</th>
                        <th>Mod</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="activity-body">
                    <tr><td colspan="4">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function fetchData(url) {
            const response = await fetch(url);
            return response.json();
        }
        
        async function loadDashboard() {
            try {
                const status = await fetchData('/api/status');
                document.getElementById('installed-count').textContent = status.installed_count || 0;
                document.getElementById('updates-count').textContent = status.updates_available || 0;
                document.getElementById('server-status').textContent = status.server_status || 'Unknown';
                
                const mods = await fetchData('/api/mods');
                const modList = document.getElementById('mod-list');
                if (mods.length) {
                    modList.innerHTML = mods.map(mod => `
                        <li class="mod-item">
                            <span class="mod-name">${mod.identifier}</span>
                            <span class="mod-version">v${mod.version}</span>
                        </li>
                    `).join('');
                } else {
                    modList.innerHTML = '<li class="mod-item">No mods installed</li>';
                }
            } catch (e) {
                console.error('Failed to load dashboard:', e);
            }
        }
        
        document.getElementById('search-input').addEventListener('input', async (e) => {
            const query = e.target.value;
            if (query.length < 2) {
                document.getElementById('search-results').innerHTML = '';
                return;
            }
            
            try {
                const results = await fetchData(`/api/search?q=${encodeURIComponent(query)}`);
                const html = results.slice(0, 10).map(pkg => `
                    <div class="mod-item">
                        <div>
                            <span class="mod-name">${pkg.name}</span>
                            <span style="color: #888; margin-left: 10px;">${pkg.downloads.toLocaleString()} downloads</span>
                        </div>
                        <button class="btn" onclick="installMod('${pkg.name}')">Install</button>
                    </div>
                `).join('');
                document.getElementById('search-results').innerHTML = html;
            } catch (e) {
                document.getElementById('search-results').innerHTML = '<div class="mod-item">Search failed</div>';
            }
        });
        
        async function installMod(name) {
            alert(`Installing ${name}... (This would trigger installation in production)`);
        }
        
        loadDashboard();
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard HTML."""
    return DASHBOARD_HTML


@app.get("/api/status")
async def get_status():
    """Get overall status."""
    return {
        "installed_count": 0,
        "updates_available": 0,
        "server_status": "Unknown",
        "last_updated": datetime.now().isoformat(),
    }


@app.get("/api/mods")
async def list_mods():
    """List installed mods."""
    return []


@app.get("/api/search")
async def search_mods(q: str, game: str = "lethal-company", limit: int = 20):
    """Search Thunderstore for mods."""
    try:
        client = ThunderstoreClient(game=game)
        results = client.search_packages(query=q, limit=limit)
        return [
            {
                "name": pkg.full_name,
                "owner": pkg.owner,
                "downloads": pkg.total_downloads,
                "rating": pkg.rating_score,
                "version": pkg.latest_version.version_number if pkg.latest_version else "N/A",
            }
            for pkg in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def main():
    """Run the dashboard server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_level="info",
    )


if __name__ == "__main__":
    main()
