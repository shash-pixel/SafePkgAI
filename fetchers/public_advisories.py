"""Fetcher for publicly known package advisory notices."""

from typing import Any

import httpx

from config.settings import settings
from fetchers.base import PackageFetchError
from models.dependency_health import PublicAdvisoryNotice
from models.package import PackageEcosystem

_OSV_QUERY_URL = "https://api.osv.dev/v1/query"

_OSV_ECOSYSTEM_NAMES = {
    PackageEcosystem.PYPI: "PyPI",
    PackageEcosystem.NPM: "npm",
}


class PublicAdvisoryFetcher:
    """Retrieve public OSV notices for an exact package version."""

    async def fetch_notices(
        self,
        ecosystem: PackageEcosystem,
        package_name: str,
        version: str,
    ) -> list[PublicAdvisoryNotice]:
        """Return publicly known notices for one package version."""

        payload = {
            "package": {
                "name": package_name,
                "ecosystem": _OSV_ECOSYSTEM_NAMES[ecosystem],
            },
            "version": version,
        }

        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds,
            ) as client:
                response = await client.post(_OSV_QUERY_URL, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise PackageFetchError(
                "Could not retrieve public advisory notices."
            ) from error
        except httpx.RequestError as error:
            raise PackageFetchError(
                "Could not connect to the public advisory service."
            ) from error

        return self._to_notices(response.json())

    @staticmethod
    def _to_notices(payload: dict[str, Any]) -> list[PublicAdvisoryNotice]:
        """Normalize OSV response data into compact public-notice records."""

        notices: list[PublicAdvisoryNotice] = []

        for vulnerability in payload.get("vulns", []):
            advisory_id = vulnerability.get("id")

            if not isinstance(advisory_id, str):
                continue

            notices.append(
                PublicAdvisoryNotice(
                    advisory_id=advisory_id,
                    summary=vulnerability.get("summary"),
                    details_url=f"https://osv.dev/vulnerability/{advisory_id}",
                )
            )

        return notices