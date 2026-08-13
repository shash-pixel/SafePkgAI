"""Parser for npm package.json files."""

import json

from models.manifest import (
    DependencyManifest,
    ManifestDependency,
    ManifestType,
)


class PackageJsonParser:
    """Parse direct dependencies declared in package.json content."""

    _DEPENDENCY_GROUPS = (
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
    )

    def parse(
        self,
        content: str,
        source_name: str = "package.json",
    ) -> DependencyManifest:
        """Return normalized dependencies from package.json text."""

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError("Invalid package.json content.") from error

        dependencies: list[ManifestDependency] = []

        for group in self._DEPENDENCY_GROUPS:
            group_dependencies = payload.get(group, {})

            if not isinstance(group_dependencies, dict):
                continue

            for name, version_constraint in group_dependencies.items():
                if not isinstance(version_constraint, str):
                    continue

                dependencies.append(
                    ManifestDependency(
                        name=name,
                        version_constraint=version_constraint,
                        group=group,
                        raw_requirement=f"{name}@{version_constraint}",
                    )
                )

        return DependencyManifest(
            manifest_type=ManifestType.PACKAGE_JSON,
            source_name=source_name,
            project_name=payload.get("name"),
            dependencies=dependencies,
        )