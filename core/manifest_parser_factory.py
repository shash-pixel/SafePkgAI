## Its job is to select the correct existing parser based on the manifest version and other criteria.
## requirements.txt → RequirementsParser
## package.json     → PackageJsonParser

"""Factory for selecting a dependency manifest parser."""

from pathlib import Path

from parsers.package_json_parser import PackageJsonParser
from parsers.requirements_parser import RequirementsParser


class UnsupportedManifestError(ValueError):
    """Raised when a file is not a supported dependency manifest."""


def get_manifest_parser(
    source_path: str | Path,
) -> RequirementsParser | PackageJsonParser:
    """Return the parser for a supported manifest filename."""

    filename = Path(source_path).name.lower()

    if filename == "requirements.txt":
        return RequirementsParser()

    if filename == "package.json":
        return PackageJsonParser()

    raise UnsupportedManifestError(
        "Supported manifest files are requirements.txt and package.json."
    )