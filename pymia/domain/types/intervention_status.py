"""InterventionStatus — Estado de ciclo de vida de InterventionPlan."""

from enum import Enum


class InterventionStatus(Enum):
    """Estados permitidos de un plan de intervención."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
