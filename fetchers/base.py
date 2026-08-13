"""Shared interfaces and errors for package registry fetchers."""

from abc import ABC, abstractmethod

from models.package import PackageMetadata


class PackageFetchError(RuntimeError):
    """Raised when package metadata cannot be retrieved."""


class PackageNotFoundError(PackageFetchError):
    """Raised when a requested package or version does not exist."""


class PackageFetcher(ABC):
    """Defines the contract for ecosystem-specific metadata fetchers."""

    @abstractmethod
    async def fetch_package(
        self,
        package_name: str,
        version: str | None = None,
    ) -> PackageMetadata:
        """Fetch normalized metadata for one package."""