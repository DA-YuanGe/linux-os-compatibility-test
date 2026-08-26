

#!/usr/bin/env python3

import subprocess
from testcase.base import TestCase


class PythonRuntimeTest(TestCase):
    """Test Python runtime availability and execution."""

    def __init__(self):
        super().__init__(
            name="python_runtime",
            category="runtime",
            description="Verify that the Python runtime is available and executable.",
            tags=["runtime", "python", "basic"],
        )

    def execute(self):
        version_result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if version_result.returncode != 0:
            return {
                "status": "FAIL",
                "message": "python3 --version failed.",
                "stdout": version_result.stdout.strip(),
                "stderr": version_result.stderr.strip(),
            }

        execution_result = subprocess.run(
            [
                "python3",
                "-c",
                "print('compatibility-test-ok')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if execution_result.returncode != 0:
            return {
                "status": "FAIL",
                "message": "Python execution test failed.",
                "stdout": execution_result.stdout.strip(),
                "stderr": execution_result.stderr.strip(),
            }

        return {
            "status": "PASS",
            "message": "Python runtime is available and executable.",
            "version": (
                version_result.stdout.strip()
                or version_result.stderr.strip()
            ),
            "output": execution_result.stdout.strip(),
        }
