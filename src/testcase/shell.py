#!/usr/bin/env python3

import subprocess

from testcase.base import TestCase


class ShellRuntimeTest(TestCase):
    """Test shell runtime availability and basic command execution."""

    def __init__(self):
        super().__init__()
        self.name = "shell_runtime"
        self.category = "runtime"

    def execute(self):
        version_result = subprocess.run(
            ["bash", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if version_result.returncode != 0:
            return {
                "status": "FAIL",
                "message": "bash --version failed.",
                "stdout": version_result.stdout.strip(),
                "stderr": version_result.stderr.strip(),
            }

        execution_result = subprocess.run(
            [
                "bash",
                "-c",
                "printf 'compatibility-test-ok\\n'",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if execution_result.returncode != 0:
            return {
                "status": "FAIL",
                "message": "Shell execution test failed.",
                "stdout": execution_result.stdout.strip(),
                "stderr": execution_result.stderr.strip(),
            }

        return {
            "status": "PASS",
            "message": "Bash runtime is available and executable.",
            "version": version_result.stdout.splitlines()[0].strip(),
            "output": execution_result.stdout.strip(),
        }


if __name__ == "__main__":
    result = ShellRuntimeTest().run()
    print(result)
