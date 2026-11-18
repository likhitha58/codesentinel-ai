
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END


class AuditAgentState(TypedDict, total=False):
    report: dict[str, Any]
    prioritized_findings: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    executive_summary: str


SEVERITY_PRIORITY = {
    "CRITICAL": "P0",
    "HIGH": "P1",
    "MEDIUM": "P2",
    "LOW": "P3",
    "INFO": "P4",
}


REMEDIATION_GUIDANCE = {
    "SEC001": (
        "Move credentials to environment variables or a managed secret store. "
        "Rotate any exposed credential after verifying exposure."
    ),
    "SEC002": (
        "Use parameterized SQL queries instead of constructing SQL with "
        "untrusted input."
    ),
    "SEC003": (
        "Avoid evaluating untrusted input. Use a safe parser or an explicit "
        "allowlist of supported operations."
    ),
    "SEC004": (
        "Avoid shell execution with untrusted input. Prefer safe process "
        "APIs with argument lists and validated inputs."
    ),
    "SEC005": (
        "Use a modern cryptographic hash such as SHA-256 for integrity "
        "checks. Use a password-specific hashing algorithm for passwords."
    ),
    "SEC006": (
        "Avoid deserializing untrusted data with unsafe loaders. Use a "
        "safe serialization format and safe parsing APIs."
    ),
    "SEC007": (
        "Disable debug mode in production and review exposed diagnostic "
        "information."
    ),
    "SEC008": (
        "Restrict CORS origins to the specific trusted domains required "
        "by the application."
    ),
    "CG001": (
        "Review the TODO, FIXME, XXX, or HACK marker and either complete "
        "the work or document why it is intentionally deferred."
    ),
    "CG002": (
        "Implement the missing functionality or explicitly document why "
        "the operation is unsupported."
    ),
    "CG003": (
        "Review the empty statement and determine whether meaningful "
        "implementation or an explanatory comment is needed."
    ),
    "CG004": (
        "Add appropriate tests for the repository's important application "
        "behavior. Confirm the test-file naming convention first."
    ),
}


def prioritize_findings(state: AuditAgentState):
    """Assign an operational priority to every finding."""

    report = state["report"]
    findings = report.get("findings", [])

    prioritized = []

    for finding in findings:
        item = dict(finding)

        severity = item.get("severity", "INFO").upper()
        item["priority"] = SEVERITY_PRIORITY.get(severity, "P4")

        item["recommended_action"] = REMEDIATION_GUIDANCE.get(
            item.get("rule_id"),
            "Review this finding manually and determine an appropriate fix."
        )

        prioritized.append(item)

    priority_order = {
        "P0": 0,
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
    }

    prioritized.sort(
        key=lambda item: (
            priority_order.get(item["priority"], 99),
            item.get("file", ""),
            item.get("line", 0) or 0,
        )
    )

    return {"prioritized_findings": prioritized}


def generate_recommendations(state: AuditAgentState):
    """Group remediation guidance by rule to avoid duplicate actions."""

    findings = state.get("prioritized_findings", [])
    grouped = {}

    for finding in findings:
        rule_id = finding.get("rule_id", "UNKNOWN")

        if rule_id not in grouped:
            grouped[rule_id] = {
                "rule_id": rule_id,
                "title": finding.get("title", "Unclassified finding"),
                "category": finding.get("category", "UNKNOWN"),
                "priority": finding.get("priority", "P4"),
                "recommended_action": finding.get(
                    "recommended_action",
                    "Review this finding manually."
                ),
                "affected_locations": [],
                "occurrences": 0,
            }

        grouped[rule_id]["occurrences"] += 1
        grouped[rule_id]["affected_locations"].append(
            {
                "file": finding.get("file"),
                "line": finding.get("line"),
            }
        )

    recommendations = list(grouped.values())

    recommendations.sort(
        key=lambda item: (
            {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}.get(
                item["priority"], 99
            ),
            item["rule_id"],
        )
    )

    return {"recommendations": recommendations}


def generate_executive_summary(state: AuditAgentState):
    """Generate a concise summary using verified audit counts."""

    report = state["report"]
    summary = report.get("scan_summary", {})
    findings = state.get("prioritized_findings", [])

    total = summary.get("total_findings", len(findings))
    security = summary.get("security_findings", 0)
    quality = summary.get("quality_findings", 0)

    high_priority = sum(
        1 for finding in findings
        if finding.get("priority") in ("P0", "P1")
    )

    if total == 0:
        message = (
            "The configured scanners did not report any findings. "
            "This does not guarantee that the repository is free of defects "
            "or vulnerabilities."
        )
    else:
        message = (
            f"The audit produced {total} findings: "
            f"{security} security indicators and "
            f"{quality} code-quality indicators. "
            f"{high_priority} findings have P0 or P1 priority "
            f"and should be reviewed first."
        )

    message += (
        " Findings are automated indicators and require manual validation."
    )

    return {"executive_summary": message}


def build_audit_agent():
    """Build and compile the LangGraph audit workflow."""

    workflow = StateGraph(AuditAgentState)

    workflow.add_node("prioritize_findings", prioritize_findings)
    workflow.add_node("generate_recommendations", generate_recommendations)
    workflow.add_node("generate_executive_summary", generate_executive_summary)

    workflow.add_edge(START, "prioritize_findings")
    workflow.add_edge("prioritize_findings", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "generate_executive_summary")
    workflow.add_edge("generate_executive_summary", END)

    return workflow.compile()


def run_audit_agent(audit_report):
    """Run the LangGraph workflow and attach its results to the report."""

    agent = build_audit_agent()

    result = agent.invoke({
        "report": audit_report,
    })

    enhanced_report = dict(audit_report)

    enhanced_report["agent_analysis"] = {
        "agent_type": "LangGraph deterministic workflow",
        "executive_summary": result["executive_summary"],
        "prioritized_findings": result["prioritized_findings"],
        "recommendations": result["recommendations"],
    }

    return enhanced_report
