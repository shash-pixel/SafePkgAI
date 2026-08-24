// SafePkg AI Frontend - Mock Data Database
// Declared on window.SafePkgMockData for easy cross-module access.

window.SafePkgMockData = (function() {
    const manifests = {
        "requirements.txt": {
            name: "requirements.txt",
            type: "pip",
            size: "2.4 KB",
            score: 75,
            level: "Review Recommended",
            levelColor: "amber",
            date: "Today at 09:41 AM",
            stats: {
                attention: 2,
                updates: 5,
                notices: 0,
                total: 7
            },
            dependencies: [
                { package: "httpx", current: "0.24.1", latest: "0.27.0", score: 85, width: "85%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "pydantic", current: "2.1.1", latest: "2.6.4", score: 60, width: "60%", status: "Review Recommended", statusClass: "bg-[#FEF3C7] text-[#B45309]", barColor: "bg-[#B45309]" },
                { package: "streamlit", current: "1.25.0", latest: "1.32.0", score: 92, width: "92%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "requests", current: "2.28.1", latest: "2.31.0", score: 78, width: "78%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "numpy", current: "1.22.0", latest: "1.26.4", score: 55, width: "55%", status: "Review Recommended", statusClass: "bg-[#FEF3C7] text-[#B45309]", barColor: "bg-[#B45309]" },
                { package: "django", current: "4.1.0", latest: "5.0.3", score: 80, width: "80%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "pytest", current: "7.2.0", latest: "8.0.2", score: 88, width: "88%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" }
            ],
            aiAnalysis: {
                available: true,
                summary: "The Python environment is generally stable, but multiple core packages are trailing significantly behind upstream releases. There are no critical CVEs detected in the current lockfile.",
                highlights: [
                    "<code>pydantic</code> major version divergence detected (v2.1 to v2.6). High risk of breaking changes in validation logic.",
                    "<code>httpx</code> update available; includes performance improvements for async connection pooling."
                ],
                recommendations: [
                    {
                        title: "Review Pydantic Migration Guide",
                        description: "Assess impact before upgrading to 2.6.4 to prevent schema validation failures."
                    },
                    {
                        title: "Upgrade Numpy Component",
                        description: "Numpy version 1.22.0 has known deprecations. Upgrading to 1.26.4 is recommended to improve compatibility with newer Python features."
                    }
                ]
            }
        },
        "package.json": {
            name: "package.json",
            type: "npm",
            size: "1.8 KB",
            score: 88,
            level: "Healthy",
            levelColor: "green",
            date: "Today at 10:15 AM",
            stats: {
                attention: 1,
                updates: 3,
                notices: 1,
                total: 9
            },
            dependencies: [
                { package: "react", current: "18.2.0", latest: "18.3.1", score: 95, width: "95%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "react-dom", current: "18.2.0", latest: "18.3.1", score: 95, width: "95%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "lodash", current: "4.17.15", latest: "4.17.21", score: 40, width: "40%", status: "Critical", statusClass: "bg-[#FEE2E2] text-[#991B1B]", barColor: "bg-[#EF4444]" },
                { package: "typescript", current: "5.0.4", latest: "5.3.3", score: 90, width: "90%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "vite", current: "4.3.9", latest: "5.1.4", score: 85, width: "85%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "tailwindcss", current: "3.3.2", latest: "3.4.1", score: 98, width: "98%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "express", current: "4.18.2", latest: "4.19.2", score: 88, width: "88%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "next", current: "13.4.4", latest: "14.1.0", score: 78, width: "78%", status: "Healthy", statusClass: "bg-[#D1FAE5] text-[#065F46]", barColor: "bg-[#065F46]" },
                { package: "eslint", current: "8.40.0", latest: "8.56.0", score: 72, width: "72%", status: "Review Recommended", statusClass: "bg-[#FEF3C7] text-[#B45309]", barColor: "bg-[#B45309]" }
            ],
            aiAnalysis: {
                available: true,
                summary: "The web project has high-quality, up-to-date framework dependencies. However, it contains a critical vulnerability in `lodash` which needs instant mitigation.",
                highlights: [
                    "<code>lodash</code> at 4.17.15 has a prototype pollution advisory. Update to 4.17.21 immediately.",
                    "Framework core components (<code>react</code>, <code>typescript</code>) are healthy and aligned with recent patch updates."
                ],
                recommendations: [
                    {
                        title: "Patch Lodash Vulnerability",
                        description: "Upgrade lodash dependency to version 4.17.21 or above to prevent Prototype Pollution exploits."
                    }
                ]
            }
        }
    };

    const packages = {
        "google-genai": {
            name: "google-genai",
            description: "Google GenAI SDK for Python",
            score: 95,
            status: "Healthy",
            statusClass: "bg-[#D1FAE5] text-[#065F46]",
            ecosystem: "Python",
            requested: "0.3.0",
            latest: "0.4.0",
            license: "Apache-2.0",
            repository: "https://github.com/googleapis/python-genai",
            homepage: "https://pypi.org/project/google-genai/",
            requirements: [
                { name: "pydantic", spec: ">=2.0.0" },
                { name: "requests", spec: ">=2.31.0" },
                { name: "typing-extensions", spec: ">=4.5.0" }
            ],
            observations: [
                { title: "Direct dependency", desc: "This package is directly required by your project manifest.", color: "bg-primary" },
                { title: "Maintained by Google", desc: "Official SDK backed by a verified enterprise organization. Low abandonment risk.", color: "bg-secondary-fixed" }
            ]
        },
        "pydantic": {
            name: "pydantic",
            description: "Data validation and settings management using Python type hints",
            score: 60,
            status: "Review Recommended",
            statusClass: "bg-[#FEF3C7] text-[#B45309]",
            ecosystem: "Python",
            requested: "2.1.1",
            latest: "2.6.4",
            license: "MIT",
            repository: "https://github.com/pydantic/pydantic",
            homepage: "https://docs.pydantic.dev/",
            requirements: [
                { name: "annotated-types", spec: ">=0.4.0" },
                { name: "pydantic-core", spec: "==2.14.6" },
                { name: "typing-extensions", spec: ">=4.6.1" }
            ],
            observations: [
                { title: "Diverged version", desc: "Your project lags 5 minor versions behind upstream releases. Major features added in between.", color: "bg-[#F59E0B]" },
                { title: "High usage index", desc: "Crucial community standard for parsing schemas. Extremely low replacement probability.", color: "bg-secondary" }
            ]
        },
        "httpx": {
            name: "httpx",
            description: "A next generation HTTP client for Python with async capabilities",
            score: 85,
            status: "Healthy",
            statusClass: "bg-[#D1FAE5] text-[#065F46]",
            ecosystem: "Python",
            requested: "0.24.1",
            latest: "0.27.0",
            license: "BSD-3-Clause",
            repository: "https://github.com/encode/httpx",
            homepage: "https://www.python-httpx.org/",
            requirements: [
                { name: "certifi", spec: "any" },
                { name: "httpcore", spec: ">=1.0.0,<1.1.0" },
                { name: "idna", spec: "any" },
                { name: "sniffio", spec: "any" }
            ],
            observations: [
                { title: "Active development", desc: "Highly active repo with frequent updates. Very prompt security patch turnarounds.", color: "bg-[#10B981]" }
            ]
        },
        "lodash": {
            name: "lodash",
            description: "Lodash modular utilities library for JavaScript",
            score: 40,
            status: "Critical Warning",
            statusClass: "bg-[#FEE2E2] text-[#991B1B]",
            ecosystem: "npm",
            requested: "4.17.15",
            latest: "4.17.21",
            license: "MIT",
            repository: "https://github.com/lodash/lodash",
            homepage: "https://lodash.com/",
            requirements: [],
            observations: [
                { title: "Active Security Advisory", desc: "Prototype Pollution vulnerabilities detected in version 4.17.15.", color: "bg-[#EF4444]" },
                { title: "Abandonment concerns", desc: "Rare commits in repository over the past two years, although widely downloaded.", color: "bg-[#F59E0B]" }
            ]
        },
        "express": {
            name: "express",
            description: "Fast, unopinionated, minimalist web framework for node",
            score: 88,
            status: "Healthy",
            statusClass: "bg-[#D1FAE5] text-[#065F46]",
            ecosystem: "npm",
            requested: "4.18.2",
            latest: "4.19.2",
            license: "MIT",
            repository: "https://github.com/expressjs/express",
            homepage: "https://expressjs.com/",
            requirements: [
                { name: "accepts", spec: "~1.3.8" },
                { name: "array-flatten", spec: "1.1.1" },
                { name: "body-parser", spec: "1.20.1" },
                { name: "content-disposition", spec: "0.5.4" }
            ],
            observations: [
                { title: "Battle tested", desc: "The standard backend runner in Node ecosystem. Low risk of sudden breaks.", color: "bg-[#10B981]" }
            ]
        }
    };

    const history = [
        { manifest: "requirements.txt", type: "pip", date: "Aug 23, 2026", score: 75, level: "Review Recommended", levelColor: "amber", levelClass: "bg-[#FEF3C7] text-[#92400E]", dotColor: "bg-[#D97706]", dependencies: 7, status: "Completed" },
        { manifest: "package.json", type: "npm", date: "Aug 22, 2026", score: 88, level: "Healthy", levelColor: "green", levelClass: "bg-[#D1FAE5] text-[#065F46]", dotColor: "bg-[#10B981]", dependencies: 9, status: "Completed" },
        { manifest: "requirements_old.txt", type: "pip", date: "Aug 20, 2026", score: 45, level: "Critical", levelColor: "red", levelClass: "bg-error-container text-on-error-container", dotColor: "bg-error", dependencies: 15, status: "Completed" }
    ];

    return {
        manifests,
        packages,
        history
    };
})();
