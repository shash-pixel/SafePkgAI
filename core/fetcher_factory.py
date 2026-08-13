"""Factory for selecting the correct package registry fetcher."""

from fetchers.base import PackageFetcher
from fetchers.npm import NpmFetcher
from fetchers.pypi import PyPIFetcher
from models.package import PackageEcosystem


def get_fetcher(ecosystem: PackageEcosystem) -> PackageFetcher:
    """Return the fetcher that supports the requested ecosystem."""

    fetchers: dict[PackageEcosystem, PackageFetcher] = {
        PackageEcosystem.PYPI: PyPIFetcher(),
        PackageEcosystem.NPM: NpmFetcher(),
    }

    return fetchers[ecosystem]