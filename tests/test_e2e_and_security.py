import pytest
import asyncio
from fastapi.testclient import TestClient

from src.multi_agent_system.config_loader import load_config
from src.multi_agent_system.orchestrator import Orchestrator
from src.multi_agent_system.api.app import app
from src.multi_agent_system.tools.registry import ToolRegistry, PermissionLevel
from src.multi_agent_system.tools.filesystem import register_filesystem_tools
from src.multi_agent_system.tools.shell import _is_command_safe
from src.multi_agent_system.tools.http_db import _is_ssrf_safe


def test_command_security_policy():
    assert _is_command_safe("echo hello") is True
    assert _is_command_safe("rm -rf /") is False
    assert _is_command_safe("mkfs.ext4 /dev/sdb") is False


def test_ssrf_security_policy():
    assert _is_ssrf_safe("http://169.254.169.254/latest/meta-data/") is False
    assert _is_ssrf_safe("http://metadata.google.internal/") is False
    assert _is_ssrf_safe("https://api.github.com/repos") is True


def test_api_health_and_agents_endpoints():
    client = TestClient(app)
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_agents = client.get("/api/v1/agents")
    assert res_agents.status_code == 200
    assert len(res_agents.json()["agents"]) >= 6


@pytest.mark.asyncio
async def test_end_to_end_real_task_execution():
    config = load_config("config/system_config.yaml")
    orc = Orchestrator(config=config)

    task_desc = "Perform a security audit of the repository, identify vulnerabilities, and report findings."
    state = await orc.run_async(task_desc)

    assert state.completed is True
    assert state.escalated is False
    assert state.final_output is not None
    assert len(state.traces) >= 2
    assert "Execution metrics" in state.final_output
