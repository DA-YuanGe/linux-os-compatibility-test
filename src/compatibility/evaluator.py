#!/usr/bin/env python3

from pathlib import Path


class CompatibilityEvaluator:
    """Evaluate whether an application is compatible with the current environment."""

    def __init__(self, rules):
        self.rules = rules or {}

    def evaluate(self, environment, test_results):
        checks = []

        checks.extend(
            self._evaluate_os(environment)
        )

        checks.extend(
            self._evaluate_architecture(environment)
        )

        checks.extend(
            self._evaluate_java(test_results)
        )

        checks.extend(
            self._evaluate_memory(environment)
        )

        checks.extend(
            self._evaluate_disk(environment)
        )

        checks.extend(
            self._evaluate_ports(test_results)
        )

        checks.extend(
            self._evaluate_application(test_results)
        )

        failed = [
            item for item in checks
            if item["status"] == "FAIL"
        ]

        warnings = [
            item for item in checks
            if item["status"] == "WARN"
        ]

        if failed:
            status = "FAIL"
            supported = False
        elif warnings:
            status = "WARN"
            supported = True
        else:
            status = "PASS"
            supported = True

        return {
            "status": status,
            "supported": supported,
            "checks": checks,
            "summary": {
                "total": len(checks),
                "passed": sum(
                    1 for item in checks
                    if item["status"] == "PASS"
                ),
                "warnings": len(warnings),
                "failed": len(failed),
            },
        }

    def _evaluate_os(self, environment):
        rule = self.rules.get("os", {})
        supported = rule.get("supported", [])

        actual = (
            environment
            .get("os", {})
            .get("id", "")
            .lower()
        )

        if not supported:
            return []

        if actual in [
            item.lower()
            for item in supported
        ]:
            return [{
                "name": "os",
                "status": "PASS",
                "message": "Operating system is supported.",
                "actual": actual,
                "supported": supported,
            }]

        return [{
            "name": "os",
            "status": "FAIL",
            "message": "Operating system is not supported.",
            "actual": actual,
            "supported": supported,
        }]

    def _evaluate_architecture(self, environment):
        rule = self.rules.get("architecture", {})
        supported = rule.get("supported", [])

        actual = (
            environment
            .get("cpu", {})
            .get("architecture", "")
            .lower()
        )

        if not supported:
            return []

        if actual in [
            item.lower()
            for item in supported
        ]:
            return [{
                "name": "architecture",
                "status": "PASS",
                "message": "CPU architecture is supported.",
                "actual": actual,
                "supported": supported,
            }]

        return [{
            "name": "architecture",
            "status": "FAIL",
            "message": "CPU architecture is not supported.",
            "actual": actual,
            "supported": supported,
        }]

    def _evaluate_java(self, test_results):
        rule = self.rules.get("java", {})
        minimum = rule.get("min_major_version")

        if minimum is None:
            return []

        for result in test_results:
            if result.get("name") != "dependency_check":
                continue

            for dependency in result.get("dependencies", []):
                if dependency.get("name") != "java":
                    continue

                actual = dependency.get("major_version")

                if actual is None:
                    return [{
                        "name": "java",
                        "status": "FAIL",
                        "message": "Java version could not be determined.",
                    }]

                if actual >= minimum:
                    return [{
                        "name": "java",
                        "status": "PASS",
                        "message": "Java version requirement satisfied.",
                        "actual_major_version": actual,
                        "required_major_version": minimum,
                    }]

                return [{
                    "name": "java",
                    "status": "FAIL",
                    "message": "Java version requirement is not satisfied.",
                    "actual_major_version": actual,
                    "required_major_version": minimum,
                }]

        return [{
            "name": "java",
            "status": "FAIL",
            "message": "Java dependency check result was not found.",
            "required_major_version": minimum,
        }]

    def _evaluate_memory(self, environment):
        rule = self.rules.get("memory", {})
        minimum_mb = rule.get("min_mb")

        if minimum_mb is None:
            return []

        actual_mb = (
            environment
            .get("memory", {})
            .get("total_mb", 0)
        )

        if actual_mb >= minimum_mb:
            return [{
                "name": "memory",
                "status": "PASS",
                "message": "Available system memory satisfies requirement.",
                "actual_mb": actual_mb,
                "required_mb": minimum_mb,
            }]

        return [{
            "name": "memory",
            "status": "FAIL",
            "message": "Available system memory is below requirement.",
            "actual_mb": actual_mb,
            "required_mb": minimum_mb,
        }]

    def _evaluate_disk(self, environment):
        rule = self.rules.get("disk", {})
        minimum_gb = rule.get("min_gb")

        if minimum_gb is None:
            return []

        actual_bytes = (
            environment
            .get("disk", {})
            .get("available_bytes", 0)
        )

        actual_gb = actual_bytes / (
            1024 * 1024 * 1024
        )

        if actual_gb >= minimum_gb:
            return [{
                "name": "disk",
                "status": "PASS",
                "message": "Available disk space satisfies requirement.",
                "actual_gb": round(actual_gb, 2),
                "required_gb": minimum_gb,
            }]

        return [{
            "name": "disk",
            "status": "FAIL",
            "message": "Available disk space is below requirement.",
            "actual_gb": round(actual_gb, 2),
            "required_gb": minimum_gb,
        }]

    def _evaluate_ports(self, test_results):
        required_ports = (
            self.rules
            .get("ports", {})
            .get("required", [])
        )

        if not required_ports:
            return []

        checks = []

        deployment_results = [
            result
            for result in test_results
            if result.get("application")
            == "demo-java-app"
        ]

        for port in required_ports:
            matched = False

            for result in deployment_results:
                for check in result.get("checks", []):
                    if (
                        check.get("name") == "port_check"
                        and check.get("port") == port
                        and check.get("status") == "PASS"
                    ):
                        matched = True
                        break

            if matched:
                checks.append({
                    "name": f"port_{port}",
                    "status": "PASS",
                    "message": "Required application port is available.",
                    "port": port,
                })
            else:
                checks.append({
                    "name": f"port_{port}",
                    "status": "FAIL",
                    "message": "Required application port check failed.",
                    "port": port,
                })

        return checks

    def _evaluate_application(self, test_results):
        deployment = [
            result
            for result in test_results
            if result.get("name") == "application_deployment"
        ]

        if not deployment:
            return []

        result = deployment[0]

        if result.get("status") == "PASS":
            return [{
                "name": "application_runtime",
                "status": "PASS",
                "message": "Application deployment and health checks passed.",
            }]

        return [{
            "name": "application_runtime",
            "status": "FAIL",
            "message": "Application deployment or health checks failed.",
        }]
