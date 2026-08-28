#!/usr/bin/env python3

from testcase.runtime import PythonRuntimeTest
from testcase.command import CommandAvailabilityTest
from testcase.shell import ShellRuntimeTest
from testcase.dependency import DependencyTest
from testcase.os_compatibility import OSCompatibilityTest
from testcase.application import ApplicationRuntimeTest
from testcase.filesystem import FilesystemCompatibilityTest
from testcase.permission import PermissionCompatibilityTest
from testcase.process import ProcessCompatibilityTest
from testcase.network import NetworkCompatibilityTest
from testcase.deployment import DeploymentTest
from testcase.offline_deployment import OfflineDeploymentTest
from testcase.platform_compatibility import PlatformCompatibilityTest
from testcase.application_compatibility import ApplicationCompatibilityTest


class TestRunner:
    """Execute configured compatibility test cases."""

    def __init__(self, config, compatibility_rules=None):
        self.config = config
        self.compatibility_rules = compatibility_rules or {}
        self.test_cases = self._build_test_cases()

    def _build_test_cases(self):
        tests_config = self.config.get(
            "tests",
            {},
        )

        test_cases = []

        # ---------------------------------------------------------
        # Runtime tests
        # ---------------------------------------------------------

        if tests_config.get(
            "python_runtime",
            True,
        ):
            test_cases.append(
                PythonRuntimeTest()
            )

        if tests_config.get(
            "command_availability",
            True,
        ):
            commands = self.config.get(
                "commands",
                [],
            )

            test_cases.append(
                CommandAvailabilityTest(commands)
            )

        if tests_config.get(
            "shell_runtime",
            True,
        ):
            test_cases.append(
                ShellRuntimeTest()
            )

        # ---------------------------------------------------------
        # Dependency / OS compatibility
        # ---------------------------------------------------------

        if tests_config.get(
            "dependency_check",
            True,
        ):
            test_cases.append(
                DependencyTest(
                    self.compatibility_rules
                )
            )

        if tests_config.get(
            "os_compatibility",
            True,
        ):
            supported_os = (
                self.config
                .get(
                    "compatibility",
                    {},
                )
                .get(
                    "supported_os",
                    [],
                )
            )

            test_cases.append(
                OSCompatibilityTest(
                    supported_os
                )
            )

        if tests_config.get(
            "platform_compatibility",
            True,
        ):
            test_cases.append(
                PlatformCompatibilityTest()
            )

        # ---------------------------------------------------------
        # Application compatibility
        # ---------------------------------------------------------

        if tests_config.get(
            "application_compatibility",
            True,
        ):
            deployment_applications = self.config.get(
                "deployment_applications",
                [],
            )

            if deployment_applications:
                application_name = deployment_applications[0].get(
                    "name",
                    "",
                )

                if application_name:
                    test_cases.append(
                        ApplicationCompatibilityTest(
                            application_name
                        )
                    )

        # ---------------------------------------------------------
        # Basic Linux compatibility
        # ---------------------------------------------------------

        if tests_config.get(
            "filesystem_compatibility",
            True,
        ):
            test_cases.append(
                FilesystemCompatibilityTest()
            )

        if tests_config.get(
            "permission_compatibility",
            True,
        ):
            test_cases.append(
                PermissionCompatibilityTest()
            )

        if tests_config.get(
            "process_compatibility",
            True,
        ):
            test_cases.append(
                ProcessCompatibilityTest()
            )

        if tests_config.get(
            "network_compatibility",
            True,
        ):
            test_cases.append(
                NetworkCompatibilityTest()
            )

        # ---------------------------------------------------------
        # Deployment
        # ---------------------------------------------------------

        deployment_applications = self.config.get(
            "deployment_applications",
            [],
        )

        if tests_config.get(
            "deployment",
            tests_config.get(
                "deployment_test",
                True,
            ),
        ):
            for application in deployment_applications:
                test_cases.append(
                    DeploymentTest(application)
                )

        # ---------------------------------------------------------
        # Offline deployment
        # ---------------------------------------------------------

        if tests_config.get(
            "offline_deployment",
            True,
        ):
            test_cases.append(
                OfflineDeploymentTest()
            )

        # ---------------------------------------------------------
        # Application runtime
        # ---------------------------------------------------------

        if tests_config.get(
            "application_runtime",
            True,
        ):
            application = {}

            if deployment_applications:
                application = deployment_applications[0]

            test_cases.append(
                ApplicationRuntimeTest(
                    application
                )
            )

        return test_cases

    def run_all(self):
        results = []

        for test_case in self.test_cases:
            result = test_case.run()
            results.append(result)

        return results
