#!/usr/bin/env python3


class CompatibilityEvaluator:
    """Evaluate application compatibility from collected test results."""

    def __init__(self, rules):
        self.rules = rules or {}

    def evaluate(self, environment, test_results):
        checks = []

        # Platform compatibility
        checks.extend(
            self._evaluate_os(
                environment,
                test_results,
            )
        )

        checks.extend(
            self._evaluate_architecture(
                environment,
                test_results,
            )
        )

        # Application environment requirements
        checks.extend(
            self._evaluate_java(
                test_results,
            )
        )

        checks.extend(
            self._evaluate_memory(
                test_results,
            )
        )

        checks.extend(
            self._evaluate_disk(
                test_results,
            )
        )

        # Deployment requirements
        checks.extend(
            self._evaluate_ports(
                test_results,
            )
        )

        checks.extend(
            self._evaluate_application(
                test_results,
            )
        )

        failed = [
            item
            for item in checks
            if item["status"] == "FAIL"
        ]

        warnings = [
            item
            for item in checks
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
                    1
                    for item in checks
                    if item["status"] == "PASS"
                ),
                "warnings": len(warnings),
                "failed": len(failed),
            },
        }

    # ---------------------------------------------------------
    # OS
    # ---------------------------------------------------------

    def _evaluate_os(
        self,
        environment,
        test_results,
    ):
        os_info = environment.get("os", {})

        current_os = os_info.get(
            "id",
            "unknown",
        ).lower()

        platforms = self.rules.get(
            "platforms",
            {},
        )

        matched_platform = None

        for platform_id, platform_rule in platforms.items():
            supported_ids = [
                str(item).lower()
                for item in platform_rule.get(
                    "ids",
                    [],
                )
            ]

            if current_os in supported_ids:
                matched_platform = platform_id
                break

        if matched_platform is None:
            matched_platform = "generic-linux"

        platform_rule = platforms.get(
            matched_platform,
            {},
        )

        supported = platform_rule.get(
            "supported",
            False,
        )

        if supported:
            return [{
                "name": "os",
                "status": "PASS",
                "message": (
                    "Operating system compatibility "
                    "requirement satisfied."
                ),
                "actual": current_os,
                "family": matched_platform,
                "platform": matched_platform,
                "supported": True,
            }]

        return [{
            "name": "os",
            "status": "FAIL",
            "message": (
                "Operating system compatibility "
                "requirement failed."
            ),
            "actual": current_os,
            "family": matched_platform,
            "platform": matched_platform,
            "supported": False,
        }]

    # ---------------------------------------------------------
    # Architecture
    # ---------------------------------------------------------

    def _evaluate_architecture(
        self,
        environment,
        test_results,
    ):
        for result in test_results:
            if result.get("name") != "platform_compatibility":
                continue

            if result.get("status") == "PASS":
                return [{
                    "name": "architecture",
                    "status": "PASS",
                    "message": (
                        "CPU architecture compatibility "
                        "test passed."
                    ),
                    "actual": result.get("architecture"),
                    "family": result.get(
                        "architecture_id"
                    ),
                }]

            return [{
                "name": "architecture",
                "status": "FAIL",
                "message": (
                    "CPU architecture compatibility "
                    "test failed."
                ),
                "actual": result.get("architecture"),
            }]

        return [{
            "name": "architecture",
            "status": "FAIL",
            "message": (
                "Platform compatibility test result "
                "was not found."
            ),
        }]

    # ---------------------------------------------------------
    # Java
    # ---------------------------------------------------------

    def _evaluate_java(self, test_results):
        """
        Read Java compatibility from the application
        compatibility test result.

        ApplicationCompatibilityTest is the single source
        of truth for application runtime requirements.
        """

        for result in test_results:
            if result.get("name") != "application_compatibility":
                continue

            for check in result.get("checks", []):
                if check.get("name") != "java":
                    continue

                status = check.get(
                    "status",
                    "FAIL",
                )

                return [{
                    "name": "java",
                    "status": status,
                    "message": (
                        "Java runtime compatibility "
                        "requirement satisfied."
                        if status == "PASS"
                        else (
                            "Java runtime compatibility "
                            "requirement failed."
                        )
                    ),
                    "actual_major_version": check.get(
                        "current"
                    ),
                    "required_major_version": check.get(
                        "required_minimum"
                    ),
                }]

        return [{
            "name": "java",
            "status": "FAIL",
            "message": (
                "Application Java compatibility "
                "result was not found."
            ),
        }]

    # ---------------------------------------------------------
    # Memory
    # ---------------------------------------------------------

    def _evaluate_memory(self, test_results):
        for result in test_results:
            if result.get("name") != "application_compatibility":
                continue

            for check in result.get(
                "checks",
                [],
            ):
                if check.get("name") != "memory":
                    continue

                status = check.get(
                    "status",
                    "FAIL",
                )

                return [{
                    "name": "memory",
                    "status": status,
                    "message": (
                        "Application memory "
                        "requirement satisfied."
                        if status == "PASS"
                        else (
                            "Application memory "
                            "requirement failed."
                        )
                    ),
                    "actual_available_mb": check.get(
                        "current_available_mb"
                    ),
                    "required_minimum_mb": check.get(
                        "required_minimum_mb"
                    ),
                }]

        return [{
            "name": "memory",
            "status": "FAIL",
            "message": (
                "Application memory compatibility "
                "result was not found."
            ),
        }]

    # ---------------------------------------------------------
    # Disk
    # ---------------------------------------------------------

    def _evaluate_disk(self, test_results):
        for result in test_results:
            if result.get("name") != "application_compatibility":
                continue

            for check in result.get(
                "checks",
                [],
            ):
                if check.get("name") != "disk":
                    continue

                status = check.get(
                    "status",
                    "FAIL",
                )

                return [{
                    "name": "disk",
                    "status": status,
                    "message": (
                        "Application disk "
                        "requirement satisfied."
                        if status == "PASS"
                        else (
                            "Application disk "
                            "requirement failed."
                        )
                    ),
                    "actual_free_mb": check.get(
                        "current_free_mb"
                    ),
                    "required_minimum_mb": check.get(
                        "required_minimum_mb"
                    ),
                }]

        return [{
            "name": "disk",
            "status": "FAIL",
            "message": (
                "Application disk compatibility "
                "result was not found."
            ),
        }]

    # ---------------------------------------------------------
    # Ports
    # ---------------------------------------------------------

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
            if result.get("name") == "deployment_test"
        ]

        for port in required_ports:
            matched = False

            for result in deployment_results:
                for check in result.get(
                    "checks",
                    [],
                ):
                    if (
                        check.get("name") == "port_check"
                        and check.get("port") == port
                        and check.get("status") == "PASS"
                    ):
                        matched = True
                        break

                if matched:
                    break

            checks.append({
                "name": f"port_{port}",
                "status": (
                    "PASS"
                    if matched
                    else "FAIL"
                ),
                "message": (
                    "Required application port "
                    "is available."
                    if matched
                    else (
                        "Required application port "
                        "check failed."
                    )
                ),
                "port": port,
            })

        return checks

    # ---------------------------------------------------------
    # Application deployment
    # ---------------------------------------------------------

    def _evaluate_application(self, test_results):
        deployment = [
            result
            for result in test_results
            if result.get("name") == "deployment_test"
        ]

        if not deployment:
            return [{
                "name": "application_runtime",
                "status": "FAIL",
                "message": (
                    "Application deployment test "
                    "result was not found."
                ),
            }]

        result = deployment[0]

        if result.get("status") == "PASS":
            return [{
                "name": "application_runtime",
                "status": "PASS",
                "message": (
                    "Application deployment and "
                    "health checks passed."
                ),
            }]

        return [{
            "name": "application_runtime",
            "status": "FAIL",
            "message": (
                "Application deployment or "
                "health checks failed."
            ),
        }]
