#!/usr/bin/env python3

import html
import json
from pathlib import Path


class ReportGenerator:
    """Generate human-readable compatibility test reports."""

    def __init__(self, result, report_dir):
        self.result = result
        self.report_dir = Path(report_dir)

    @staticmethod
    def _escape(value):
        if value is None:
            return ""

        return html.escape(str(value))

    @staticmethod
    def _status_class(status):
        status = str(status or "UNKNOWN").lower()

        if status == "pass":
            return "pass"

        if status == "fail":
            return "fail"

        if status in ("warn", "warning"):
            return "warn"

        if status == "skip":
            return "skip"

        return "unknown"

    @staticmethod
    def _status_icon(status):
        status = str(status or "").upper()

        if status == "PASS":
            return "✓"

        if status == "FAIL":
            return "✗"

        if status == "SKIP":
            return "−"

        return "!"

    def generate_markdown(self):
        report_file = self.report_dir / "result.md"

        environment = self.result.get("environment", {})
        os_info = environment.get("os", {})
        cpu_info = environment.get("cpu", {})
        memory_info = environment.get("memory", {})
        disk_info = environment.get("disk", {})

        compatibility = self.result.get("compatibility", {})
        summary = self.result.get("summary", {})

        lines = []

        lines.append("# Linux OS Compatibility Test Report")
        lines.append("")

        lines.append(
            f"**Overall Result:** "
            f"`{self.result.get('status', 'UNKNOWN')}`"
        )

        lines.append(
            f"**Timestamp:** "
            f"`{self.result.get('timestamp', '')}`"
        )

        lines.append("")

        lines.append("## Environment")
        lines.append("")

        lines.append(
            f"- OS: {os_info.get('pretty_name', 'Unknown')}"
        )

        lines.append(
            f"- Architecture: "
            f"{cpu_info.get('architecture', 'Unknown')}"
        )

        lines.append(
            f"- Kernel: "
            f"{environment.get('kernel', {}).get('release', 'Unknown')}"
        )

        lines.append(
            f"- CPU: "
            f"{cpu_info.get('model_name', 'Unknown')}"
        )

        lines.append(
            f"- Memory: "
            f"{memory_info.get('total_mb', 0)} MB"
        )

        lines.append(
            f"- Disk Available: "
            f"{round(
                disk_info.get('available_bytes', 0)
                / (1024 * 1024 * 1024),
                2
            )} GB"
        )

        lines.append("")

        lines.append("## Compatibility Result")
        lines.append("")

        lines.append(
            f"- Status: "
            f"`{compatibility.get('status', 'UNKNOWN')}`"
        )

        lines.append(
            f"- Supported: "
            f"`{compatibility.get('supported', False)}`"
        )

        lines.append("")

        lines.append("| Check | Status | Message |")
        lines.append("|---|---|---|")

        for check in compatibility.get("checks", []):
            lines.append(
                f"| {check.get('name', '')} "
                f"| {check.get('status', '')} "
                f"| {check.get('message', '')} |"
            )

        lines.append("")

        lines.append("## Test Summary")
        lines.append("")

        lines.append(
            f"- Total: {summary.get('total', 0)}"
        )

        lines.append(
            f"- PASS: {summary.get('passed', 0)}"
        )

        lines.append(
            f"- FAIL: {summary.get('failed', 0)}"
        )

        lines.append(
            f"- SKIP: {summary.get('skipped', 0)}"
        )

        lines.append("")

        lines.append("## Test Cases")
        lines.append("")

        lines.append(
            "| Test | Category | Status | Message |"
        )

        lines.append("|---|---|---|---|")

        for test in self.result.get("tests", []):
            lines.append(
                f"| {test.get('name', '')} "
                f"| {test.get('category', '')} "
                f"| {test.get('status', '')} "
                f"| {test.get('message', '')} |"
            )

        lines.append("")

        lines.append("## Application Log Analysis")
        lines.append("")

        deployment_tests = [
            test
            for test in self.result.get("tests", [])
            if test.get("log_analysis") is not None
        ]

        if not deployment_tests:
            lines.append(
                "No application deployment log analysis "
                "was generated."
            )
            lines.append("")

        else:
            for test in deployment_tests:
                application = test.get(
                    "application",
                    "Unknown",
                )

                log_analysis = test.get(
                    "log_analysis",
                    {},
                )

                log_summary = log_analysis.get(
                    "summary",
                    {},
                )

                lines.append(f"### {application}")
                lines.append("")

                lines.append(
                    f"- Status: "
                    f"`{log_summary.get('status', 'UNKNOWN')}`"
                )

                lines.append(
                    f"- Total Findings: "
                    f"{log_summary.get('total', 0)}"
                )

                lines.append(
                    f"- Critical: "
                    f"{log_summary.get('critical', 0)}"
                )

                lines.append(
                    f"- High: "
                    f"{log_summary.get('high', 0)}"
                )

                lines.append(
                    f"- Medium: "
                    f"{log_summary.get('medium', 0)}"
                )

                lines.append(
                    f"- Low: "
                    f"{log_summary.get('low', 0)}"
                )

                lines.append("")

                findings = log_analysis.get(
                    "findings",
                    [],
                )

                if not findings:
                    lines.append(
                        "No compatibility-related "
                        "log findings detected."
                    )
                    lines.append("")
                    continue

                lines.append(
                    "| Severity | Category | Message | Reason | Suggestion |"
                )

                lines.append(
                    "|---|---|---|---|---|"
                )

                for finding in findings:
                    lines.append(
                        f"| {finding.get('severity', '')} "
                        f"| {finding.get('category', '')} "
                        f"| {finding.get('message', '')} "
                        f"| {finding.get('reason', '')} "
                        f"| {finding.get('suggestion', '')} |"
                    )

                lines.append("")

        lines.append("## Conclusion")
        lines.append("")

        if compatibility.get("supported"):
            lines.append(
                "The current environment satisfies "
                "the configured compatibility requirements."
            )
        else:
            lines.append(
                "The current environment does not satisfy "
                "the configured compatibility requirements."
            )

        report_file.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        return report_file

    def generate_html(self):
        report_file = self.report_dir / "result.html"

        environment = self.result.get("environment", {})
        os_info = environment.get("os", {})
        kernel_info = environment.get("kernel", {})
        cpu_info = environment.get("cpu", {})
        memory_info = environment.get("memory", {})
        disk_info = environment.get("disk", {})

        compatibility = self.result.get("compatibility", {})
        summary = self.result.get("summary", {})

        tests = self.result.get("tests", [])

        overall_status = self.result.get(
            "status",
            "UNKNOWN",
        )

        compatibility_status = compatibility.get(
            "status",
            "UNKNOWN",
        )

        supported = compatibility.get(
            "supported",
            False,
        )

        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)

        if total:
            pass_rate = round(
                passed / total * 100,
                1,
            )
        else:
            pass_rate = 0

        html_parts = []

        html_parts.append(
            "<!DOCTYPE html>"
        )

        html_parts.append(
            '<html lang="en">'
        )

        html_parts.append("<head>")

        html_parts.append(
            '<meta charset="UTF-8">'
        )

        html_parts.append(
            '<meta name="viewport" '
            'content="width=device-width, initial-scale=1.0">'
        )

        html_parts.append(
            "<title>"
            "Linux OS Compatibility Test Report"
            "</title>"
        )

        html_parts.append(
            """
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f3f4f6;
    color: #111827;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}

.container {
    width: min(1380px, calc(100% - 40px));
    margin: 30px auto 50px;
}

.header {
    background: #111827;
    color: white;
    border-radius: 16px;
    padding: 32px;
    margin-bottom: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.header-top {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    align-items: flex-start;
}

.header h1 {
    margin: 0;
    font-size: 30px;
    letter-spacing: -0.5px;
}

.header-subtitle {
    margin-top: 8px;
    color: #cbd5e1;
}

.timestamp {
    margin-top: 16px;
    color: #94a3b8;
    font-size: 13px;
}

.status-banner {
    margin-top: 25px;
    padding: 18px 20px;
    border-radius: 12px;
    font-size: 22px;
    font-weight: 800;
}

.status-banner.pass {
    background: #14532d;
    color: #bbf7d0;
}

.status-banner.fail {
    background: #7f1d1d;
    color: #fecaca;
}

.status-banner.warn {
    background: #78350f;
    color: #fde68a;
}

.status-banner.unknown {
    background: #374151;
    color: #e5e7eb;
}

.section {
    background: white;
    border-radius: 14px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.05);
}

.section h2 {
    margin: 0 0 20px;
    font-size: 20px;
}

.dashboard {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(170px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
}

.metric {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e5e7eb;
}

.metric-number {
    font-size: 32px;
    font-weight: 800;
}

.metric-label {
    margin-top: 5px;
    color: #6b7280;
    font-size: 14px;
}

.metric.pass .metric-number {
    color: #16a34a;
}

.metric.fail .metric-number {
    color: #dc2626;
}

.metric.skip .metric-number {
    color: #6b7280;
}

.metric.rate .metric-number {
    color: #2563eb;
}

.environment-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
}

.info-card {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px;
}

.info-label {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 6px;
}

.info-value {
    font-size: 15px;
    font-weight: 650;
    word-break: break-word;
}

.compatibility-summary {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
}

.badge-pass {
    background: #dcfce7;
    color: #166534;
}

.badge-fail {
    background: #fee2e2;
    color: #991b1b;
}

.badge-warn {
    background: #fef3c7;
    color: #92400e;
}

.badge-skip {
    background: #e5e7eb;
    color: #374151;
}

.badge-unknown {
    background: #e5e7eb;
    color: #374151;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    border-bottom: 1px solid #e5e7eb;
    padding: 12px 10px;
    text-align: left;
    vertical-align: top;
}

th {
    background: #f8fafc;
    color: #475569;
    font-size: 13px;
}

tr:hover {
    background: #fafafa;
}

.toolbar {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 18px;
}

.filter-btn,
.search-input {
    border: 1px solid #d1d5db;
    background: white;
    border-radius: 8px;
    padding: 9px 13px;
    font-size: 14px;
}

.filter-btn {
    cursor: pointer;
}

.filter-btn.active {
    background: #111827;
    color: white;
    border-color: #111827;
}

.search-input {
    min-width: 260px;
    flex: 1;
}

.test-row {
    transition: opacity 0.15s ease;
}

.test-details {
    display: none;
}

.test-details.open {
    display: table-row;
}

.details-box {
    background: #f8fafc;
    border-radius: 10px;
    padding: 15px;
    margin: 5px 0;
}

.detail-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
}

.detail-item {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px;
}

.detail-label {
    font-size: 12px;
    color: #64748b;
}

.detail-value {
    margin-top: 4px;
    font-size: 13px;
    word-break: break-word;
}

.expand-btn {
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 16px;
    margin-right: 7px;
}

.diagnosis-card {
    border: 1px solid #fecaca;
    background: #fff7f7;
    border-radius: 10px;
    padding: 18px;
    margin-bottom: 12px;
}

.diagnosis-title {
    font-weight: 800;
    color: #991b1b;
}

.diagnosis-meta {
    margin-top: 8px;
    font-size: 13px;
    color: #6b7280;
}

.diagnosis-message {
    margin-top: 10px;
}

.diagnosis-suggestion {
    margin-top: 10px;
    padding: 10px;
    background: #fff;
    border-radius: 8px;
    border: 1px solid #fecaca;
}

.conclusion {
    padding: 18px;
    border-left: 5px solid #2563eb;
    background: #eff6ff;
    border-radius: 8px;
}

.footer {
    text-align: center;
    color: #6b7280;
    padding: 25px;
    font-size: 13px;
}

.empty {
    padding: 20px;
    text-align: center;
    color: #6b7280;
}

pre {
    white-space: pre-wrap;
    word-break: break-word;
    margin: 0;
}

@media (max-width: 700px) {
    .container {
        width: calc(100% - 20px);
        margin-top: 10px;
    }

    .header {
        padding: 22px;
    }

    .header-top {
        flex-direction: column;
    }

    .section {
        padding: 18px;
        overflow-x: auto;
    }

    table {
        min-width: 760px;
    }

    .search-input {
        min-width: 100%;
    }
}
</style>
"""
        )

        html_parts.append("</head>")
        html_parts.append("<body>")

        html_parts.append(
            '<div class="container">'
        )

        # Header
        overall_class = self._status_class(
            overall_status
        )

        html_parts.append(
            '<div class="header">'
        )

        html_parts.append(
            '<div class="header-top">'
        )

        html_parts.append(
            "<div>"
            "<h1>Linux OS Compatibility Test Report</h1>"
            '<div class="header-subtitle">'
            "Linux / Domestic OS Application "
            "Compatibility Automation Testing Tool"
            "</div>"
            "</div>"
        )

        html_parts.append(
            f'<span class="badge badge-{overall_class}">'
            f"{self._escape(overall_status)}"
            "</span>"
        )

        html_parts.append(
            "</div>"
        )

        html_parts.append(
            '<div class="timestamp">'
            "Generated at: "
            f"{self._escape(self.result.get('timestamp', ''))}"
            "</div>"
        )

        html_parts.append(
            f'<div class="status-banner {overall_class}">'
            f"{self._status_icon(overall_status)} "
            f"Overall Result: "
            f"{self._escape(overall_status)}"
            "</div>"
        )

        html_parts.append("</div>")

        # Dashboard
        html_parts.append(
            '<div class="dashboard">'
        )

        metrics = [
            ("Total Tests", total, ""),
            ("Passed", passed, "pass"),
            ("Failed", failed, "fail"),
            ("Skipped", skipped, "skip"),
            ("Pass Rate", f"{pass_rate}%", "rate"),
        ]

        for label, value, css_class in metrics:
            html_parts.append(
                f'<div class="metric {css_class}">'
                f'<div class="metric-number">'
                f"{self._escape(value)}"
                "</div>"
                f'<div class="metric-label">'
                f"{self._escape(label)}"
                "</div>"
                "</div>"
            )

        html_parts.append("</div>")

        # Environment
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Environment</h2>"
        )

        html_parts.append(
            '<div class="environment-grid">'
        )

        environment_items = [
            (
                "Operating System",
                os_info.get(
                    "pretty_name",
                    "Unknown",
                ),
            ),
            (
                "OS ID",
                os_info.get(
                    "id",
                    "Unknown",
                ),
            ),
            (
                "Architecture",
                cpu_info.get(
                    "architecture",
                    "Unknown",
                ),
            ),
            (
                "Kernel",
                kernel_info.get(
                    "release",
                    "Unknown",
                ),
            ),
            (
                "CPU",
                cpu_info.get(
                    "model_name",
                    "Unknown",
                ),
            ),
            (
                "Logical CPUs",
                cpu_info.get(
                    "logical_cpus",
                    "Unknown",
                ),
            ),
            (
                "Memory",
                f"{memory_info.get('total_mb', 0)} MB",
            ),
            (
                "Available Memory",
                f"{memory_info.get('available_mb', 0)} MB",
            ),
            (
                "Disk Available",
                f"{round(
                    disk_info.get('available_bytes', 0)
                    / (1024 * 1024 * 1024),
                    2
                )} GB",
            ),
        ]

        for label, value in environment_items:
            html_parts.append(
                '<div class="info-card">'
                '<div class="info-label">'
                f"{self._escape(label)}"
                "</div>"
                '<div class="info-value">'
                f"{self._escape(value)}"
                "</div>"
                "</div>"
            )

        html_parts.append("</div>")
        html_parts.append("</div>")

        # Compatibility
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Compatibility Result</h2>"
        )

        compatibility_class = self._status_class(
            compatibility_status
        )

        supported_text = (
            "SUPPORTED"
            if supported
            else "NOT SUPPORTED"
        )

        supported_class = (
            "pass"
            if supported
            else "fail"
        )

        html_parts.append(
            '<div class="compatibility-summary">'
            f'<span class="badge badge-{compatibility_class}">'
            f"Status: "
            f"{self._escape(compatibility_status)}"
            "</span>"
            f'<span class="badge badge-{supported_class}">'
            f"{supported_text}"
            "</span>"
            "</div>"
        )

        html_parts.append(
            "<table>"
            "<thead>"
            "<tr>"
            "<th>Check</th>"
            "<th>Status</th>"
            "<th>Message</th>"
            "</tr>"
            "</thead>"
            "<tbody>"
        )

        for check in compatibility.get(
            "checks",
            [],
        ):
            check_status = check.get(
                "status",
                "UNKNOWN",
            )

            check_class = self._status_class(
                check_status
            )

            html_parts.append(
                "<tr>"
                f"<td>{self._escape(check.get('name', ''))}</td>"
                f'<td><span class="badge badge-{check_class}">'
                f"{self._status_icon(check_status)} "
                f"{self._escape(check_status)}"
                "</span></td>"
                f"<td>{self._escape(check.get('message', ''))}</td>"
                "</tr>"
            )

        html_parts.append(
            "</tbody>"
            "</table>"
        )

        html_parts.append("</div>")

        # Test cases
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Test Cases</h2>"
        )

        html_parts.append(
            '<div class="toolbar">'
            '<button class="filter-btn active" '
            'onclick="filterTests(\'ALL\', this)">All</button>'
            '<button class="filter-btn" '
            'onclick="filterTests(\'PASS\', this)">Pass</button>'
            '<button class="filter-btn" '
            'onclick="filterTests(\'FAIL\', this)">Fail</button>'
            '<button class="filter-btn" '
            'onclick="filterTests(\'SKIP\', this)">Skip</button>'
            '<input id="testSearch" '
            'class="search-input" '
            'type="text" '
            'placeholder="Search test name, category or message..." '
            'oninput="searchTests()">'
            "</div>"
        )

        html_parts.append(
            '<table id="testTable">'
            "<thead>"
            "<tr>"
            "<th>Test</th>"
            "<th>Category</th>"
            "<th>Status</th>"
            "<th>Message</th>"
            "</tr>"
            "</thead>"
            "<tbody>"
        )

        for index, test in enumerate(tests):
            test_status = test.get(
                "status",
                "UNKNOWN",
            )

            test_class = self._status_class(
                test_status
            )

            test_name = test.get(
                "name",
                "",
            )

            category = test.get(
                "category",
                "",
            )

            message = test.get(
                "message",
                "",
            )

            test_json = json.dumps(
                test,
                ensure_ascii=False,
                indent=2,
            )

            html_parts.append(
                f'<tr class="test-row" '
                f'data-status="{self._escape(test_status)}" '
                f'data-search="{self._escape(
                    str(test_name) + " "
                    + str(category) + " "
                    + str(message)
                ).lower()}">'
                "<td>"
                f'<button class="expand-btn" '
                f'onclick="toggleDetails({index})">'
                "＋"
                "</button>"
                f"{self._escape(test_name)}"
                "</td>"
                f"<td>{self._escape(category)}</td>"
                f'<td><span class="badge badge-{test_class}">'
                f"{self._status_icon(test_status)} "
                f"{self._escape(test_status)}"
                "</span></td>"
                f"<td>{self._escape(message)}</td>"
                "</tr>"
            )

            html_parts.append(
                f'<tr id="details-{index}" '
                'class="test-details">'
                '<td colspan="4">'
                '<div class="details-box">'
                '<div class="detail-grid">'
                '<div class="detail-item">'
                '<div class="detail-label">Test Name</div>'
                '<div class="detail-value">'
                f"{self._escape(test_name)}"
                "</div>"
                "</div>"
                '<div class="detail-item">'
                '<div class="detail-label">Category</div>'
                '<div class="detail-value">'
                f"{self._escape(category)}"
                "</div>"
                "</div>"
                '<div class="detail-item">'
                '<div class="detail-label">Started</div>'
                '<div class="detail-value">'
                f"{self._escape(test.get('started_at', ''))}"
                "</div>"
                "</div>"
                '<div class="detail-item">'
                '<div class="detail-label">Finished</div>'
                '<div class="detail-value">'
                f"{self._escape(test.get('finished_at', ''))}"
                "</div>"
                "</div>"
                "</div>"
                "<br>"
                "<strong>Raw Test Result</strong>"
                "<pre>"
                f"{self._escape(test_json)}"
                "</pre>"
                "</div>"
                "</td>"
                "</tr>"
            )

        if not tests:
            html_parts.append(
                '<tr><td colspan="4" class="empty">'
                "No test cases were executed."
                "</td></tr>"
            )

        html_parts.append(
            "</tbody>"
            "</table>"
        )

        html_parts.append("</div>")

        # Failure / Diagnosis
        findings = []

        for test in tests:
            log_analysis = test.get(
                "log_analysis"
            )

            if log_analysis:
                findings.extend(
                    log_analysis.get(
                        "findings",
                        [],
                    )
                )

            diagnosis = test.get(
                "diagnosis"
            )

            if isinstance(diagnosis, dict):
                findings.append(diagnosis)

            test_findings = test.get(
                "findings"
            )

            if isinstance(test_findings, list):
                findings.extend(test_findings)

        diagnostics = self.result.get(
            "diagnostics"
        )

        if isinstance(diagnostics, dict):
            findings.extend(
                diagnostics.get(
                    "findings",
                    [],
                )
            )

        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Failure Diagnosis & Findings</h2>"
        )

        if not findings:
            html_parts.append(
                '<div class="empty">'
                "No failure or compatibility findings detected."
                "</div>"
            )

        else:
            for finding in findings:
                severity = finding.get(
                    "severity",
                    "UNKNOWN",
                )

                severity_class = self._status_class(
                    "FAIL"
                    if severity.upper()
                    in ("CRITICAL", "HIGH")
                    else "WARN"
                )

                code = finding.get(
                    "code",
                    "UNCLASSIFIED",
                )

                category = finding.get(
                    "category",
                    "UNKNOWN",
                )

                message = finding.get(
                    "message",
                    "",
                )

                diagnosis = finding.get(
                    "diagnosis",
                    finding.get(
                        "reason",
                        "",
                    ),
                )

                suggestion = finding.get(
                    "suggestion",
                    "",
                )

                html_parts.append(
                    '<div class="diagnosis-card">'
                    '<div class="diagnosis-title">'
                    f"{self._escape(code)}"
                    "</div>"
                    '<div class="diagnosis-meta">'
                    f"Severity: "
                    f"{self._escape(severity)}"
                    " · Category: "
                    f"{self._escape(category)}"
                    "</div>"
                    '<div class="diagnosis-message">'
                    f"<strong>Message:</strong> "
                    f"{self._escape(message)}"
                    "</div>"
                    '<div class="diagnosis-message">'
                    f"<strong>Diagnosis:</strong> "
                    f"{self._escape(diagnosis)}"
                    "</div>"
                    '<div class="diagnosis-suggestion">'
                    f"<strong>Suggestion:</strong> "
                    f"{self._escape(suggestion)}"
                    "</div>"
                    "</div>"
                )

        html_parts.append("</div>")

        # Application logs
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Application Log Analysis</h2>"
        )

        deployment_tests = [
            test
            for test in tests
            if test.get("log_analysis") is not None
        ]

        if not deployment_tests:
            html_parts.append(
                '<div class="empty">'
                "No application deployment log analysis "
                "was generated."
                "</div>"
            )

        else:
            for test in deployment_tests:
                application = test.get(
                    "application",
                    "Unknown",
                )

                log_analysis = test.get(
                    "log_analysis",
                    {},
                )

                log_summary = log_analysis.get(
                    "summary",
                    {},
                )

                html_parts.append(
                    f"<h3>{self._escape(application)}</h3>"
                )

                html_parts.append(
                    '<div class="compatibility-summary">'
                    f'<span class="badge badge-'
                    f'{self._status_class(log_summary.get("status"))}">'
                    f"Status: "
                    f"{self._escape(log_summary.get('status', 'UNKNOWN'))}"
                    "</span>"
                    f'<span class="badge badge-unknown">'
                    f"Findings: "
                    f"{self._escape(log_summary.get('total', 0))}"
                    "</span>"
                    "</div>"
                )

                log_findings = log_analysis.get(
                    "findings",
                    [],
                )

                if not log_findings:
                    html_parts.append(
                        '<div class="empty">'
                        "No compatibility-related "
                        "log findings detected."
                        "</div>"
                    )

                else:
                    html_parts.append(
                        "<table>"
                        "<thead>"
                        "<tr>"
                        "<th>Severity</th>"
                        "<th>Category</th>"
                        "<th>Message</th>"
                        "<th>Reason</th>"
                        "<th>Suggestion</th>"
                        "</tr>"
                        "</thead>"
                        "<tbody>"
                    )

                    for finding in log_findings:
                        html_parts.append(
                            "<tr>"
                            f"<td>{self._escape(finding.get('severity', ''))}</td>"
                            f"<td>{self._escape(finding.get('category', ''))}</td>"
                            f"<td>{self._escape(finding.get('message', ''))}</td>"
                            f"<td>{self._escape(finding.get('reason', ''))}</td>"
                            f"<td>{self._escape(finding.get('suggestion', ''))}</td>"
                            "</tr>"
                        )

                    html_parts.append(
                        "</tbody>"
                        "</table>"
                    )

        html_parts.append("</div>")

        # Conclusion
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Conclusion</h2>"
        )

        html_parts.append(
            '<div class="conclusion">'
        )

        if supported:
            conclusion = (
                "The current environment satisfies "
                "the configured compatibility requirements. "
                f"{passed} of {total} configured tests passed."
            )
        else:
            conclusion = (
                "The current environment does not satisfy "
                "the configured compatibility requirements. "
                "Review the failed checks and diagnostic findings."
            )

        html_parts.append(
            self._escape(conclusion)
        )

        html_parts.append(
            "</div>"
        )

        html_parts.append("</div>")

        # Footer
        html_parts.append(
            '<div class="footer">'
            "Linux / Domestic OS Application "
            "Compatibility Automation Testing Tool"
            "</div>"
        )

        html_parts.append(
            "</div>"
        )

        # JavaScript
        html_parts.append(
            """
<script>
let currentFilter = "ALL";

function filterTests(status, button) {
    currentFilter = status;

    document
        .querySelectorAll(".filter-btn")
        .forEach(function(btn) {
            btn.classList.remove("active");
        });

    button.classList.add("active");

    applyFilters();
}

function searchTests() {
    applyFilters();
}

function applyFilters() {
    const query = (
        document.getElementById("testSearch").value || ""
    ).toLowerCase();

    document
        .querySelectorAll(".test-row")
        .forEach(function(row) {
            const status = row.dataset.status;
            const text = row.dataset.search || "";

            const statusMatch =
                currentFilter === "ALL" ||
                status === currentFilter;

            const searchMatch =
                !query ||
                text.includes(query);

            row.style.display =
                statusMatch && searchMatch
                    ? ""
                    : "none";

            const details =
                row.nextElementSibling;

            if (details) {
                details.style.display =
                    statusMatch && searchMatch
                        ? ""
                        : "none";
            }
        });
}

function toggleDetails(index) {
    const row =
        document.getElementById("details-" + index);

    if (!row) {
        return;
    }

    row.classList.toggle("open");
}
</script>
"""
        )

        html_parts.append(
            "</body>"
        )

        html_parts.append(
            "</html>"
        )

        report_file.write_text(
            "\n".join(html_parts),
            encoding="utf-8",
        )

        return report_file
