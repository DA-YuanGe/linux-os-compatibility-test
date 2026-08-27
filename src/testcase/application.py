#!/usr/bin/env python3

import subprocess
import time
from datetime import datetime
from pathlib import Path

from testcase.base import TestCase


class ApplicationRuntimeTest(TestCase):
    """Test whether a configured application can start and execute."""

    def __init__(self, application):
        super().__init__(
            name="application_runtime",
            category="application",
            description=(
                "Verify that the configured application "
                "can start and execute."
            ),
            tags=[
                "application",
                "runtime",
                "config-driven",
            ],
        )

        self.application = application or {}

    def execute(self):
        project_root = Path(__file__).resolve().parents[2]

        application_name = self.application.get(
            "name",
            "",
        )

        command = self.application.get(
            "command",
            [],
        )

        if not application_name:
            return {
                "status": "FAIL",
                "message": "Application name is not configured.",
            }

        if not isinstance(command, list) or not command:
            return {
                "status": "FAIL",
                "message": (
                    "Application command is not "
                    "configured correctly."
                ),
                "application": application_name,
            }

        process = None

        try:
            started_at = datetime.now()

            process = subprocess.Popen(
                command,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            startup_timeout = 10
            deadline = time.time() + startup_timeout

            while time.time() < deadline:
                return_code = process.poll()

                if return_code is not None:
                    stdout, stderr = process.communicate()

                    finished_at = datetime.now()

                    duration_ms = int(
                        (
                            finished_at - started_at
                        ).total_seconds() * 1000
                    )

                    output = stdout.strip()
                    error = stderr.strip()

                    if return_code != 0:
                        return {
                            "status": "FAIL",
                            "message": (
                                "Configured application "
                                "execution failed."
                            ),
                            "application": application_name,
                            "command": command,
                            "return_code": return_code,
                            "stdout": output,
                            "stderr": error,
                            "duration_ms": duration_ms,
                        }

                    return {
                        "status": "PASS",
                        "message": (
                            "Configured application "
                            "started and exited successfully."
                        ),
                        "application": application_name,
                        "command": command,
                        "return_code": return_code,
                        "output": output,
                        "duration_ms": duration_ms,
                        "execution_mode": "short_lived",
                    }

                time.sleep(0.2)

            if process.poll() is None:
                pid = process.pid

                process.terminate()

                try:
                    stdout, stderr = process.communicate(
                        timeout=5
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()

                finished_at = datetime.now()

                duration_ms = int(
                    (
                        finished_at - started_at
                    ).total_seconds() * 1000
                )

                return {
                    "status": "PASS",
                    "message": (
                        "Configured application "
                        "started successfully and "
                        "remained running."
                    ),
                    "application": application_name,
                    "command": command,
                    "pid": pid,
                    "return_code": None,
                    "stdout": (stdout or "").strip(),
                    "stderr": (stderr or "").strip(),
                    "duration_ms": duration_ms,
                    "execution_mode": "long_running",
                }

        except Exception as exc:
            if process is not None:
                try:
                    if process.poll() is None:
                        process.terminate()

                        try:
                            process.communicate(
                                timeout=5
                            )
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.communicate()
                except Exception:
                    pass

            return {
                "status": "FAIL",
                "message": (
                    "Failed to execute configured "
                    "application."
                ),
                "application": application_name,
                "command": command,
                "error": str(exc),
            }
