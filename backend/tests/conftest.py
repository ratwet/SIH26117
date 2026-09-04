"""
SovereignWorkbench — Shared Pytest Fixtures (tests/conftest.py)
Configures test isolation and enables synthetic contract mode for offline CI runs.
"""

import pytest
from app.config import settings
from app.security import network_monitor


@pytest.fixture(autouse=True)
def enable_test_synthetic_mode(monkeypatch):
    """
    By default in unit/integration test runs:
    1. Allow synthetic test LLM contract so compilers and state graphs verify offline.
    2. Mock check_wan_reachability to False by default so unit tests simulate clean air-gapped refinery LAN.
    """
    monkeypatch.setattr(settings, "ALLOW_EMULATION", True)
    monkeypatch.setattr(network_monitor, "check_wan_reachability", lambda timeout=0.4: False)

