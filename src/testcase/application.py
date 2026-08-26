#!/usr/bin/env python3

import json
import subprocess
from datetime import datetime
from pathlib import Path

from testcase.base import TestCase


class ApplicationRuntimeTest(TestCase):
    """Test whether the configured application can start and execute."""

    def __init__(self):
        super().__init__()
        self.name = "application_runtime"
        self.category = "application"

    def execute(self):
        project_root = Path(__file__).resolve().parents[2]
        config_file = project_root / "configs" / "test-case.json"

        if not config_file.exists():
            return {
                "status": "FAIL",
                "message": "Test configuration file was not found.",
                "config": str(config_file),
            }

        try:
            with config_file.open("r", encoding="utf-8") as file:
                config = json.load(file)
        except Exception as exc:
            return {
                "status": "FAIL",
                "message": "Failed to load test configuration.",
                "error": str(exc),
            }

        application = config.get("application", {})
        application_name = application.get("name", "")
        command = application.get("command", [])

        if not application_name:
            return {
                "status": "FAIL",
                "message": "Application name is not configured.",
            }

        if not isinstance(command, list) or not command:
            return {
                "status": "FAIL",
                "message": "Application command is not configured correctly.",
                "application": application_name,
            }

        try:
            started_at = datetime.now()

            result = subprocess.run(
                command,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            finished_at = datetime.now()

            output = result.stdout.strip()
            error = result.stderr.strip()

            return_code = result.returncode

            if return_code != 0:
                return {
                    "status": "FAIL",
                    "message": "Configured application execution failed.",
                    "application": application_name,
                    "command": command,
                    "return_code": return_code,
                    "stdout": output,
                    "stderr": error,
                    "duration_ms": int(
                        (finished_at - started_at).total_seconds() * 1000
                    ),
                }

            return {
                "status": "PASS",
                "message": "Configured application started and executed successfully.",
                "application": application_name,
                "command": command,
                "return_code": return_code,
                "output": output,
                "duration_ms": int(
                    (finished_at - started_at).total_seconds() * 1000
                ),
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "FAIL",
                "message": "Configured application execution timed out.",
                "application": application_name,
                "command": command,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": "Failed to execute configured application.",
                "application": application_name,
                "command": command,
                "error": str(exc),
            }
