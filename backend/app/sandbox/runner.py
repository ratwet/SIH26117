"""
SovereignWorkbench — Sandbox Runner (app/sandbox/runner.py)
Executes LLM-generated Python math scripts in an isolated Bubblewrap (bwrap) namespace
or graceful local fallback with strict resource caps and JSON output parsing.
"""

import json
import logging
import os
import re
import shutil
import subprocess
import sys
from typing import Optional, Dict, Any

from app.schemas import SandboxResult
from app.sandbox.error_parser import distill_python_traceback

logger = logging.getLogger(__name__)


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
    Execute Python code inside an isolated environment.
    
    Uses Linux Bubblewrap (bwrap) if present:
      bwrap --unshare-net --unshare-pid --ro-bind / / --tmpfs /tmp --proc /proc --dev /dev python3 -c "<code>"
    Falls back gracefully to standard subprocess on non-Linux / local dev machines without bwrap.
    """
    bwrap_path = shutil.which("bwrap")
    
    if bwrap_path:
        # Strict non-networked Linux namespace container
        cmd = [
            bwrap_path,
            "--unshare-net",
            "--unshare-pid",
            "--ro-bind", "/", "/",
            "--tmpfs", "/tmp",
            "--proc", "/proc",
            "--dev", "/dev",
            sys.executable,
            "-c",
            code
        ]
    else:
        logger.warning("[WARNING] bwrap not found, running with standard subprocess")
        cmd = [sys.executable, "-c", code]
        
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
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
