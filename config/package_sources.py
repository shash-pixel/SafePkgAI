"""Package registry URL builders."""

from urllib.parse import quote

from models.package import PackageEcosystem

PYPI_REGISTRY_URL = "https://pypi.org/pypi"
NPM_REGISTRY_URL = "https://registry.npmjs.org"


def build_package_metadata_url(
    ecosystem: PackageEcosystem,
    package_name: str,
    version: str | None = None,
) -> str:
    """Build a registry metadata URL for a package and optional version."""

    encoded_name = quote(package_name, safe="@")

    if ecosystem is PackageEcosystem.PYPI:
        base_url = f"{PYPI_REGISTRY_URL}/{encoded_name}"
    else:
        base_url = f"{NPM_REGISTRY_URL}/{encoded_name}"

    if version is None:
        return f"{base_url}/json" if ecosystem is PackageEcosystem.PYPI else base_url

    encoded_version = quote(version, safe="")
    return (
        f"{base_url}/{encoded_version}/json"
        if ecosystem is PackageEcosystem.PYPI
        else f"{base_url}/{encoded_version}"
    )