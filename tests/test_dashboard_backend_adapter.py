"""Tests for the dashboard's thin backend adapter."""

import pytest

from dashboard.backend_adapter import DashboardInputError, _validate_manifest_filename
from dashboard.app import group_recommended_actions


def test_accepts_supported_manifest_names() -> None:
    assert _validate_manifest_filename("requirements.txt") == "requirements.txt"
    assert _validate_manifest_filename("package.json") == "package.json"


def test_rejects_invalid_manifest_names() -> None:
    with pytest.raises(DashboardInputError):
        _validate_manifest_filename("../requirements.txt")
    with pytest.raises(DashboardInputError):
        _validate_manifest_filename("dependencies.txt")


def test_groups_repeated_update_actions() -> None:
    actions = [
        "Review an update to Flask 3.1.3 and confirm compatibility before changing the project dependency.",
        "Review an update to pandas 3.0.5 and confirm compatibility before changing the project dependency.",
        "Replace the deprecated package after reviewing its migration notes.",
    ]

    assert group_recommended_actions(actions) == [
        "Review available updates and confirm compatibility before changing project dependencies: Flask 3.1.3, pandas 3.0.5.",
        "Replace the deprecated package after reviewing its migration notes.",
    ]
