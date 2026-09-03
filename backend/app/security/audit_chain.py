"""
SovereignWorkbench — Cryptographic Audit Chain (app/security/audit_chain.py)
Maintains an immutable, append-only SHA-256 hash chain in SQLite (mrpl_audit.db)
for tamper-proof statutory audit trails.
"""

import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from app.config import settings
from app.schemas import AuditEvent

GENESIS_HASH = "0" * 64


def _get_db_connection() -> sqlite3.Connection:
    """Get SQLite connection and ensure table exists."""
    settings.AUDIT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.AUDIT_DB_PATH))
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE,
                timestamp TEXT NOT NULL,
                user_role TEXT NOT NULL,
                model_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                prompt_hash TEXT NOT NULL,
                tool_exit_code INTEGER NOT NULL,
                output_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            )
        """)
    return conn


def _compute_entry_hash(
    previous_hash: str,
    timestamp: str,
    user_role: str,
    prompt_hash: str,
    output_hash: str
) -> str:
    """Compute SHA-256 digest of block contents."""
    raw_payload = f"{previous_hash}{timestamp}{user_role}{prompt_hash}{output_hash}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def record_audit_event(event: AuditEvent) -> str:
    """
    Append an immutable event to the cryptographic audit chain.
    
    Args:
        event: AuditEvent payload.
        
    Returns:
        str: Computed entry_hash for the newly appended ledger record.
    """
    conn = _get_db_connection()
    try:
        with conn:
            # 1. Fetch previous hash
            cursor = conn.execute("SELECT entry_hash FROM audit_ledger ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            previous_hash = row["entry_hash"] if row else GENESIS_HASH
            
            # 2. Populate timestamps and ids if not present
            timestamp = event.timestamp or datetime.now(timezone.utc).isoformat()
            event_id = event.event_id or str(uuid.uuid4())
            
            # 3. Compute entry hash
            entry_hash = _compute_entry_hash(
                previous_hash=previous_hash,
                timestamp=timestamp,
                user_role=event.user_role,
                prompt_hash=event.prompt_hash,
                output_hash=event.output_hash
            )
            
            # 4. Insert into append-only table
            conn.execute("""
                INSERT INTO audit_ledger (
                    event_id, timestamp, user_role, model_id, task_type,
                    prompt_hash, tool_exit_code, output_hash, previous_hash, entry_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, timestamp, event.user_role, event.model_id, event.task_type,
                event.prompt_hash, event.tool_exit_code, event.output_hash, previous_hash, entry_hash
            ))
            
            # Update incoming object
            event.event_id = event_id
            event.timestamp = timestamp
            event.previous_hash = previous_hash
            event.entry_hash = entry_hash
            
            return entry_hash
    finally:
        conn.close()


def verify_audit_chain() -> Tuple[bool, str, int]:
    """
    Verify the cryptographic integrity of the entire audit chain.
    
    Returns:
        Tuple[bool, str, int]: (is_valid, status_message, total_blocks_verified)
    """
    conn = _get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM audit_ledger ORDER BY id ASC")
        rows = cursor.fetchall()
        
        if not rows:
            return True, "Audit ledger is empty (Genesis state).", 0
            
        expected_prev = GENESIS_HASH
        for idx, row in enumerate(rows):
            # Check previous hash link
            if row["previous_hash"] != expected_prev:
                return False, f"Broken link at block #{row['id']}: expected prev {expected_prev}, got {row['previous_hash']}", idx
                
            # Recompute entry hash
            computed_hash = _compute_entry_hash(
                previous_hash=row["previous_hash"],
                timestamp=row["timestamp"],
                user_role=row["user_role"],
                prompt_hash=row["prompt_hash"],
                output_hash=row["output_hash"]
            )
            if computed_hash != row["entry_hash"]:
                return False, f"Tampered block #{row['id']}: stored {row['entry_hash']} does not match computed {computed_hash}", idx
                
            expected_prev = row["entry_hash"]
            
        return True, f"All {len(rows)} blocks cryptographically verified and intact.", len(rows)
    finally:
        conn.close()


def get_audit_ledger(limit: int = 50) -> List[AuditEvent]:
    """Retrieve recent audit records from the ledger."""
    conn = _get_db_connection()
    try:
        cursor = conn.execute("SELECT * FROM audit_ledger ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        records = []
        for r in rows:
            records.append(AuditEvent(
                event_id=r["event_id"],
                timestamp=r["timestamp"],
                user_role=r["user_role"],
                model_id=r["model_id"],
                task_type=r["task_type"],
                prompt_hash=r["prompt_hash"],
                tool_exit_code=r["tool_exit_code"],
                output_hash=r["output_hash"],
                previous_hash=r["previous_hash"],
                entry_hash=r["entry_hash"]
            ))
        return records
    finally:
        conn.close()
