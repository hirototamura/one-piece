"""Actor boundary checks — mirrors packages/domain AgentScopePolicy."""

from enum import Enum
from typing import Literal

ActorKind = Literal["human_engineer", "logic_automation", "ai_agent"]
CriticalityTier = Literal["critical", "standard", "derived"]
MutableNodeKind = Literal[
    "requirement",
    "design_parameter",
    "design_constraint",
    "interface_parameter",
    "icd",
]


class ActorKindEnum(str, Enum):
    HUMAN = "human_engineer"
    LOGIC = "logic_automation"
    AI = "ai_agent"


def can_actor_mutate(
    actor: ActorKind,
    node_kind: MutableNodeKind,
    criticality: CriticalityTier,
    *,
    ai_allowed_fraction: float = 0.2,
    ai_blocked_tiers: tuple[CriticalityTier, ...] = ("critical",),
    ai_allowed_kinds: tuple[MutableNodeKind, ...] = ("design_parameter",),
) -> bool:
    """Return True if actor may mutate the node under policy defaults (~20% AI scope)."""
    if actor == "human_engineer":
        return True
    if actor == "logic_automation":
        return criticality != "critical" or node_kind == "design_parameter"
    if actor == "ai_agent":
        if ai_allowed_fraction <= 0:
            return False
        if criticality in ai_blocked_tiers:
            return False
        if node_kind not in ai_allowed_kinds:
            return False
        return ai_allowed_fraction > 0
    return False
