#!/usr/bin/env python3

from pathlib import Path

from testcase.base import TestCase


class OSCompatibilityTest(TestCase):
    """Check whether the current Linux distribution is supported."""

    def __init__(self, supported_os=None):
        super().__init__(
            name="os_compatibility",
            category="compatibility",
            description="Verify that the current operating system is supported.",
            tags=["compatibility", "os", "config-driven"],
        )

        self.supported_os = supported_os or []

    def execute(self):
        os_info = {}

        content = Path("/etc/os-release").read_text(
            encoding="utf-8"
        )

        for line in content.splitlines():
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os_info[key] = value.strip('"')

        current_os = os_info.get("ID", "")

        if not self.supported_os:
            return {
                "status": "SKIP",
                "message": "No supported operating systems are configured.",
                "current_os": current_os,
                "supported_os": [],
            }

        if current_os in self.supported_os:
            return {
                "status": "PASS",
                "message": "Current operating system is supported.",
                "current_os": current_os,
                "supported_os": self.supported_os,
            }

        return {
            "status": "FAIL",
            "message": "Current operating system is not supported.",
            "current_os": current_os,
            "supported_os": self.supported_os,
        }
