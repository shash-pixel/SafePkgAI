"""PyPI metadata fetcher."""


### This revision populates the new version and runtime fields.###

import re
from typing import Any

import httpx

from config.package_sources import build_package_metadata_url
from config.settings import settings
from fetchers.base import PackageFetchError, PackageFetcher, PackageNotFoundError
from models.package import (
    PackageDependency,
    PackageEcosystem,
    PackageMetadata,
    PackageReference,
)

_REQUIREMENT_PATTERN = re.compile(
    r"(?P<name>[A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(?P<constraint>.*)"
)


class PyPIFetcher(PackageFetcher):
    """Fetch and normalize package metadata from the PyPI JSON API."""

    ecosystem = PackageEcosystem.PYPI

    @staticmethod
    def _get_license_name(license_value: object) -> str | None:
        """Return a usable PyPI license label when one is published."""

        if isinstance(license_value, str) and license_value.strip():
            return license_value.strip()

        return None

    async def fetch_package(
        self,
        package_name: str,
        version: str | None = None,
    ) -> PackageMetadata:
        """Fetch one PyPI package, optionally at a specific version."""

        url = build_package_metadata_url(self.ecosystem, package_name, version)

        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
        except httpx.RequestError as error:
            raise PackageFetchError(
                f"Could not connect to PyPI for package '{package_name}'."
            ) from error

        if response.status_code == httpx.codes.NOT_FOUND:
            raise PackageNotFoundError(
                f"PyPI package '{package_name}' was not found."
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise PackageFetchError(
                f"PyPI returned HTTP {response.status_code} for '{package_name}'."
            ) from error

        return self._to_package_metadata(response.json(), package_name, version)

    def _to_package_metadata(
        self,
        payload: dict[str, Any],
        package_name: str,
        requested_version: str | None,
    ) -> PackageMetadata:
        """Convert a PyPI API payload into a normalized package model."""

        info = payload["info"]
        license_name = self._get_license_name(info.get("license"))

        releases = payload.get("releases", {})
        resolved_version = info["version"]

        runtime_requirements = {}
        if info.get("requires_python"):
            runtime_requirements["python"] = info["requires_python"]

        return PackageMetadata(
            reference=PackageReference(
                ecosystem=self.ecosystem,
                name=info.get("name", package_name),
                requested_version=requested_version,
            ),
            resolved_version=resolved_version,
            latest_available_version=resolved_version,
            published_at=self._get_publish_time(releases, resolved_version),
            latest_published_at=self._get_latest_publish_time(releases),
            release_count=len(releases),
            summary=info.get("summary"),
            description=info.get("description"),
            homepage_url=info.get("home_page"),
            repository_url=self._get_repository_url(info.get("project_urls")),
            license_name=license_name,
            runtime_requirements=runtime_requirements,
            dependencies=self._parse_dependencies(info.get("requires_dist") or []),
            classifiers=info.get("classifiers") or [],
            keywords=self._parse_keywords(info.get("keywords")),
        )

    @staticmethod
    def _get_publish_time(
        releases: dict[str, list[dict[str, Any]]],
        version: str,
    ) -> str | None:
        """Return the newest upload time for one package version."""

        timestamps = [
            file_info["upload_time_iso_8601"]
            for file_info in releases.get(version, [])
            if file_info.get("upload_time_iso_8601")
        ]

        return max(timestamps, default=None)

    @staticmethod
    def _get_latest_publish_time(
        releases: dict[str, list[dict[str, Any]]],
    ) -> str | None:
        """Return the newest upload time across all package releases."""

        timestamps = [
            file_info["upload_time_iso_8601"]
            for release_files in releases.values()
            for file_info in release_files
            if file_info.get("upload_time_iso_8601")
        ]

        return max(timestamps, default=None)

    @staticmethod
    def _get_repository_url(project_urls: dict[str, str] | None) -> str | None:
        """Select a source repository URL when PyPI publishes one."""

        if not project_urls:
            return None

        for label, url in project_urls.items():
            if label.lower() in {"repository", "source", "source code"}:
                return url

        return None

    @staticmethod
    def _parse_dependencies(
        requirements: list[str],
    ) -> list[PackageDependency]:
        """Convert PyPI requirement strings into structured dependencies."""

        dependencies: list[PackageDependency] = []

        for requirement in requirements:
            package_requirement, separator, marker = requirement.partition(";")
            match = _REQUIREMENT_PATTERN.match(package_requirement.strip())

            if match is None:
                dependencies.append(
                    PackageDependency(
                        name=package_requirement.strip(),
                        raw_requirement=requirement,
                    )
                )
                continue

            dependencies.append(
                PackageDependency(
                    name=match.group("name"),
                    version_constraint=match.group("constraint").strip() or None,
                    environment_marker=marker.strip() if separator else None,
                    raw_requirement=requirement,
                )
            )

        return dependencies

    @staticmethod
    def _parse_keywords(keywords: str | None) -> list[str]:
        """Normalize PyPI's comma-separated keywords value."""

        if not keywords:
            return []

        return [keyword.strip() for keyword in keywords.split(",") if keyword.strip()]