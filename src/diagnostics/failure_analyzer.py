#!/usr/bin/env python3


class FailureAnalyzer:
    """Analyze failed compatibility test results."""

    def __init__(self):
        self.rules = {
            "java": {
                "category": "RUNTIME",
                "severity": "HIGH",
                "code": "JAVA_VERSION_INCOMPATIBLE",
                "diagnosis": (
                    "The current Java major version does not "
                    "satisfy the application's minimum requirement."
                ),
                "suggestion": (
                    "Install or configure a compatible JDK version "
                    "that satisfies the minimum Java requirement."
                ),
            },
            "memory": {
                "category": "RESOURCE",
                "severity": "HIGH",
                "code": "MEMORY_INSUFFICIENT",
                "diagnosis": (
                    "The available memory is lower than the "
                    "minimum required by the application."
                ),
                "suggestion": (
                    "Increase available memory or reduce the "
                    "application memory requirement."
                ),
            },
            "disk": {
                "category": "RESOURCE",
                "severity": "HIGH",
                "code": "DISK_INSUFFICIENT",
                "diagnosis": (
                    "The available disk space is lower than "
                    "the application's minimum requirement."
                ),
                "suggestion": (
                    "Free disk space or deploy the application "
                    "on a filesystem with sufficient capacity."
                ),
            },
            "os": {
                "category": "PLATFORM",
                "severity": "CRITICAL",
                "code": "OS_UNSUPPORTED",
                "diagnosis": (
                    "The current operating system is not included "
                    "in the application's supported platform list."
                ),
                "suggestion": (
                    "Deploy the application on a supported Linux "
                    "distribution or update its compatibility rules."
                ),
            },
            "architecture": {
                "category": "PLATFORM",
                "severity": "CRITICAL",
                "code": "ARCHITECTURE_UNSUPPORTED",
                "diagnosis": (
                    "The current CPU architecture is not supported "
                    "by the application."
                ),
                "suggestion": (
                    "Deploy the application on a supported CPU "
                    "architecture or provide a compatible build."
                ),
            },
            "application_runtime": {
                "category": "APPLICATION",
                "severity": "CRITICAL",
                "code": "APPLICATION_RUNTIME_FAILED",
                "diagnosis": (
                    "The application could not be started or "
                    "did not pass its runtime health checks."
                ),
                "suggestion": (
                    "Review the application startup output and "
                    "runtime logs, fix the reported problem, "
                    "and execute the compatibility test again."
                ),
            },
        }

    def analyze(self, test_results):
        findings = []

        for result in test_results:
            if result.get("status") != "FAIL":
                continue

            test_name = result.get(
                "name",
                "unknown",
            )

            # Prefer detailed checks when available.
            detailed_findings = self._analyze_checks(
                test_name,
                result,
            )

            if detailed_findings:
                findings.extend(detailed_findings)
                continue

            # Only create a test-level finding when there is
            # no detailed failed check explaining the root cause.
            findings.append(
                self._create_test_level_finding(
                    test_name,
                    result,
                )
            )

        severity_count = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }

        for finding in findings:
            severity = finding.get(
                "severity",
                "MEDIUM",
            )

            if severity in severity_count:
                severity_count[severity] += 1

        status = "FAIL" if findings else "PASS"

        return {
            "status": status,
            "total": len(findings),
            "critical": severity_count["CRITICAL"],
            "high": severity_count["HIGH"],
            "medium": severity_count["MEDIUM"],
            "low": severity_count["LOW"],
            "findings": findings,
        }

    def _analyze_checks(
        self,
        test_name,
        result,
    ):
        checks = result.get(
            "checks",
            [],
        )

        findings = []

        for check in checks:
            if check.get("status") != "FAIL":
                continue

            check_name = check.get(
                "name",
                "unknown",
            )

            rule = self.rules.get(check_name)

            if rule is None:
                findings.append(
                    self._create_unknown_check_finding(
                        test_name,
                        check,
                    )
                )
                continue

            findings.append(
                self._create_rule_finding(
                    test_name,
                    check,
                    rule,
                )
            )

        return findings

    def _create_rule_finding(
        self,
        test_name,
        check,
        rule,
    ):
        check_name = check.get(
            "name",
            "unknown",
        )

        message = check.get(
            "message",
            self._default_message(check_name),
        )

        diagnosis = rule["diagnosis"]

        # Add runtime-specific context when available.
        if check_name == "java":
            current = check.get("current")
            required = check.get(
                "required_minimum"
            )

            if current is not None and required is not None:
                diagnosis = (
                    f"Current Java major version is "
                    f"{current}, while the application "
                    f"requires version {required} or later."
                )

        elif check_name == "memory":
            current = check.get(
                "current_available_mb"
            )
            required = check.get(
                "required_minimum_mb"
            )

            if current is not None and required is not None:
                diagnosis = (
                    f"Available memory is {current} MB, "
                    f"while the application requires at "
                    f"least {required} MB."
                )

        elif check_name == "disk":
            current = check.get(
                "current_free_mb"
            )
            required = check.get(
                "required_minimum_mb"
            )

            if current is not None and required is not None:
                diagnosis = (
                    f"Available disk space is {current} MB, "
                    f"while the application requires at "
                    f"least {required} MB."
                )

        return {
            "test": test_name,
            "check": check_name,
            "category": rule["category"],
            "severity": rule["severity"],
            "code": rule["code"],
            "message": message,
            "diagnosis": diagnosis,
            "suggestion": rule["suggestion"],
        }

    def _create_unknown_check_finding(
        self,
        test_name,
        check,
    ):
        check_name = check.get(
            "name",
            "unknown",
        )

        return {
            "test": test_name,
            "check": check_name,
            "category": "UNKNOWN",
            "severity": "MEDIUM",
            "code": "UNKNOWN_COMPATIBILITY_FAILURE",
            "message": check.get(
                "message",
                "Compatibility check failed.",
            ),
            "diagnosis": (
                "A compatibility check failed, but no "
                "specific diagnostic rule is configured "
                "for this check."
            ),
            "suggestion": (
                "Review the detailed test output and add "
                "a diagnostic rule for this failure type."
            ),
        }

    def _create_test_level_finding(
        self,
        test_name,
        result,
    ):
        category = "APPLICATION"
        severity = "CRITICAL"
        code = "COMPATIBILITY_TEST_FAILED"

        if test_name == "deployment_test":
            category = "DEPLOYMENT"
            code = "DEPLOYMENT_TEST_FAILED"

        elif test_name == "network_compatibility":
            category = "NETWORK"
            severity = "HIGH"
            code = "NETWORK_COMPATIBILITY_FAILED"

        elif test_name == "filesystem_compatibility":
            category = "FILESYSTEM"
            severity = "HIGH"
            code = "FILESYSTEM_COMPATIBILITY_FAILED"

        elif test_name == "permission_compatibility":
            category = "PERMISSION"
            severity = "HIGH"
            code = "PERMISSION_COMPATIBILITY_FAILED"

        elif test_name == "process_compatibility":
            category = "PROCESS"
            severity = "HIGH"
            code = "PROCESS_COMPATIBILITY_FAILED"

        return {
            "test": test_name,
            "check": None,
            "category": category,
            "severity": severity,
            "code": code,
            "message": result.get(
                "message",
                "Compatibility test failed.",
            ),
            "diagnosis": (
                "The compatibility test failed without "
                "providing a more specific failed check."
            ),
            "suggestion": (
                "Review the detailed test result and "
                "application logs, fix the reported "
                "condition, and execute the compatibility "
                "test again."
            ),
        }

    @staticmethod
    def _default_message(check_name):
        return (
            f"Compatibility check '{check_name}' failed."
        )
