// SafePkg AI Frontend - Main Application Controller

document.addEventListener("DOMContentLoaded", () => {
    // Current application state
    const state = {
        activePage: "dashboard",
        currentManifest: "requirements.txt",
        uploadedFile: null,
        generateAiExplanation: false,
        history: [...window.SafePkgMockData.history]
    };

    // DOM Elements
    const elements = {
        // Sidebar Navigation
        navLinks: document.querySelectorAll("nav ul li a, nav div a"),
        // Page Containers
        pages: {
            dashboard: document.getElementById("page-dashboard"),
            newScan: document.getElementById("page-new-scan"),
            scanHistory: document.getElementById("page-scan-history"),
            packageSearch: document.getElementById("page-package-search")
        },
        // Dashboard Page Components
        dashTitle: document.getElementById("dash-project-title"),
        dashScore: document.getElementById("dash-health-score"),
        dashScoreBar: document.getElementById("dash-score-bar"),
        dashAttention: document.getElementById("dash-attention-count"),
        dashUpdates: document.getElementById("dash-updates-count"),
        dashNotices: document.getElementById("dash-notices-count"),
        dashTableBody: document.getElementById("dash-table-body"),
        dashAiSection: document.getElementById("dash-ai-section"),
        dashAiSummary: document.getElementById("dash-ai-summary"),
        dashAiHighlights: document.getElementById("dash-ai-highlights"),
        dashAiRecommendations: document.getElementById("dash-ai-recommendations"),
        dashAiUnavailable: document.getElementById("dash-ai-unavailable"),

        // New Scan Components
        uploaderArea: document.getElementById("uploader-area"),
        fileInput: document.getElementById("file-input"),
        postUploadDetails: document.getElementById("post-upload-details"),
        uploadedFileName: document.getElementById("uploaded-file-name"),
        uploadedFileInfo: document.getElementById("uploaded-file-info"),
        removeFileBtn: document.getElementById("remove-file-btn"),
        aiCheckbox: document.getElementById("ai-checkbox"),
        analyzeBtn: document.getElementById("analyze-btn"),
        progressState: document.getElementById("progress-state"),
        progressBar: document.getElementById("progress-bar"),
        progressPercentage: document.getElementById("progress-percentage"),

        // Package Search Components
        pkgSearchInput: document.getElementById("pkg-search-input"),
        pkgAnalyzeBtn: document.getElementById("pkg-analyze-btn"),
        pkgResultsGrid: document.getElementById("pkg-results-grid"),
        pkgNotFound: document.getElementById("pkg-not-found"),
        pkgDetailsName: document.getElementById("pkg-details-name"),
        pkgDetailsDesc: document.getElementById("pkg-details-desc"),
        pkgDetailsScore: document.getElementById("pkg-details-score"),
        pkgDetailsStatus: document.getElementById("pkg-details-status"),
        pkgDetailsEcosystem: document.getElementById("pkg-details-ecosystem"),
        pkgDetailsRequested: document.getElementById("pkg-details-requested"),
        pkgDetailsLatest: document.getElementById("pkg-details-latest"),
        pkgDetailsLicense: document.getElementById("pkg-details-license"),
        pkgRepoLink: document.getElementById("pkg-repo-link"),
        pkgHomepageLink: document.getElementById("pkg-homepage-link"),
        pkgRequirementsTitle: document.getElementById("pkg-requirements-title"),
        pkgRequirementsList: document.getElementById("pkg-requirements-list"),
        pkgObservationsList: document.getElementById("pkg-observations-list"),

        // Scan History Components
        historySearchInput: document.getElementById("history-search-input"),
        historyTableBody: document.getElementById("history-table-body"),
        historyResultsCount: document.getElementById("history-results-count")
    };

    // Initialize application
    init();

    function init() {
        setupNavigation();
        setupUploadFlow();
        setupPackageSearch();
        setupScanHistory();
        
        // Render initial view
        renderDashboard(state.currentManifest);
        renderHistoryTable();
    }

    // ==========================================
    // NAVIGATION ROUTING
    // ==========================================
    function setupNavigation() {
        elements.navLinks.forEach(link => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                const iconSpan = link.querySelector(".material-symbols-outlined");
                if (!iconSpan) return;

                const iconType = iconSpan.getAttribute("data-icon");
                let targetPage = "";

                if (iconType === "dashboard") targetPage = "dashboard";
                else if (iconType === "security") targetPage = "newScan";
                else if (iconType === "history") targetPage = "scanHistory";
                else if (iconType === "search") targetPage = "packageSearch";
                
                if (targetPage) {
                    navigateTo(targetPage);
                }
            });
        });

        // "Run New Scan" shortcut button on Dashboard
        const runNewScanBtn = document.getElementById("dash-run-new-scan-btn");
        if (runNewScanBtn) {
            runNewScanBtn.addEventListener("click", () => {
                navigateTo("newScan");
            });
        }
    }

    function navigateTo(pageKey) {
        state.activePage = pageKey;

        // Toggle page visibility
        Object.keys(elements.pages).forEach(key => {
            if (key === pageKey) {
                elements.pages[key].classList.remove("hidden");
            } else {
                elements.pages[key].classList.add("hidden");
            }
        });

        // Update sidebar links styles
        elements.navLinks.forEach(link => {
            const iconSpan = link.querySelector(".material-symbols-outlined");
            if (!iconSpan) return;

            const iconType = iconSpan.getAttribute("data-icon");
            let isCurrent = false;

            if (iconType === "dashboard" && pageKey === "dashboard") isCurrent = true;
            else if (iconType === "security" && pageKey === "newScan") isCurrent = true;
            else if (iconType === "history" && pageKey === "scanHistory") isCurrent = true;
            else if (iconType === "search" && pageKey === "packageSearch") isCurrent = true;

            if (isCurrent) {
                link.className = "flex items-center gap-md px-md py-sm rounded bg-surface-container-low text-primary border-l-2 border-primary transition-colors duration-200";
                if (iconSpan) iconSpan.style.fontVariationSettings = "'FILL' 1";
            } else {
                link.className = "flex items-center gap-md px-md py-sm rounded text-secondary hover:bg-surface-container-lowest transition-colors duration-200";
                if (iconSpan) iconSpan.style.fontVariationSettings = "'FILL' 0";
            }
        });

        // Custom action for package search inputs syncing
        if (pageKey === "packageSearch") {
            setTimeout(() => elements.pkgSearchInput.focus(), 50);
        }
    }

    // ==========================================
    // PAGE 1 — DASHBOARD RENDERER
    // ==========================================
    function renderDashboard(manifestName) {
        const manifest = window.SafePkgMockData.manifests[manifestName];
        if (!manifest) return;

        // Update titles and headers
        elements.dashTitle.textContent = `Project / Dependency Health: ${manifest.name}`;
        
        // Update Summary Cards
        elements.dashScore.textContent = manifest.score;
        elements.dashAttention.textContent = manifest.stats.attention;
        elements.dashUpdates.textContent = manifest.stats.updates;
        elements.dashNotices.textContent = manifest.stats.notices;

        // Render Table Body
        elements.dashTableBody.innerHTML = "";
        manifest.dependencies.forEach(dep => {
            const tr = document.createElement("tr");
            tr.className = "border-b border-functional hover:bg-[#F9FAFB] transition-colors";
            tr.innerHTML = `
                <td class="py-sm px-md font-semibold">${dep.package}</td>
                <td class="py-sm px-md text-secondary">${dep.current}</td>
                <td class="py-sm px-md">${dep.latest}</td>
                <td class="py-sm px-md">
                    <div class="flex items-center gap-xs">
                        <div class="w-12 h-1 bg-surface-container-high rounded-full overflow-hidden">
                            <div class="h-full ${dep.barColor}" style="width: ${dep.width}"></div>
                        </div>
                        <span class="font-body-sm">${dep.score}</span>
                    </div>
                </td>
                <td class="py-sm px-md">
                    <span class="inline-flex items-center px-2 py-1 rounded ${dep.statusClass} font-label-md text-label-md">${dep.status}</span>
                </td>
            `;
            // Add click listener to show details on package search
            tr.addEventListener("click", () => {
                elements.pkgSearchInput.value = dep.package;
                performPackageSearch(dep.package);
                navigateTo("packageSearch");
            });
            tr.classList.add("cursor-pointer");
            elements.dashTableBody.appendChild(tr);
        });

        // AI Explanation Layer
        const hasAi = state.generateAiExplanation && manifest.aiAnalysis;
        if (hasAi) {
            elements.dashAiSection.classList.remove("hidden");
            elements.dashAiUnavailable.classList.add("hidden");

            elements.dashAiSummary.textContent = manifest.aiAnalysis.summary;
            
            // Render Highlights
            elements.dashAiHighlights.innerHTML = "";
            manifest.aiAnalysis.highlights.forEach(highlight => {
                const li = document.createElement("li");
                li.innerHTML = highlight;
                elements.dashAiHighlights.appendChild(li);
            });

            // Render Recommendations
            elements.dashAiRecommendations.innerHTML = "";
            manifest.aiAnalysis.recommendations.forEach(rec => {
                const div = document.createElement("div");
                div.className = "bg-surface-container-lowest border border-functional rounded p-sm flex items-start gap-sm mt-xs";
                div.innerHTML = `
                    <span class="material-symbols-outlined text-secondary text-[16px] mt-[2px]" data-icon="task_alt">task_alt</span>
                    <div class="flex-1">
                        <p class="font-body-sm text-body-sm text-primary font-medium">${rec.title}</p>
                        <p class="font-body-sm text-body-sm text-secondary mt-[2px]">${rec.description}</p>
                    </div>
                    <button class="px-sm py-xs border border-functional rounded text-primary font-label-md text-label-md hover:bg-surface-container-high transition-colors">Create Issue</button>
                `;
                elements.dashAiRecommendations.appendChild(div);
            });
        } else {
            elements.dashAiSection.classList.add("hidden");
            elements.dashAiUnavailable.classList.remove("hidden");
        }
    }

    // ==========================================
    // PAGE 2 — NEW SCAN FLOW
    // ==========================================
    function setupUploadFlow() {
        // Drag and drop trigger
        elements.uploaderArea.addEventListener("click", () => {
            elements.fileInput.click();
        });

        elements.uploaderArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            elements.uploaderArea.classList.add("bg-surface-container-low");
        });

        elements.uploaderArea.addEventListener("dragleave", () => {
            elements.uploaderArea.classList.remove("bg-surface-container-low");
        });

        elements.uploaderArea.addEventListener("drop", (e) => {
            e.preventDefault();
            elements.uploaderArea.classList.remove("bg-surface-container-low");
            
            if (e.dataTransfer.files.length > 0) {
                handleFileSelected(e.dataTransfer.files[0]);
            }
        });

        elements.fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                handleFileSelected(e.target.files[0]);
            }
        });

        elements.removeFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            clearSelectedFile();
        });

        elements.analyzeBtn.addEventListener("click", () => {
            runScanSimulation();
        });
    }

    function handleFileSelected(file) {
        const name = file.name;
        const validNames = ["requirements.txt", "package.json"];
        
        if (!validNames.includes(name)) {
            alert(`Unsupported manifest file: "${name}". Please upload requirements.txt or package.json.`);
            clearSelectedFile();
            return;
        }

        state.uploadedFile = file;
        
        // Show file details
        elements.uploadedFileName.textContent = file.name;
        const sizeKB = (file.size / 1024).toFixed(1);
        const fileType = file.name.endsWith(".json") ? "JSON Config" : "Plain Text";
        elements.uploadedFileInfo.textContent = `${fileType} · ${sizeKB} KB`;

        elements.postUploadDetails.classList.remove("hidden");
        elements.analyzeBtn.removeAttribute("disabled");
    }

    function clearSelectedFile() {
        state.uploadedFile = null;
        elements.fileInput.value = "";
        elements.postUploadDetails.classList.add("hidden");
        elements.analyzeBtn.setAttribute("disabled", "true");
        elements.progressState.classList.add("hidden");
    }

    function runScanSimulation() {
        if (!state.uploadedFile) return;

        // Set AI generator option
        state.generateAiExplanation = elements.aiCheckbox.checked;

        // Hide upload triggers, show progress state
        elements.analyzeBtn.setAttribute("disabled", "true");
        elements.progressState.classList.remove("hidden");

        let progress = 0;
        elements.progressBar.style.width = "0%";
        elements.progressPercentage.textContent = "0%";

        const interval = setInterval(() => {
            progress += Math.floor(Math.random() * 15) + 5;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);

                setTimeout(() => {
                    finalizeScan();
                }, 400);
            }
            elements.progressBar.style.width = `${progress}%`;
            elements.progressPercentage.textContent = `${progress}%`;
        }, 150);
    }

    function finalizeScan() {
        const fileName = state.uploadedFile.name;
        
        // Add new item to history database
        const template = window.SafePkgMockData.manifests[fileName];
        const newHistoryItem = {
            manifest: fileName,
            type: fileName.endsWith(".json") ? "npm" : "pip",
            date: "Today at " + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            score: template.score,
            level: template.level,
            levelColor: template.levelColor,
            levelClass: template.levelColor === "green" ? "bg-[#D1FAE5] text-[#065F46]" : "bg-[#FEF3C7] text-[#92400E]",
            dotColor: template.levelColor === "green" ? "bg-[#10B981]" : "bg-[#D97706]",
            dependencies: template.stats.total,
            status: "Completed"
        };

        // Add to history state
        state.history.unshift(newHistoryItem);
        state.currentManifest = fileName;

        // Re-render dashboard and scan history
        renderDashboard(fileName);
        renderHistoryTable();

        // Reset scanning inputs
        clearSelectedFile();

        // Navigate to Dashboard
        navigateTo("dashboard");
    }

    // ==========================================
    // PAGE 3 — PACKAGE SEARCH
    // ==========================================
    function setupPackageSearch() {
        elements.pkgAnalyzeBtn.addEventListener("click", () => {
            performPackageSearch(elements.pkgSearchInput.value);
        });

        elements.pkgSearchInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                performPackageSearch(elements.pkgSearchInput.value);
            }
        });
    }

    function performPackageSearch(query) {
        if (!query) return;
        
        const cleanQuery = query.trim().toLowerCase();
        const pkg = window.SafePkgMockData.packages[cleanQuery];

        if (pkg) {
            elements.pkgNotFound.classList.add("hidden");
            elements.pkgResultsGrid.classList.remove("hidden");

            // Fill bento card details
            elements.pkgDetailsName.textContent = pkg.name;
            elements.pkgDetailsDesc.textContent = pkg.description;
            elements.pkgDetailsScore.innerHTML = `${pkg.score}<span class="text-secondary text-sm">/100</span>`;
            elements.pkgDetailsStatus.className = `px-md py-sm rounded font-label-md text-label-md border flex items-center gap-xs ${pkg.statusClass}`;
            elements.pkgDetailsStatus.innerHTML = `
                <span class="material-symbols-outlined text-[16px]" data-icon="check_circle">check_circle</span>
                ${pkg.status}
            `;
            elements.pkgDetailsEcosystem.textContent = pkg.ecosystem;
            elements.pkgDetailsRequested.textContent = pkg.requested;
            elements.pkgDetailsLatest.textContent = pkg.latest;
            elements.pkgDetailsLicense.textContent = pkg.license;
            elements.pkgRepoLink.href = pkg.repository;
            elements.pkgHomepageLink.href = pkg.homepage;

            // Runtime requirements list
            elements.pkgRequirementsTitle.textContent = "Runtime Requirements";
            elements.pkgRequirementsList.innerHTML = "";
            if (pkg.requirements && pkg.requirements.length > 0) {
                pkg.requirements.forEach(req => {
                    const div = document.createElement("div");
                    div.className = "flex justify-between items-center py-xs border-b border-outline-variant border-dashed";
                    div.innerHTML = `<span>${req.name}</span><span class="text-secondary">${req.spec}</span>`;
                    elements.pkgRequirementsList.appendChild(div);
                });
            } else {
                elements.pkgRequirementsList.innerHTML = `<div class="text-secondary py-xs font-body-sm">No dependencies defined.</div>`;
            }

            // Observations
            elements.pkgObservationsList.innerHTML = "";
            pkg.observations.forEach(obs => {
                const div = document.createElement("div");
                div.className = "flex items-start gap-sm";
                div.innerHTML = `
                    <div class="mt-1 w-2 h-2 rounded-full ${obs.color} shrink-0"></div>
                    <div class="flex flex-col">
                        <span class="font-body-md text-body-md text-on-surface font-semibold">${obs.title}</span>
                        <span class="font-body-sm text-body-sm text-secondary mt-xs">${obs.desc}</span>
                    </div>
                `;
                elements.pkgObservationsList.appendChild(div);
            });
        } else {
            // Not found state
            elements.pkgResultsGrid.classList.add("hidden");
            elements.pkgNotFound.classList.remove("hidden");
        }
    }

    // ==========================================
    // PAGE 4 — SCAN HISTORY
    // ==========================================
    function setupScanHistory() {
        elements.historySearchInput.addEventListener("input", () => {
            renderHistoryTable();
        });
    }

    function renderHistoryTable() {
        const filter = elements.historySearchInput.value.toLowerCase().trim();
        elements.historyTableBody.innerHTML = "";

        const filtered = state.history.filter(item => 
            item.manifest.toLowerCase().includes(filter)
        );

        elements.historyResultsCount.textContent = `Showing 1 to ${filtered.length} of ${filtered.length} results`;

        if (filtered.length === 0) {
            elements.historyTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="py-xl text-center text-secondary font-body-md">
                        No matching scans found.
                    </td>
                </tr>
            `;
            return;
        }

        filtered.forEach(item => {
            const tr = document.createElement("tr");
            tr.className = "hover:bg-surface-container-low transition-colors group";
            
            const isJson = item.manifest.endsWith(".json");
            const icon = isJson ? "data_object" : "description";

            tr.innerHTML = `
                <td class="py-md px-md whitespace-nowrap flex items-center gap-sm">
                    <span class="material-symbols-outlined text-secondary" data-icon="${icon}">${icon}</span>
                    <span class="font-code-sm text-code-sm font-semibold">${item.manifest}</span>
                </td>
                <td class="py-md px-md whitespace-nowrap text-secondary">${item.date}</td>
                <td class="py-md px-md whitespace-nowrap">
                    <div class="flex items-center gap-xs">
                        <span class="font-medium text-on-surface-variant">${item.score}</span>
                        <span class="text-xs text-secondary">/100</span>
                    </div>
                </td>
                <td class="py-md px-md whitespace-nowrap">
                    <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full font-label-md text-[11px] ${item.levelClass}">
                        <span class="w-1.5 h-1.5 rounded-full ${item.dotColor}"></span>
                        ${item.level}
                    </span>
                </td>
                <td class="py-md px-md whitespace-nowrap text-right text-secondary">${item.dependencies}</td>
                <td class="py-md px-md whitespace-nowrap">
                    <span class="inline-flex items-center gap-1.5 text-secondary">
                        <span class="material-symbols-outlined text-[16px] text-[#10B981]" data-icon="check_circle">check_circle</span>
                        ${item.status}
                    </span>
                </td>
                <td class="py-md px-md whitespace-nowrap text-right">
                    <button class="view-report-btn font-label-md text-label-md text-primary bg-surface border border-outline-variant px-sm py-xs rounded hover:bg-surface-container-high transition-colors">
                        View Report
                    </button>
                </td>
            `;

            // Setup report loading listener
            const btn = tr.querySelector(".view-report-btn");
            btn.addEventListener("click", () => {
                state.currentManifest = item.manifest;
                // If it was a newly created scan or historical template, ensure state aligns
                const originalManifest = window.SafePkgMockData.manifests[item.manifest];
                if (originalManifest) {
                    // Update artificial AI summary generator toggle based on availability
                    state.generateAiExplanation = originalManifest.aiAnalysis ? originalManifest.aiAnalysis.available : false;
                }
                renderDashboard(item.manifest);
                navigateTo("dashboard");
            });

            elements.historyTableBody.appendChild(tr);
        });
    }
});
