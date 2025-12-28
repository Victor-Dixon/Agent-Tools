import sys
import json
import subprocess
from pathlib import Path
import pytest

# Add workspace root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMCPServers:
    def _run_server(self, server_module, input_data):
        """Run an MCP server module with input data."""
        cmd = [sys.executable, "-m", server_module]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=json.dumps(input_data) + "\n")
        return stdout, stderr

    def test_tools_server_initialize(self):
        """Test swarm-tools-server initialization."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.tools", init_req)
        response = json.loads(stdout)
        
        assert response["jsonrpc"] == "2.0"
        
        assert "result" in response
        assert "capabilities" in response["result"]
        assert "tools" in response["result"]["capabilities"]
        
        tools = response["result"]["capabilities"]["tools"]
        assert "run_monitor" in tools
        assert "run_security_scan" in tools

    def test_messaging_server_initialize(self):
        """Test swarm-messaging-server initialization."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.messaging", init_req)
        response = json.loads(stdout)
        
        assert response["result"]["serverInfo"]["name"] == "swarm-messaging"
        tools = response["result"]["capabilities"]["tools"]
        assert "send_agent_message" in tools

    def test_memory_server_initialize(self):
        """Test swarm-memory-server initialization."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.memory", init_req)
        response = json.loads(stdout)
        
        assert response["result"]["serverInfo"]["name"] == "swarm-memory"

    def test_tasks_server_initialize(self):
        """Test swarm-tasks-server initialization and Stage 4 tools."""
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
        }
        
        stdout, _ = self._run_server("swarm_mcp.servers.tasks", init_req)
        response = json.loads(stdout)
        
        assert response["result"]["serverInfo"]["name"] == "swarm-tasks"
        tools = response["result"]["capabilities"]["tools"]
        
        # Core tasks
        assert "add_task_to_inbox" in tools
        assert "mark_task_complete" in tools
        
        # Stage 4 additions
        assert "select_next_task" in tools
        assert "verify_task_completion" in tools
        assert "recover_system" in tools
