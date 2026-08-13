"""Central thresholds for deterministic package insights."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InsightThresholds:
    """Defines consistent boundaries for package maintenance observations."""

    recent_release_days: int = 180
    aging_release_days: int = 365
    stale_release_days: int = 730
    limited_release_history_count: int = 3


insight_thresholds = InsightThresholds()