"""npm metadata fetcher."""

""" Why: it implements the same fetcher contract as PyPI, so future orchestration does not need special-case logic."""

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


class NpmFetcher(PackageFetcher):
    """Fetch and normalize package metadata from the npm registry."""

    ecosystem = PackageEcosystem.NPM

    async def fetch_package(
        self,
        package_name: str,
        version: str | None = None,
    ) -> PackageMetadata:
        """Fetch npm metadata and select the requested or latest version."""

        url = build_package_metadata_url(self.ecosystem, package_name)

        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
        except httpx.RequestError as error:
            raise PackageFetchError(
                f"Could not connect to npm for package '{package_name}'."
            ) from error

        if response.status_code == httpx.codes.NOT_FOUND:
            raise PackageNotFoundError(
                f"npm package '{package_name}' was not found."
            )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise PackageFetchError(
                f"npm returned HTTP {response.status_code} for '{package_name}'."
            ) from error

        return self._to_package_metadata(response.json(), package_name, version)

    def _to_package_metadata(
        self,
        payload: dict[str, Any],
        package_name: str,
        requested_version: str | None,
    ) -> PackageMetadata:
        """Convert an npm registry payload into a normalized package model."""

        versions = payload.get("versions", {})
        latest_version = payload.get("dist-tags", {}).get("latest")

        if latest_version is None:
            raise PackageFetchError(
                f"npm did not provide a latest version for '{package_name}'."
            )

        resolved_version = requested_version or latest_version
        version_data = versions.get(resolved_version)

        if version_data is None:
            raise PackageNotFoundError(
                f"npm package '{package_name}' has no version '{resolved_version}'."
            )

        repository_url = self._get_repository_url(version_data.get("repository"))
        runtime_requirements = {
            key: value
            for key, value in version_data.get("engines", {}).items()
            if isinstance(value, str)
        }

        return PackageMetadata(
            reference=PackageReference(
                ecosystem=self.ecosystem,
                name=version_data.get("name", package_name),
                requested_version=requested_version,
            ),
            resolved_version=resolved_version,
            latest_available_version=latest_version,
            published_at=payload.get("time", {}).get(resolved_version),
            latest_published_at=payload.get("time", {}).get(latest_version),
            release_count=len(versions),
            summary=version_data.get("description"),
            description=version_data.get("description"),
            homepage_url=self._get_homepage_url(version_data.get("homepage")),
            repository_url=repository_url,
            runtime_requirements=runtime_requirements,
            dependencies=self._parse_dependencies(
                version_data.get("dependencies", {})
            ),
            keywords=version_data.get("keywords", []),
            deprecated_message=version_data.get("deprecated"),
        )

    @staticmethod
    def _parse_dependencies(
        dependencies: dict[str, str],
    ) -> list[PackageDependency]:
        """Convert npm dependency mapping into normalized dependency records."""

        return [
            PackageDependency(
                name=name,
                version_constraint=constraint,
                raw_requirement=f"{name}@{constraint}",
            )
            for name, constraint in dependencies.items()
        ]

    @staticmethod
    def _get_repository_url(repository: str | dict[str, Any] | None) -> str | None:
        """Normalize npm repository data into a URL when available."""

        if isinstance(repository, str):
            return repository

        if isinstance(repository, dict):
            url = repository.get("url")
            return url if isinstance(url, str) else None

        return None

    @staticmethod
    def _get_homepage_url(homepage: object) -> str | None:
        """Return a homepage only when npm provides a string URL."""

        return homepage if isinstance(homepage, str) else None