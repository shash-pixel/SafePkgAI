"""Tests for manifest parser selection."""

import pytest

from core.manifest_parser_factory import (
    UnsupportedManifestError,
    get_manifest_parser,
)
from parsers.package_json_parser import PackageJsonParser
from parsers.requirements_parser import RequirementsParser


def test_returns_requirements_parser() -> None:
    """requirements.txt selects the Python dependency parser."""

    parser = get_manifest_parser("requirements.txt")

    assert isinstance(parser, RequirementsParser)


def test_returns_package_json_parser() -> None:
    """package.json selects the npm dependency parser."""

    parser = get_manifest_parser("package.json")

    assert isinstance(parser, PackageJsonParser)


def test_rejects_unsupported_manifest() -> None:
    """Unsupported filenames produce a clear error."""

    with pytest.raises(UnsupportedManifestError):
        get_manifest_parser("pyproject.toml")