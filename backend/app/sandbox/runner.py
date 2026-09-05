"""
SovereignWorkbench — Sandbox Runner (app/sandbox/runner.py)
Executes LLM-generated Python math scripts in an isolated Bubblewrap (bwrap) namespace
or graceful local fallback with strict resource caps, filesystem whitelisting, and JSON output parsing.
"""

import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Optional, Dict, Any

from app.schemas import SandboxResult
from app.sandbox.error_parser import distill_python_traceback
from app.config import settings

logger = logging.getLogger(__name__)


def _set_resource_limits(mem_limit_mb: int):
    """Enforce strict memory caps (RLIMIT_AS) at the OS level via resource module."""
    try:
        import resource
        mem_bytes = int(mem_limit_mb * 1024 * 1024)
        # Limit total address space
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    except Exception as exc:
        logger.debug(f"Resource limit setting skipped: {exc}")


def _extract_json_from_stdout(stdout: str) -> Optional[Dict[str, Any]]:
    """Try parsing stdout as JSON, handling possible extra logging output."""
    cleaned = stdout.strip()
    if not cleaned:
        return None
        
    # Attempt direct parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
        
    # Attempt to locate JSON object substring {...}
    match = re.search(r"(\{.*\})", stdout, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
            
    return None


def execute_in_sandbox(
    code: str,
    timeout: int = 5,
    mem_limit_mb: int = 256
) -> SandboxResult:
    """
    Execute Python code inside an isolated, non-networked environment.
    
    Uses Linux Bubblewrap (bwrap) with strict minimal filesystem allowlist:
      - Unshared network (--unshare-net) and PID namespace (--unshare-pid)
      - Read-only whitelist for system binaries and virtualenv only
      - Host project files, uploads, and databases are strictly excluded
      - Memory limits enforced via OS resource caps (RLIMIT_AS)
    """
    bwrap_path = shutil.which("bwrap")
    preexec = (lambda: _set_resource_limits(mem_limit_mb)) if os.name == "posix" else None

    if bwrap_path:
        cmd = [
            bwrap_path,
            "--unshare-net",
            "--unshare-pid",
            "--dev", "/dev",
            "--proc", "/proc",
            "--tmpfs", "/tmp",
        ]
        # Whitelist essential system directories read-only
        system_dirs = ["/usr", "/lib", "/lib64", "/bin", "/etc"]
        for d in system_dirs:
            if Path(d).exists():
                cmd.extend(["--ro-bind", d, d])

        # Whitelist active Python virtualenv if outside standard /usr
        py_prefix = sys.prefix
        if py_prefix and not any(py_prefix.startswith(sd) for sd in system_dirs):
            if Path(py_prefix).exists():
                cmd.extend(["--ro-bind", py_prefix, py_prefix])

        cmd.extend([sys.executable, "-c", code])
    else:
        allow_fallback = getattr(settings, "ALLOW_UNSANDBOXED_FALLBACK", True)
        if not allow_fallback:
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="Security Policy Violation: Bubblewrap (bwrap) isolation runtime is required in strict mode.",
                distilled_error="Security Violation: bwrap sandbox runtime missing and fallback disabled.",
                parsed_output=None
            )
        logger.warning("[WARNING] bwrap not found, running with resource-capped standard subprocess")
        cmd = [sys.executable, "-c", code]
        
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            preexec_fn=preexec
        )
        
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        exit_code = result.returncode
        
        if exit_code == 0:
            parsed_output = _extract_json_from_stdout(stdout)
            return SandboxResult(
                success=True,
                exit_code=0,
                stdout=stdout,
                stderr=stderr,
                distilled_error=None,
                parsed_output=parsed_output
            )
        else:
            distilled = distill_python_traceback(stderr)
            return SandboxResult(
                success=False,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                distilled_error=distilled,
                parsed_output=None
            )
            
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if exc.stdout else ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        stderr = f"TimeoutError: Execution timed out after exceeding {timeout} seconds limit."
        distilled = (
            f"Runtime Error: TimeoutError: Execution exceeded {timeout}-second cap.\n"
            f"Offending code: [Execution Timeout]\n"
            f"Root cause: The script took too long to complete. Check for infinite loops or heavy calculations."
        )
        return SandboxResult(
            success=False,
            exit_code=124,
            stdout=stdout,
            stderr=stderr,
            distilled_error=distilled,
            parsed_output=None
        )
    except Exception as exc:
        stderr_msg = f"Internal Sandbox Execution Error: {str(exc)}"
        distilled = (
            f"Runtime Error: SubprocessError: {str(exc)}\n"
            f"Root cause: Subprocess execution failed unexpectedly."
        )
        return SandboxResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=stderr_msg,
            distilled_error=distilled,
            parsed_output=None
        )
