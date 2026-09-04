"""
SovereignWorkbench — Shared Pytest Fixtures (tests/conftest.py)
Configures test isolation and enables synthetic contract mode for offline CI runs.
"""

import pytest
from app.config import settings


@pytest.fixture(autouse=True)
def enable_test_synthetic_mode(monkeypatch):
    """
    By default in unit/integration test runs where no GPU cluster is active,
    allow emulation fallback so compiler and state-machine tests verify deterministically.
    Tests specifically checking that the engine refuses to run without a model
    can explicitly set monkeypatch.setattr(settings, 'ALLOW_EMULATION', False).
    """
    monkeypatch.setattr(settings, "ALLOW_EMULATION", True)
