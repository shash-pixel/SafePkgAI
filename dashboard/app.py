"""Native Streamlit dashboard for SafePkg AI."""

import asyncio
import re
from collections.abc import Awaitable
from datetime import datetime, timezone
from typing import TypeVar
from zoneinfo import ZoneInfo

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from dashboard.backend_adapter import (
    DashboardInputError,
    analyze_package,
    analyze_uploaded_manifest,
    list_history,
    load_history_summary,
    save_summary,
)

from config.settings import settings
st.write("Gemini key configured:", bool(settings.gemini_api_key))

from fetchers.base import PackageFetchError
from llm.dependency_health_explainer import DependencyHealthExplanationService
from llm.gemini_provider import GeminiStructuredProvider
from llm.provider import LLMConfigurationError, LLMGenerationError
from models.dependency_health_explanation import DependencyHealthExplanation
from models.dependency_health_summary import DependencyHealthSummary
from models.package import PackageEcosystem

Result = TypeVar("Result")
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def run_async(awaitable: Awaitable[Result]) -> Result:
    """Run one existing async service from Streamlit's script flow."""

    return asyncio.run(awaitable)


def score_text(score: int | None) -> str:
    return f"{score}/100" if score is not None else "Not available"


def format_history_time(timestamp: datetime) -> str:
    """Display UTC history timestamps in India Standard Time."""

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(INDIA_TIMEZONE).strftime("%Y-%m-%d %H:%M IST")


_UPDATE_ACTION = re.compile(
    r"^Review an update to (.+?) and confirm compatibility before changing "
    r"the project dependency\.$",
    re.IGNORECASE,
)


def group_recommended_actions(actions: list[str]) -> list[str]:
    """Collapse repeated update advice while retaining meaningful actions."""

    update_targets: list[str] = []
    distinct_actions: list[str] = []
    seen_actions: set[str] = set()
    for action in actions:
        match = _UPDATE_ACTION.match(action.strip())
        if match:
            update_targets.append(match.group(1))
        elif action not in seen_actions:
            distinct_actions.append(action)
            seen_actions.add(action)
    if update_targets:
        package_list = ", ".join(dict.fromkeys(update_targets))
        distinct_actions.insert(
            0,
            "Review available updates and confirm compatibility before changing "
            f"project dependencies: {package_list}.",
        )
    return distinct_actions


def initialize_state() -> None:
    for key, value in {
        "health_summary": None,
        "ai_explanation": None,
        "ai_unavailable": False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = value


def open_new_scan() -> None:
    """Move from the dashboard empty state to the existing scan workflow."""

    st.session_state.page = "New scan"


def render_empty_dashboard() -> None:
    """Give a first-time developer a useful, focused starting point."""

    with st.container(border=True, gap="large"):
        introduction, overview = st.columns([3, 2], gap="large", vertical_alignment="center")
        with introduction:
            st.badge("Ready for analysis", icon=":material/check_circle:", color="gray")
            st.subheader("Turn a dependency manifest into a clear plan", anchor=False)
            st.write(
                "Upload requirements.txt or package.json and SafePkg AI will create "
                "a practical Dependency Health Report from real package metadata."
            )
            st.button(
                "Create a Dependency Health Report",
                type="primary",
                icon=":material/upload_file:",
                on_click=open_new_scan,
            )
        with overview:
            st.markdown("**Your first report includes**")
            st.write(":material/update: Version recommendations")
            st.write(":material/build: Maintenance observations")
            st.write(":material/gavel: License information")
            st.write(":material/campaign: Public package notices")
    st.caption("Reports are saved locally and remain available in Scan history.")


def render_report(summary: DependencyHealthSummary) -> None:
    """Render backend facts; no scoring, parsing, or fetching is duplicated here."""

    st.subheader("Dependency Health Report", anchor=False)
    st.caption(
        f"Project / Dependency Health: {summary.source_name}  ·  "
        f"{summary.manifest_type}  ·  {summary.data_coverage_percent}% data coverage"
    )
    with st.container(horizontal=True):
        st.metric("Health Score", score_text(summary.aggregate_health_score), border=True)
        st.metric("Health Level", summary.aggregate_health_level.replace("_", " ").title(), border=True)
        st.metric("Needs Attention", summary.dependencies_needing_attention, border=True)
        st.metric("Updates Available", summary.dependencies_with_updates, border=True)
        st.metric("Public Notices", summary.dependencies_with_public_notices, border=True)

    show_notices = summary.dependencies_with_public_notices > 0
    rows = []
    for report in summary.dependency_reports:
        metadata = report.package_metadata
        row = {
            "Package": report.declared_dependency.name,
            "Declared version": report.declared_dependency.version_constraint or "Not specified",
            "Resolved version": metadata.resolved_version if metadata else "Unknown",
            "Latest version": metadata.latest_available_version if metadata else "Unknown",
            "Health Score": report.health_score,
            "Health Level": report.health_level.replace("_", " ").title(),
        }
        if show_notices:
            row["Public notices"] = len(report.public_advisory_notices) or "—"
        rows.append(row)
    with st.container(border=True):
        st.subheader(":material/table_chart: Dependency overview", anchor=False)
        st.dataframe(
            rows,
            column_config={
                "Health Score": st.column_config.ProgressColumn(
                    "Health Score", min_value=0, max_value=100, format="%d"
                )
            },
            hide_index=True,
            width="stretch",
        )

    st.subheader(":material/account_tree: Dependency details", anchor=False)
    for report in summary.dependency_reports:
        metadata = report.package_metadata
        with st.expander(
            f"{report.declared_dependency.name} · {score_text(report.health_score)} · "
            f"{report.health_level.replace('_', ' ').title()}"
        ):
            if metadata:
                st.write(metadata.summary or "No registry summary is available.")
                st.write(f"**License:** {metadata.license_name or 'Not reported'}")
                st.write(
                    f"**Versions:** {metadata.resolved_version} resolved; "
                    f"{metadata.latest_available_version} latest"
                )
            else:
                st.info("Package metadata could not be retrieved for this dependency.")
            if report.version_recommendation:
                st.write(f"**Version recommendation:** {report.version_recommendation}")
            for observation in report.observations:
                st.write(f"- **{observation.title}:** {observation.description}")
            for notice in report.public_advisory_notices:
                if notice.details_url:
                    st.markdown(
                        f"- **{notice.advisory_id}:** "
                        f"[{notice.summary or 'Public package notice'}]({notice.details_url})"
                    )
                else:
                    st.write(f"- **{notice.advisory_id}:** {notice.summary or 'Public package notice'}")
            for limitation in report.limitations:
                st.caption(f"Limitation: {limitation}")
    if summary.limitations:
        with st.expander("Report limitations"):
            for limitation in summary.limitations:
                st.write(f"- {limitation}")


def render_ai_explanation(explanation: DependencyHealthExplanation | None) -> None:
    st.subheader(":material/auto_awesome: AI analysis", anchor=False)
    if explanation is None:
        message = (
            "AI explanation is currently unavailable. The factual report is complete."
            if st.session_state.ai_unavailable
            else "Enable the optional Gemini explanation when starting a new scan."
        )
        st.info(message)
        return
    st.write(explanation.overall_summary)
    if explanation.health_highlights:
        st.write("**Highlights**")
        for item in explanation.health_highlights:
            st.write(f"- {item}")
    if explanation.recommended_actions:
        st.write("**Recommended actions**")
        for item in group_recommended_actions(explanation.recommended_actions):
            st.write(f"- {item}")


def render_new_scan() -> None:
    st.subheader("New Dependency Health Scan", anchor=False)
    st.caption("Upload a file named requirements.txt or package.json.")
    with st.form("manifest_scan_form"):
        uploaded_file = st.file_uploader("Dependency manifest", type=["txt", "json"])
        include_ai = st.checkbox("Generate optional Gemini explanation")
        submitted = st.form_submit_button("Run New Scan", type="primary")
    if not submitted:
        return
    if uploaded_file is None:
        st.error("Choose requirements.txt or package.json before running a scan.")
        return
    try:
        with st.spinner("Analyzing package metadata and Dependency Health..."):
            summary = run_async(analyze_uploaded_manifest(uploaded_file))
            save_summary(summary)
        st.session_state.health_summary = summary
        st.session_state.ai_explanation = None
        st.session_state.ai_unavailable = False
        if include_ai:
            try:
                with st.spinner("Generating AI explanation..."):
                    service = DependencyHealthExplanationService(GeminiStructuredProvider())
                    st.session_state.ai_explanation = run_async(service.explain(summary))
            except (LLMConfigurationError, LLMGenerationError):
                st.session_state.ai_unavailable = True
        st.success("Dependency Health Report created and saved to scan history.")
        render_report(summary)
        render_ai_explanation(st.session_state.ai_explanation)
    except DashboardInputError as error:
        st.error(str(error))
    except (OSError, ValueError, PackageFetchError):
        st.error("The report could not be created. Check the file and try again.")


def render_package_search() -> None:
    st.subheader("Package search", anchor=False)
    with st.form("package_search_form"):
        ecosystem = st.selectbox("Package type", list(PackageEcosystem), format_func=str.upper)
        package_name = st.text_input("Package name", placeholder="requests or httpx")
        version = st.text_input("Version (optional)")
        submitted = st.form_submit_button("Analyze package", type="primary")
    if not submitted:
        return
    if not package_name.strip():
        st.error("Enter a package name.")
        return
    try:
        with st.spinner("Retrieving real package metadata..."):
            result = run_async(analyze_package(ecosystem, package_name.strip(), version or None))
        metadata = result.metadata
        st.subheader(f"{metadata.reference.name} ({metadata.reference.ecosystem.upper()})")
        st.write(metadata.summary or "No package summary is available.")
        with st.container(horizontal=True):
            st.metric("Resolved Version", metadata.resolved_version, border=True)
            st.metric("Latest Version", metadata.latest_available_version, border=True)
            st.metric("License", metadata.license_name or "Not reported", border=True)
            st.metric("Dependencies", len(metadata.dependencies), border=True)
        for insight in result.insights:
            st.write(f"- **{insight.title}:** {insight.explanation}")
        if metadata.dependencies:
            st.dataframe(
                [{"Name": item.name, "Version": item.version_constraint or "Not specified"} for item in metadata.dependencies],
                hide_index=True,
                width="stretch",
            )
    except (OSError, ValueError, PackageFetchError):
        st.error("Package metadata could not be retrieved. Check the package and try again.")


def render_history() -> None:
    st.subheader("Scan history", anchor=False)
    try:
        entries = list_history()
    except OSError:
        st.error("Scan history is temporarily unavailable.")
        return
    if not entries:
        st.info("No saved Dependency Health Reports yet.")
        return
    st.dataframe(
        [
            {
                "ID": entry.scan_id,
                "Source": entry.source_name,
                "Health Score": entry.aggregate_health_score,
                "Dependencies": entry.dependency_count,
                "Saved (IST)": format_history_time(entry.saved_at),
            }
            for entry in entries
        ],
        hide_index=True,
        width="stretch",
    )
    scan_id = st.selectbox("Open saved report", [entry.scan_id for entry in entries])
    if st.button("Load report"):
        summary = load_history_summary(scan_id)
        if summary is None:
            st.error("That saved report could not be found.")
            return
        st.session_state.health_summary = summary
        st.session_state.ai_explanation = None
        st.session_state.ai_unavailable = False
        st.success("Saved report loaded. Open Dashboard to review it.")


def main() -> None:
    st.set_page_config(page_title="SafePkg AI", page_icon=":material/account_tree:", layout="wide")
    initialize_state()
    with st.sidebar:
        st.title(":material/account_tree: SafePkg AI", anchor=False)
        st.caption("Open-source package workspace")
        st.space("small")
        page = st.radio(
            "Navigation",
            ["Dashboard", "New scan", "Package search", "Scan history"],
            key="page",
            label_visibility="collapsed",
        )
        st.space("medium")
        st.badge("Local scan history", icon=":material/database:", color="gray")
        st.caption("Dependency Health · Package Health")
    st.title(page, anchor=False)
    st.caption("Practical package intelligence for your project dependencies")
    if page == "Dashboard":
        summary = st.session_state.health_summary
        if summary is None:
            render_empty_dashboard()
        else:
            render_report(summary)
            render_ai_explanation(st.session_state.ai_explanation)
    elif page == "New scan":
        render_new_scan()
    elif page == "Package search":
        render_package_search()
    else:
        render_history()


if __name__ == "__main__":
    main()
