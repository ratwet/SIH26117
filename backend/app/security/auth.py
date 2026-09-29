"""
Aquanex - Sovereign On-Premise Authentication & RBAC User Registry (app/security/auth.py)
Zero Cloud Dependencies • 100% Air-Gapped • Local In-Memory & File Store
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class UserAccount(BaseModel):
    id: str
    username: str
    name: str
    role: str  # "admin" | "senior" | "junior"
    avatar: str
    pin: str
    allowed_models: List[str]
    default_model: str
    description: str


# Pre-seeded Refinery Personnel for Smart India Hackathon (SIH26117 / MRPL)
DEFAULT_USERS: Dict[str, UserAccount] = {
    "usr_admin": UserAccount(
        id="usr_admin",
        username="admin",
        name="Rajat",
        role="admin",
        avatar="👑",
        pin="1170",
        allowed_models=["*"],
        default_model="Enterprise-100B",
        description="IT Systems Administrator • Level 1 Governance & Model Gatekeeper",
    ),
    "usr_senior": UserAccount(
        id="usr_senior",
        username="senior",
        name="Anand",
        role="senior",
        avatar="📐",
        pin="5700",
        allowed_models=["Enterprise-100B", "Workstation-32B", "Edge-8B"],
        default_model="Workstation-32B",
        description="Senior Reliability Lead • Level 2 Statutory Approval & Model Switcher",
    ),
    "usr_junior": UserAccount(
        id="usr_junior",
        username="junior",
        name="Naveen",
        role="junior",
        avatar="👷",
        pin="2026",
        allowed_models=["Edge-8B"],
        default_model="Edge-8B",
        description="Field Technician • Level 3 Pre-configured Inspection Operator",
    ),
}

# Runtime mutable registry for on-premise model access configuration
_USERS_REGISTRY: Dict[str, UserAccount] = {k: v.model_copy() for k, v in DEFAULT_USERS.items()}


def get_all_users() -> List[UserAccount]:
    """Returns all registered users in the refinery."""
    return list(_USERS_REGISTRY.values())


def get_user_by_id(user_id: str) -> Optional[UserAccount]:
    """Looks up user by ID."""
    return _USERS_REGISTRY.get(user_id)


def get_user_by_username(username: str) -> Optional[UserAccount]:
    """Looks up user by username."""
    u_lower = username.strip().lower()
    for user in _USERS_REGISTRY.values():
        if user.username.lower() == u_lower or user.role.lower() == u_lower:
            return user
    return None


def authenticate_user(username: str, pin: Optional[str] = None) -> Optional[UserAccount]:
    """
    Authenticates user against on-premise personnel registry.
    If PIN is provided, validates exact PIN match.
    If PIN is empty/None, supports instant persona switching for hackathon jury convenience.
    """
    user = get_user_by_username(username)
    if not user:
        return None
    if pin is not None and pin.strip() != "":
        if user.pin != pin.strip():
            return None
    return user


def update_user_allowed_models(user_id: str, allowed_models: List[str]) -> Optional[UserAccount]:
    """
    Updates the list of models an individual user/role is authorized to invoke.
    Invoked exclusively by the IT Systems Administrator.
    """
    if user_id not in _USERS_REGISTRY:
        return None
    user = _USERS_REGISTRY[user_id]
    user.allowed_models = allowed_models
    # If default model is no longer in allowed list, update default model
    if "*" not in allowed_models and user.default_model not in allowed_models:
        if allowed_models:
            user.default_model = allowed_models[0]
        else:
            user.default_model = "Edge-8B"
    return user


def is_model_authorized_for_user(user: UserAccount, model_name: str) -> bool:
    """Verifies whether a specific model or tier is authorized for the given user."""
    if "*" in user.allowed_models or user.role == "admin":
        return True
    
    # Normalize comparison (case-insensitive substring match)
    m_lower = model_name.lower().replace("-", "").replace("_", "")
    for allowed in user.allowed_models:
        a_lower = allowed.lower().replace("-", "").replace("_", "")
        if a_lower in m_lower or m_lower in a_lower:
            return True
    return False
