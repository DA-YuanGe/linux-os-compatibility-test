#!/usr/bin/env python3

import html
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
        return status.lower()

    def generate_markdown(self):
        report_file = self.report_dir / "result.md"

        environment = self.result.get(
            "environment",
            {},
        )

        os_info = environment.get(
            "os",
            {},
        )

        cpu_info = environment.get(
            "cpu",
            {},
        )

        memory_info = environment.get(
            "memory",
            {},
        )

        disk_info = environment.get(
            "disk",
            {},
        )

        compatibility = self.result.get(
            "compatibility",
            {},
        )

        lines = []

        lines.append(
            "# Linux OS Compatibility Test Report"
        )
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
            f"- OS: "
            f"{os_info.get('pretty_name', 'Unknown')}"
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

        lines.append(
            "| Check | Status | Message |"
        )
        lines.append(
            "|---|---|---|"
        )

        for check in compatibility.get(
            "checks",
            [],
        ):
            lines.append(
                f"| {check.get('name', '')} "
                f"| {check.get('status', '')} "
                f"| {check.get('message', '')} |"
            )

        lines.append("")

        summary = self.result.get(
            "summary",
            {},
        )

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

        lines.append(
            "|---|---|---|---|"
        )

        for test in self.result.get(
            "tests",
            [],
        ):
            lines.append(
                f"| {test.get('name', '')} "
                f"| {test.get('category', '')} "
                f"| {test.get('status', '')} "
                f"| {test.get('message', '')} |"
            )

        lines.append("")

        # Application Log Analysis
        lines.append("## Application Log Analysis")
        lines.append("")

        deployment_tests = [
            test
            for test in self.result.get(
                "tests",
                [],
            )
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

                lines.append(
                    f"### {application}"
                )
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

        environment = self.result.get(
            "environment",
            {},
        )

        os_info = environment.get(
            "os",
            {},
        )

        kernel_info = environment.get(
            "kernel",
            {},
        )

        cpu_info = environment.get(
            "cpu",
            {},
        )

        memory_info = environment.get(
            "memory",
            {},
        )

        disk_info = environment.get(
            "disk",
            {},
        )

        compatibility = self.result.get(
            "compatibility",
            {},
        )

        summary = self.result.get(
            "summary",
            {},
        )

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

        html_parts = []

        html_parts.append(
            "<!DOCTYPE html>"
        )

        html_parts.append(
            '<html lang="en">'
        )

        html_parts.append(
            "<head>"
        )

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
    padding: 0;
    background: #f4f6f8;
    color: #1f2937;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.container {
    max-width: 1200px;
    margin: 40px auto;
    padding: 0 20px;
}

.header {
    background: #ffffff;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

.header h1 {
    margin: 0 0 10px;
    font-size: 28px;
}

.timestamp {
    color: #6b7280;
}

.status-banner {
    margin-top: 20px;
    padding: 18px;
    border-radius: 10px;
    font-size: 22px;
    font-weight: 700;
}

.status-pass {
    background: #dcfce7;
    color: #166534;
}

.status-fail {
    background: #fee2e2;
    color: #991b1b;
}

.status-warn {
    background: #fef3c7;
    color: #92400e;
}

.status-unknown {
    background: #e5e7eb;
    color: #374151;
}

.section {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

.section h2 {
    margin-top: 0;
}

.environment-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
}

.info-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
}

.info-label {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 6px;
}

.info-value {
    font-size: 16px;
    font-weight: 600;
    word-break: break-word;
}

.summary-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
}

.summary-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 18px;
    text-align: center;
}

.summary-number {
    font-size: 30px;
    font-weight: 700;
}

.summary-label {
    color: #6b7280;
    margin-top: 5px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    border-bottom: 1px solid #e5e7eb;
    padding: 12px;
    text-align: left;
    vertical-align: top;
}

th {
    background: #f9fafb;
}

.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
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

.conclusion {
    padding: 18px;
    border-left: 5px solid #6b7280;
    background: #f9fafb;
}

.footer {
    text-align: center;
    color: #6b7280;
    padding: 20px;
}

@media (max-width: 700px) {
    .container {
        margin: 20px auto;
    }

    .section {
        padding: 16px;
        overflow-x: auto;
    }

    table {
        min-width: 700px;
    }
}
</style>
"""
        )

        html_parts.append(
            "</head>"
        )

        html_parts.append(
            "<body>"
        )

        html_parts.append(
            '<div class="container">'
        )

        html_parts.append(
            '<div class="header">'
        )

        html_parts.append(
            "<h1>"
            "Linux OS Compatibility Test Report"
            "</h1>"
        )

        html_parts.append(
            '<div class="timestamp">'
            "Generated at: "
            f"{self._escape(self.result.get('timestamp', ''))}"
            "</div>"
        )

        overall_class = (
            self._status_class(overall_status)
        )

        html_parts.append(
            '<div class="status-banner '
            f'status-{overall_class}">'
            "Overall Result: "
            f"{self._escape(overall_status)}"
            "</div>"
        )

        html_parts.append(
            "</div>"
        )

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
            )

            html_parts.append(
                '<div class="info-label">'
                f"{self._escape(label)}"
                "</div>"
            )

            html_parts.append(
                '<div class="info-value">'
                f"{self._escape(value)}"
                "</div>"
            )

            html_parts.append(
                "</div>"
            )

        html_parts.append(
            "</div>"
        )

        html_parts.append(
            "</div>"
        )

        # Compatibility
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Compatibility Result</h2>"
        )

        compatibility_class = (
            self._status_class(
                compatibility_status
            )
        )

        html_parts.append(
            f'<p><strong>Status:</strong> '
            f'<span class="badge badge-{compatibility_class}">'
            f"{self._escape(compatibility_status)}"
            "</span></p>"
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
            f'<p><strong>Compatibility:</strong> '
            f'<span class="badge badge-{supported_class}">'
            f"{supported_text}"
            "</span></p>"
        )

        html_parts.append(
            "<table>"
        )

        html_parts.append(
            "<thead>"
            "<tr>"
            "<th>Check</th>"
            "<th>Status</th>"
            "<th>Message</th>"
            "</tr>"
            "</thead>"
        )

        html_parts.append(
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

            check_class = (
                self._status_class(
                    check_status
                )
            )

            html_parts.append(
                "<tr>"
                f"<td>{self._escape(check.get('name', ''))}</td>"
                f'<td><span class="badge badge-{check_class}">'
                f"{self._escape(check_status)}"
                "</span></td>"
                f"<td>{self._escape(check.get('message', ''))}</td>"
                "</tr>"
            )

        html_parts.append(
            "</tbody>"
        )

        html_parts.append(
            "</table>"
        )

        html_parts.append(
            "</div>"
        )

        # Summary
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Test Summary</h2>"
        )

        html_parts.append(
            '<div class="summary-grid">'
        )

        summary_items = [
            (
                "Total",
                summary.get("total", 0),
            ),
            (
                "PASS",
                summary.get("passed", 0),
            ),
            (
                "FAIL",
                summary.get("failed", 0),
            ),
            (
                "SKIP",
                summary.get("skipped", 0),
            ),
        ]

        for label, value in summary_items:
            html_parts.append(
                '<div class="summary-card">'
            )

            html_parts.append(
                '<div class="summary-number">'
                f"{self._escape(value)}"
                "</div>"
            )

            html_parts.append(
                '<div class="summary-label">'
                f"{self._escape(label)}"
                "</div>"
            )

            html_parts.append(
                "</div>"
            )

        html_parts.append(
            "</div>"
        )

        html_parts.append(
            "</div>"
        )

        # Test cases
        html_parts.append(
            '<div class="section">'
        )

        html_parts.append(
            "<h2>Test Cases</h2>"
        )

        html_parts.append(
            "<table>"
        )

        html_parts.append(
            "<thead>"
            "<tr>"
            "<th>Test</th>"
            "<th>Category</th>"
            "<th>Status</th>"
            "<th>Message</th>"
            "</tr>"
            "</thead>"
        )

        html_parts.append(
            "<tbody>"
        )

        for test in self.result.get(
            "tests",
            [],
        ):
            test_status = test.get(
                "status",
                "UNKNOWN",
            )

            test_class = (
                self._status_class(
                    test_status
                )
            )

            html_parts.append(
                "<tr>"
                f"<td>{self._escape(test.get('name', ''))}</td>"
                f"<td>{self._escape(test.get('category', ''))}</td>"
                f'<td><span class="badge badge-{test_class}">'
                f"{self._escape(test_status)}"
                "</span></td>"
                f"<td>{self._escape(test.get('message', ''))}</td>"
                "</tr>"
            )

        html_parts.append(
            "</tbody>"
        )

        html_parts.append(
            "</table>"
        )

        html_parts.append(
            "</div>"
        )

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
                "the configured compatibility requirements."
            )
        else:
            conclusion = (
                "The current environment does not satisfy "
                "the configured compatibility requirements."
            )

        html_parts.append(
            self._escape(conclusion)
        )

        html_parts.append(
            "</div>"
        )

        html_parts.append(
            "</div>"
        )

        html_parts.append(
            '<div class="footer">'
            "Linux / Domestic OS Application "
            "Compatibility Automation Testing Tool"
            "</div>"
        )

        html_parts.append(
            "</div>"
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
