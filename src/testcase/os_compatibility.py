#!/usr/bin/env python3

import json
from pathlib import Path

from testcase.base import TestCase


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = PROJECT_ROOT / "configs" / "test-case.json"


class OSCompatibilityTest(TestCase):
    """Check whether the current Linux distribution is supported."""

    def __init__(self):
        super().__init__()
        self.name = "os_compatibility"
        self.category = "compatibility"

    def execute(self):
        os_info = {}

        content = Path("/etc/os-release").read_text(encoding="utf-8")

        for line in content.splitlines():
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os_info[key] = value.strip('"')

        current_os = os_info.get("ID", "")

        config = json.loads(
            CONFIG_FILE.read_text(encoding="utf-8")
        )

        supported_os = config.get(
            "compatibility", {}
        ).get(
            "supported_os", []
        )

        if current_os in supported_os:
            return {
                "status": "PASS",
                "message": "Current operating system is supported.",
                "current_os": current_os,
                "supported_os": supported_os,
            }

        return {
            "status": "FAIL",
            "message": "Current operating system is not supported.",
            "current_os": current_os,
            "supported_os": supported_os,
        }
