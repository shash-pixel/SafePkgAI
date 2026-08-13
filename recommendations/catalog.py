"""Small curated catalog of comparable package alternatives."""

from models.package import PackageEcosystem
from models.recommendation import AlternativeCandidate

_CATALOG: dict[
    tuple[PackageEcosystem, str],
    list[AlternativeCandidate],
] = {
    (PackageEcosystem.PYPI, "requests"): [
        AlternativeCandidate(
            name="httpx",
            ecosystem=PackageEcosystem.PYPI,
            description="Modern HTTP client offering synchronous and asynchronous APIs.",
        ),
        AlternativeCandidate(
            name="aiohttp",
            ecosystem=PackageEcosystem.PYPI,
            description="Asynchronous HTTP client and server framework.",
        ),
    ],
    (PackageEcosystem.PYPI, "httpx"): [
        AlternativeCandidate(
            name="requests",
            ecosystem=PackageEcosystem.PYPI,
            description="Widely used synchronous HTTP client.",
        ),
        AlternativeCandidate(
            name="aiohttp",
            ecosystem=PackageEcosystem.PYPI,
            description="Asynchronous HTTP client and server framework.",
        ),
    ],
    (PackageEcosystem.PYPI, "flask"): [
        AlternativeCandidate(
            name="fastapi",
            ecosystem=PackageEcosystem.PYPI,
            description="Type-hint-oriented API framework with async support.",
        ),
        AlternativeCandidate(
            name="django",
            ecosystem=PackageEcosystem.PYPI,
            description="Full-stack Python web framework with built-in components.",
        ),
    ],
    (PackageEcosystem.NPM, "axios"): [
        AlternativeCandidate(
            name="got",
            ecosystem=PackageEcosystem.NPM,
            description="Feature-rich HTTP request library for Node.js.",
        ),
        AlternativeCandidate(
            name="undici",
            ecosystem=PackageEcosystem.NPM,
            description="High-performance HTTP client for Node.js.",
        ),
    ],
    (PackageEcosystem.NPM, "express"): [
        AlternativeCandidate(
            name="fastify",
            ecosystem=PackageEcosystem.NPM,
            description="Performance-oriented Node.js web framework.",
        ),
        AlternativeCandidate(
            name="koa",
            ecosystem=PackageEcosystem.NPM,
            description="Minimal middleware-focused Node.js web framework.",
        ),
    ],
}


def get_alternative_candidates(
    ecosystem: PackageEcosystem,
    package_name: str,
) -> list[AlternativeCandidate]:
    """Return curated alternatives for a known package, if available."""

    catalog_key = (ecosystem, package_name.strip().lower())
    return _CATALOG.get(catalog_key, [])