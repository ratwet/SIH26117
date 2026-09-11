"""SovereignWorkbench — Enterprise On-Premise Connectors."""
from .email_connector import (
    create_inspection_email_draft,
    approve_and_dispatch_email,
    get_email_draft,
    compute_draft_payload_hash,
)

__all__ = [
    "create_inspection_email_draft",
    "approve_and_dispatch_email",
    "get_email_draft",
    "compute_draft_payload_hash",
]
