#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path

from testcase.base import TestCase
from compatibility.platform import PlatformDetector


class ApplicationCompatibilityTest(TestCase):
    """Validate application requirements against the current Linux environment."""

    def __init__(self, application_name="demo-java-app"):
        super().__init__(
            name="application_compatibility",
            category="compatibility",
            description=(
                "Validate application runtime and platform requirements "
                "against the current Linux environment."
            ),
            tags=[
                "application",
                "compatibility",
                "os",
                "architecture",
                "java",
            ],
        )

        self.application_name = application_name

    def _load_profile(self):
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
            self.application_name
        )

        if profile is None:
            raise ValueError(
                f"Application profile "
                f"'{self.application_name}' "
                f"is not configured."
            )

        return profile

    def _get_java_major_version(self):
        result = subprocess.run(
            [
                "java",
                "-version",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Unable to execute Java."
            )

        import re

        match = re.search(
            r'version "(\d+)(?:\.(\d+))?',
            output,
        )

        if not match:
            raise RuntimeError(
                "Unable to determine Java major version."
            )

        return int(match.group(1))

    def execute(self):
        checks = []

        profile = self._load_profile()
        requirements = profile.get(
            "requirements",
            {},
        )

        platform_info = PlatformDetector().detect()

        os_info = platform_info.get(
            "os",
            {},
        )

        architecture_info = platform_info.get(
            "architecture",
            {},
        )

        current_os = os_info.get(
            "id",
            "unknown",
        )

        current_architecture = architecture_info.get(
            "normalized",
            "unknown",
        )

        required_os = (
            requirements
            .get("os", {})
            .get("supported", [])
        )

        required_architectures = (
            requirements
            .get("architectures", {})
            .get("supported", [])
        )

        java_requirements = (
            requirements
            .get("runtime", {})
            .get("java", {})
        )

        java_required = java_requirements.get(
            "required",
            False,
        )

        minimum_java = java_requirements.get(
            "minimum_major_version",
            0,
        )

        # ---------------------------------------------------------
        # 1. Operating system compatibility
        # ---------------------------------------------------------

        os_pass = current_os in required_os

        checks.append({
            "name": "os",
            "status": (
                "PASS"
                if os_pass
                else "FAIL"
            ),
            "current": current_os,
            "required": required_os,
        })

        if not os_pass:
            return {
                "status": "FAIL",
                "message": (
                    f"Operating system '{current_os}' "
                    "is not supported by the application."
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "application": self.application_name,
                "checks": checks,
                "profile": profile,
                "platform": platform_info,
            }

        # ---------------------------------------------------------
        # 2. CPU architecture compatibility
        # ---------------------------------------------------------

        architecture_pass = (
            current_architecture
            in required_architectures
        )

        checks.append({
            "name": "architecture",
            "status": (
                "PASS"
                if architecture_pass
                else "FAIL"
            ),
            "current": current_architecture,
            "required": required_architectures,
        })

        if not architecture_pass:
            return {
                "status": "FAIL",
                "message": (
                    f"Architecture '{current_architecture}' "
                    "is not supported by the application."
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "application": self.application_name,
                "checks": checks,
                "profile": profile,
                "platform": platform_info,
            }

        # ---------------------------------------------------------
        # 3. Java runtime compatibility
        # ---------------------------------------------------------

        if java_required:
            current_java = self._get_java_major_version()

            java_pass = (
                current_java >= minimum_java
            )

            checks.append({
                "name": "java",
                "status": (
                    "PASS"
                    if java_pass
                    else "FAIL"
                ),
                "current": current_java,
                "required_minimum": minimum_java,
            })

            if not java_pass:
                return {
                    "status": "FAIL",
                    "message": (
                        f"Java {current_java} does not "
                        f"meet the minimum required "
                        f"version {minimum_java}."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "application": self.application_name,
                    "checks": checks,
                    "profile": profile,
                    "platform": platform_info,
                }

        # ---------------------------------------------------------
        # 4. Compatibility result
        #
        # Port availability, HTTP health and API checks are
        # intentionally handled by DeploymentTest.
        # ApplicationCompatibilityTest only validates whether
        # the current environment satisfies the application's
        # declared platform and runtime requirements.
        # ---------------------------------------------------------

        return {
            "status": "PASS",
            "message": (
                f"Application "
                f"{self.application_name} "
                "is compatible with the current environment."
            ),
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "application": self.application_name,
            "checks": checks,
            "profile": profile,
            "platform": platform_info,
        }
