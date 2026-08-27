#!/usr/bin/env python3

import shutil
import subprocess

from testcase.base import TestCase


class CommandAvailabilityTest(TestCase):
    """Test availability and execution of configured Linux commands."""

    def __init__(self, commands=None):
        super().__init__(
            name="command_availability",
            category="system",
            description="Verify that configured system commands are available and executable.",
            tags=["system", "command", "config-driven"],
        )

        self.commands = commands or []

    def execute(self):
        if not self.commands:
            return {
                "status": "SKIP",
                "message": "No commands are configured for availability testing.",
                "commands": [],
            }

        results = []

        for command in self.commands:
            command_path = shutil.which(command)

            if command_path is None:
                results.append({
                    "command": command,
                    "status": "FAIL",
                    "message": "Command not found.",
                })
                continue

            try:
                if command in ("sh", "bash"):
                    test_command = [
                        command,
                        "-c",
                        "printf 'compatibility-test-ok\\n'",
                    ]
                else:
                    test_command = [command, "--version"]

                result = subprocess.run(
                    test_command,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                output = (
                    result.stdout.strip()
                    or result.stderr.strip()
                )

                results.append({
                    "command": command,
                    "status": (
                        "PASS"
                        if result.returncode == 0
                        else "FAIL"
                    ),
                    "path": command_path,
                    "output": (
                        output.splitlines()[0]
                        if output
                        else ""
                    ),
                })

            except Exception as exc:
                results.append({
                    "command": command,
                    "status": "FAIL",
                    "path": command_path,
                    "message": str(exc),
                })

        failed = [
            item
            for item in results
            if item["status"] == "FAIL"
        ]

        return {
            "status": "FAIL" if failed else "PASS",
            "message": (
                "All configured commands are available and executable."
                if not failed
                else "Some configured commands are unavailable or failed."
            ),
            "commands": results,
        }
