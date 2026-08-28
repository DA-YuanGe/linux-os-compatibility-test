#!/usr/bin/env python3

import json
import re
import shutil
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
                "Validate application runtime, platform and resource "
                "requirements against the current Linux environment."
            ),
            tags=[
                "application",
                "compatibility",
                "os",
                "architecture",
                "java",
                "memory",
                "disk",
                "resource",
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

        match = re.search(
            r'version "(\d+)(?:\.(\d+))?',
            output,
        )

        if not match:
            raise RuntimeError(
                "Unable to determine Java major version."
            )

        return int(match.group(1))

    def _get_available_memory_mb(self):
        """Return currently available system memory in MB."""

        meminfo = Path("/proc/meminfo")

        if not meminfo.exists():
            raise RuntimeError(
                "Unable to determine available system memory."
            )

        content = meminfo.read_text(
            encoding="utf-8"
        )

        for line in content.splitlines():
            if line.startswith("MemAvailable:"):
                parts = line.split()

                if len(parts) < 2:
                    break

                available_kb = int(parts[1])

                return available_kb // 1024

        raise RuntimeError(
            "MemAvailable information is not available."
        )

    def _get_disk_free_mb(self):
        """Return available disk space for the project filesystem."""

        project_root = Path(__file__).resolve().parents[2]

        usage = shutil.disk_usage(
            project_root
        )

        return usage.free // (1024 * 1024)

    def _build_result(
        self,
        status,
        message,
        checks,
        profile,
        platform_info,
    ):
        return {
            "status": status,
            "message": message,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "application": self.application_name,
            "checks": checks,
            "profile": profile,
            "platform": platform_info,
        }

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

        resource_requirements = requirements.get(
            "resources",
            {},
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
            return self._build_result(
                "FAIL",
                (
                    f"Operating system '{current_os}' "
                    "is not supported by the application."
                ),
                checks,
                profile,
                platform_info,
            )

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
            return self._build_result(
                "FAIL",
                (
                    f"Architecture '{current_architecture}' "
                    "is not supported by the application."
                ),
                checks,
                profile,
                platform_info,
            )

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
                return self._build_result(
                    "FAIL",
                    (
                        f"Java {current_java} does not "
                        f"meet the minimum required "
                        f"version {minimum_java}."
                    ),
                    checks,
                    profile,
                    platform_info,
                )

        # ---------------------------------------------------------
        # 4. Memory compatibility
        # ---------------------------------------------------------

        memory_requirements = resource_requirements.get(
            "memory",
            {}
        )

        minimum_memory_mb = memory_requirements.get(
            "minimum_mb"
        )

        if minimum_memory_mb is not None:
            current_memory_mb = (
                self._get_available_memory_mb()
            )

            memory_pass = (
                current_memory_mb
                >= minimum_memory_mb
            )

            checks.append({
                "name": "memory",
                "status": (
                    "PASS"
                    if memory_pass
                    else "FAIL"
                ),
                "current_available_mb": current_memory_mb,
                "required_minimum_mb": minimum_memory_mb,
            })

            if not memory_pass:
                return self._build_result(
                    "FAIL",
                    (
                        f"Available memory "
                        f"{current_memory_mb} MB does not "
                        f"meet the minimum required "
                        f"{minimum_memory_mb} MB."
                    ),
                    checks,
                    profile,
                    platform_info,
                )

        # ---------------------------------------------------------
        # 5. Disk compatibility
        # ---------------------------------------------------------

        disk_requirements = resource_requirements.get(
            "disk",
            {}
        )

        minimum_free_mb = disk_requirements.get(
            "minimum_free_mb"
        )

        if minimum_free_mb is not None:
            current_free_mb = (
                self._get_disk_free_mb()
            )

            disk_pass = (
                current_free_mb
                >= minimum_free_mb
            )

            checks.append({
                "name": "disk",
                "status": (
                    "PASS"
                    if disk_pass
                    else "FAIL"
                ),
                "current_free_mb": current_free_mb,
                "required_minimum_mb": minimum_free_mb,
            })

            if not disk_pass:
                return self._build_result(
                    "FAIL",
                    (
                        f"Available disk space "
                        f"{current_free_mb} MB does not "
                        f"meet the minimum required "
                        f"{minimum_free_mb} MB."
                    ),
                    checks,
                    profile,
                    platform_info,
                )

        # ---------------------------------------------------------
        # 6. Compatibility result
        #
        # Network port availability, HTTP health and API checks
        # are handled by DeploymentTest.
        #
        # ApplicationCompatibilityTest validates whether the
        # current environment satisfies the application's
        # declared platform, runtime and resource requirements.
        # ---------------------------------------------------------

        return self._build_result(
            "PASS",
            (
                f"Application "
                f"{self.application_name} "
                "is compatible with the current environment."
            ),
            checks,
            profile,
            platform_info,
        )
