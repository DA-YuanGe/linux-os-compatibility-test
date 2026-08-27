#!/usr/bin/env python3

import re
from pathlib import Path


class LogAnalyzer:
    """Analyze application logs and classify compatibility failures."""

    RULES = [
        {
            "name": "java_runtime",
            "category": "Java Runtime Compatibility",
            "severity": "HIGH",
            "patterns": [
                r"UnsupportedClassVersionError",
                r"has been compiled by a more recent version",
            ],
            "reason": (
                "The application was compiled for a newer Java "
                "runtime than the current environment provides."
            ),
            "suggestion": (
                "Check the application's required Java major version "
                "and upgrade the runtime if necessary."
            ),
        },
        {
            "name": "port_conflict",
            "category": "Port Conflict",
            "severity": "HIGH",
            "patterns": [
                r"Address already in use",
                r"BindException",
            ],
            "reason": (
                "The application failed to bind to the required "
                "network port because it is already in use."
            ),
            "suggestion": (
                "Check which process is using the port with "
                "`ss -lntp` or `lsof -i` and release or change the port."
            ),
        },
        {
            "name": "permission",
            "category": "Permission",
            "severity": "HIGH",
            "patterns": [
                r"Permission denied",
                r"AccessDeniedException",
            ],
            "reason": (
                "The application does not have sufficient permission "
                "to access a required file or resource."
            ),
            "suggestion": (
                "Check file ownership and permissions with `ls -l` "
                "and adjust permissions or the service user."
            ),
        },
        {
            "name": "network",
            "category": "Network",
            "severity": "HIGH",
            "patterns": [
                r"Connection refused",
                r"ConnectException",
                r"Connection timed out",
                r"TimeoutException",
            ],
            "reason": (
                "The application could not establish the required "
                "network connection."
            ),
            "suggestion": (
                "Check the target service, network connectivity, "
                "firewall rules and configured host or port."
            ),
        },
        {
            "name": "filesystem",
            "category": "File System",
            "severity": "HIGH",
            "patterns": [
                r"No such file or directory",
                r"FileNotFoundException",
            ],
            "reason": (
                "The application attempted to access a file or "
                "directory that does not exist."
            ),
            "suggestion": (
                "Check the configured file path and verify that "
                "the required file or directory exists."
            ),
        },
        {
            "name": "memory",
            "category": "Memory",
            "severity": "CRITICAL",
            "patterns": [
                r"OutOfMemoryError",
                r"Cannot allocate memory",
                r"CannotCreateNativeThread",
            ],
            "reason": (
                "The application does not have sufficient memory "
                "or system resources to continue execution."
            ),
            "suggestion": (
                "Check available memory and application memory "
                "configuration. Consider increasing available memory "
                "or reducing application resource usage."
            ),
        },
        {
            "name": "java_dependency",
            "category": "Java Dependency",
            "severity": "HIGH",
            "patterns": [
                r"ClassNotFoundException",
                r"NoClassDefFoundError",
            ],
            "reason": (
                "A required Java class or dependency could not be "
                "loaded at runtime."
            ),
            "suggestion": (
                "Check the application's packaged dependencies "
                "and runtime classpath."
            ),
        },
        {
            "name": "python_dependency",
            "category": "Python Dependency",
            "severity": "HIGH",
            "patterns": [
                r"ModuleNotFoundError",
                r"ImportError",
            ],
            "reason": (
                "A required Python module or dependency is missing "
                "from the runtime environment."
            ),
            "suggestion": (
                "Check the application's Python dependencies and "
                "install the required packages."
            ),
        },
    ]

    def __init__(self, log_files=None):
        self.log_files = [
            Path(path)
            for path in (log_files or [])
        ]

    def _match_rule(self, text):
        """
        Match a complete log fragment against the configured rules.

        The whole fragment is checked instead of treating every line
        as an independent finding. This prevents one exception from
        producing multiple duplicate findings.
        """
        for rule in self.RULES:
            for pattern in rule["patterns"]:
                if re.search(
                    pattern,
                    text,
                    re.IGNORECASE,
                ):
                    return rule

        return None

    def _build_log_fragments(self, text):
        """
        Group related exception lines into logical log fragments.

        Java stack traces and multi-line error messages are commonly
        represented by several consecutive lines. We keep the first
        matching line together with the immediately following
        non-empty lines until another obvious exception begins.
        """
        lines = text.splitlines()

        fragments = []
        current = []

        for line in lines:
            stripped = line.strip()

            if not stripped:
                if current:
                    fragments.append(current)
                    current = []
                continue

            current.append(stripped)

        if current:
            fragments.append(current)

        return fragments

    def analyze_text(self, text, source="unknown"):
        findings = []

        fragments = self._build_log_fragments(text)

        current_line = 1

        for fragment in fragments:
            fragment_text = "\n".join(fragment)

            rule = self._match_rule(fragment_text)

            if rule is None:
                current_line += len(fragment) + 1
                continue

            # Prefer the most informative line as the message.
            message = fragment[0]

            if rule["name"] == "java_runtime":
                for line in fragment:
                    if (
                        "UnsupportedClassVersionError" in line
                        or "has been compiled by a more recent version"
                        in line
                    ):
                        message = line
                        break

            findings.append({
                "rule": rule["name"],
                "category": rule["category"],
                "severity": rule["severity"],
                "source": source,
                "line_number": current_line,
                "message": message,
                "reason": rule["reason"],
                "suggestion": rule["suggestion"],
            })

            current_line += len(fragment) + 1

        return findings

    def analyze_file(self, log_file):
        path = Path(log_file)

        if not path.exists():
            return []

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return []

        return self.analyze_text(
            text,
            source=str(path),
        )

    def analyze(self):
        findings = []

        for log_file in self.log_files:
            findings.extend(
                self.analyze_file(log_file)
            )

        severity_order = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3,
        }

        findings.sort(
            key=lambda item: (
                severity_order.get(
                    item["severity"],
                    99,
                ),
                item["source"],
                item["line_number"],
            )
        )

        return findings

    def summarize(self, findings):
        if not findings:
            return {
                "status": "PASS",
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            }

        critical = sum(
            1
            for item in findings
            if item["severity"] == "CRITICAL"
        )

        high = sum(
            1
            for item in findings
            if item["severity"] == "HIGH"
        )

        medium = sum(
            1
            for item in findings
            if item["severity"] == "MEDIUM"
        )

        low = sum(
            1
            for item in findings
            if item["severity"] == "LOW"
        )

        return {
            "status": "FAIL" if findings else "PASS",
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        }
