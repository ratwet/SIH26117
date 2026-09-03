"""
SovereignWorkbench — Error Distiller (app/sandbox/error_parser.py)
Distills noisy Python tracebacks into concise 2-3 line root-cause summaries
suitable for LLM self-healing loops.
"""

import re
from typing import Optional, Tuple


def _diagnose_root_cause(exc_type: str, exc_msg: str, offending_code: Optional[str]) -> str:
    """Generate helpful heuristic root-cause guidance for LLM code repair."""
    exc_type_lower = exc_type.lower()
    
    if "zerodivision" in exc_type_lower:
        if offending_code and "/" in offending_code:
            parts = offending_code.split("/")
            denominator = parts[-1].strip()
            return f"Denominator ({denominator}) evaluated to 0.0. Add a safety check before dividing (e.g., if corrosion_rate > 0: ...)."
        return "Division by zero occurred. Add a safety check to verify denominator is strictly greater than 0 before division."
        
    elif "keyerror" in exc_type_lower:
        key_match = re.search(r"['\"](.*?)['\"]", exc_msg)
        key = key_match.group(1) if key_match else exc_msg
        return f"Key '{key}' not found in dictionary. Verify the input data schema or use dict.get('{key}', default)."
        
    elif "nameerror" in exc_type_lower:
        name_match = re.search(r"name ['\"](.*?)['\"]", exc_msg)
        name = name_match.group(1) if name_match else exc_msg
        return f"Identifier '{name}' is not defined. Ensure it is initialized, correctly spelled, or imported."
        
    elif "typeerror" in exc_type_lower:
        if "unsupported operand" in exc_msg:
            return f"Incompatible types used in operator: {exc_msg}. Ensure variables are cast to float/int before math operations."
        elif "positional argument" in exc_msg or "unexpected keyword" in exc_msg:
            return f"Function signature mismatch: {exc_msg}. Verify function arguments."
        return f"Type mismatch: {exc_msg}. Check data types."
        
    elif "valueerror" in exc_type_lower:
        return f"Invalid value encountered: {exc_msg}. Check parameter bounds and conversion logic."
        
    elif "indexerror" in exc_type_lower:
        return "List or array index out of bounds. Verify sequence length before indexing."
        
    elif "syntaxerror" in exc_type_lower:
        return f"Python syntax error: {exc_msg}. Check matching parentheses, colons, and valid operators."
        
    elif "indentationerror" in exc_type_lower:
        return f"Indentation error: {exc_msg}. Ensure consistent 4-space indentation throughout the script."
        
    elif "timeouterror" in exc_type_lower or "timeout" in exc_type_lower:
        return "Execution timed out. Check for infinite loops or reduce algorithmic complexity."
        
    return f"Execution failed due to {exc_type}: {exc_msg}."


def distill_python_traceback(raw_stderr: str) -> str:
    """
    Distill noisy 50-line Python tracebacks into clean 2-3 line root-cause summaries.
    
    Returns structured string:
    Runtime Error on line <N>: <ExceptionType>: <message>
    Offending code: <code line>
    Root cause: <diagnostic guidance>
    """
    if not raw_stderr or not raw_stderr.strip():
        return "Execution failed with unknown error (empty stderr)."
        
    lines = [line.strip() for line in raw_stderr.strip().splitlines() if line.strip()]
    
    # 1. Identify exception type and message (typically the last line)
    exc_type = "RuntimeError"
    exc_msg = ""
    for line in reversed(lines):
        # Match standard ExceptionName: message
        match = re.match(r"^([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Interrupt|Exit|Warning)):?\s*(.*)$", line)
        if match:
            exc_type = match.group(1)
            exc_msg = match.group(2).strip()
            break
    if not exc_msg and lines:
        exc_msg = lines[-1]
        
    # 2. Extract line number and offending code
    line_num: Optional[int] = None
    offending_code: Optional[str] = None
    
    # Traceback lines format: File "<string>", line 18, in <module>
    file_matches = list(re.finditer(r'File\s+["\'].*?["\'],\s+line\s+(\d+)(?:,\s+in\s+(.+))?', raw_stderr))
    if file_matches:
        last_match = file_matches[-1]
        line_num = int(last_match.group(1))
        
        # Offending code is usually the line following the File match in standard tracebacks
        match_end = last_match.end()
        after_text = raw_stderr[match_end:]
        after_lines = [l.strip() for l in after_text.splitlines() if l.strip()]
        if after_lines and not re.match(r"^[A-Z][a-zA-Z0-9_]*(?:Error|Exception)", after_lines[0]):
            offending_code = after_lines[0]
            
    # 3. Generate diagnostic guidance
    root_cause = _diagnose_root_cause(exc_type, exc_msg, offending_code)
    
    # 4. Assemble clean summary
    summary_parts = []
    if line_num is not None:
        summary_parts.append(f"Runtime Error on line {line_num}: {exc_type}: {exc_msg}")
    else:
        summary_parts.append(f"Runtime Error: {exc_type}: {exc_msg}")
        
    if offending_code:
        summary_parts.append(f"Offending code: {offending_code}")
        
    summary_parts.append(f"Root cause: {root_cause}")
    
    return "\n".join(summary_parts)
