#!/usr/bin/env python3

import json
from pathlib import Path

from dependency.checker import DependencyChecker
from testcase.base import TestCase


class DependencyTest(TestCase):
    """Test required application dependencies."""

    def __init__(self, compatibility_rules=None):
        super().__init__()
        self.name = "dependency_check"
        self.category = "dependency"
        self.compatibility_rules = compatibility_rules or {}

    def _load_application_profile(self):
        project_root = Path(__file__).resolve().parents[2]

        profile_file = (
            project_root
            / "configs"
            / "application-profiles.json"
        )

        with profile_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        applications = data.get(
            "applications",
            {},
        )

        profile = applications.get(
            "demo-java-app"
        )

        if profile is None:
            raise ValueError(
                "Application profile 'demo-java-app' "
                "is not configured."
            )

        return profile

    @staticmethod
    def _analyze_failure(item):
        """
        Convert a raw dependency failure into a structured diagnosis.
        """

        name = item.get("name", "unknown")
        message = item.get("message", "")

        # Java runtime failures
        if name == "java":
            if message == "Java runtime not found.":
                return {
                    "category": "dependency",
                    "severity": "HIGH",
                    "reason": (
                        "Java runtime is not available in the current "
                        "environment."
                    ),
                    "details": {
                        "dependency": "java",
                        "required_major_version": item.get(
                            "required_major_version"
                        ),
                    },
                    "suggestion": (
                        "Install a compatible Java runtime and ensure "
                        "the java command is available in PATH."
                    ),
                }

            if message == (
                "Java version is below the minimum requirement."
            ):
                return {
                    "category": "dependency",
                    "severity": "HIGH",
                    "reason": (
                        "The installed Java runtime version is lower "
                        "than the configured minimum requirement."
                    ),
                    "details": {
                        "dependency": "java",
                        "current_version": item.get("version"),
                        "current_major_version": item.get(
                            "major_version"
                        ),
                        "required_major_version": item.get(
                            "required_major_version"
                        ),
                    },
                    "suggestion": (
                        "Install or configure a Java runtime with "
                        "the required major version or higher."
                    ),
                }

            if message == "Java runtime could not be executed.":
                return {
                    "category": "runtime",
                    "severity": "HIGH",
                    "reason": (
                        "The Java runtime is installed but could "
                        "not be executed successfully."
                    ),
                    "details": {
                        "dependency": "java",
                        "path": item.get("path"),
                        "error": item.get("error", ""),
                    },
                    "suggestion": (
                        "Check the Java installation, executable "
                        "permissions, PATH configuration and runtime "
                        "environment."
                    ),
                }

            if message == "Unable to determine Java version.":
                return {
                    "category": "runtime",
                    "severity": "HIGH",
                    "reason": (
                        "The Java runtime is available but its version "
                        "could not be determined."
                    ),
                    "details": {
                        "dependency": "java",
                        "path": item.get("path"),
                    },
                    "suggestion": (
                        "Verify that the installed Java runtime provides "
                        "a standard java -version output."
                    ),
                }

            if message == "Java version check timed out.":
                return {
                    "category": "runtime",
                    "severity": "HIGH",
                    "reason": (
                        "The Java runtime version check timed out."
                    ),
                    "details": {
                        "dependency": "java",
                        "path": item.get("path"),
                    },
                    "suggestion": (
                        "Check the Java runtime installation and "
                        "environment for execution problems."
                    ),
                }

            if message == "Unexpected Java version check error.":
                return {
                    "category": "runtime",
                    "severity": "HIGH",
                    "reason": (
                        "An unexpected error occurred while checking "
                        "the Java runtime."
                    ),
                    "details": {
                        "dependency": "java",
                        "path": item.get("path"),
                        "error": item.get("error", ""),
                    },
                    "suggestion": (
                        "Check the Java runtime installation and "
                        "review the reported error."
                    ),
                }

        # Generic command failures
        if message == "Command not found.":
            return {
                "category": "dependency",
                "severity": "HIGH",
                "reason": (
                    f"Required command '{name}' is not available "
                    "in the current environment."
                ),
                "details": {
                    "dependency": name,
                },
                "suggestion": (
                    f"Install the package providing '{name}' or "
                    "configure PATH so the command is available."
                ),
            }

        # Generic fallback
        return {
            "category": "dependency",
            "severity": "HIGH",
            "reason": (
                f"Required dependency '{name}' failed its "
                "compatibility check."
            ),
            "details": {
                "dependency": name,
                "message": message,
            },
            "suggestion": (
                "Check the dependency installation and runtime "
                "environment."
            ),
        }

    def execute(self):
        checker = DependencyChecker()

        required_commands = [
            "python3",
            "bash",
        ]

        results = checker.check_all(required_commands)

        # Java version requirement is defined by the application profile.
        profile = self._load_application_profile()

        java_requirements = (
            profile
            .get("requirements", {})
            .get("runtime", {})
            .get("java", {})
        )

        minimum_java_version = java_requirements.get(
            "minimum_major_version",
            0,
        )

        java_required = java_requirements.get(
            "required",
            False,
        )

        if java_required:
            java_result = checker.check_java(
                min_major_version=minimum_java_version
            )

            results.append(java_result)

        failed = [
            item
            for item in results
            if item["status"] == "FAIL"
        ]

        result = {
            "status": "FAIL" if failed else "PASS",
            "message": (
                "All required dependencies are available."
                if not failed
                else "Some required dependencies are unavailable."
            ),
            "dependencies": results,
        }

        if failed:
            result["failure_analysis"] = [
                self._analyze_failure(item)
                for item in failed
            ]

        return result
