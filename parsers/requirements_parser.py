"""Parser for Python requirements.txt files."""

import re

from models.manifest import (
    DependencyManifest,
    ManifestDependency,
    ManifestType,
)

_REQUIREMENT_PATTERN = re.compile(
    r"(?P<name>[A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(?P<constraint>.*)"
)


class RequirementsParser:
    """Parse direct dependencies declared in requirements.txt content."""

    def parse(
        self,
        content: str,
        source_name: str = "requirements.txt",
    ) -> DependencyManifest:
        """Return normalized dependencies from requirements.txt text."""

        dependencies: list[ManifestDependency] = []

        for raw_line in content.splitlines():
            line = raw_line.strip()

            if not line or line.startswith("#") or line.startswith("-"):
                continue

            package_requirement, separator, marker = line.partition(";")
            match = _REQUIREMENT_PATTERN.match(package_requirement.strip())

            if match is None:
                continue

            constraint = match.group("constraint").strip() or None
            if separator:
                constraint = f"{constraint}; {marker.strip()}" if constraint else marker.strip()

            dependencies.append(
                ManifestDependency(
                    name=match.group("name"),
                    version_constraint=constraint,
                    group="production",
                    raw_requirement=line,
                )
            )

        return DependencyManifest(
            manifest_type=ManifestType.REQUIREMENTS_TXT,
            source_name=source_name,
            dependencies=dependencies,
        )