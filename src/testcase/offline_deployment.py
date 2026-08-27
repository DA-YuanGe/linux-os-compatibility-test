#!/usr/bin/env python3

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class OfflineDeploymentTest:
    """Test offline application deployment."""

    def __init__(self):
        self.name = "offline_deployment"
        self.category = "deployment"
        self.description = (
            "Verify that the application can be deployed "
            "and verified from local offline packages."
        )

    def run(self):
        install_script = (
            PROJECT_ROOT / "offline" / "install.sh"
        )

        if not install_script.exists():
            return {
                "status": "FAIL",
                "message": (
                    "Offline deployment script not found."
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
            }

        if not install_script.is_file():
            return {
                "status": "FAIL",
                "message": (
                    "Offline deployment script is not a file."
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
            }

        try:
            process = subprocess.run(
                [
                    "sh",
                    str(install_script),
                    "--offline",
                ],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
            )

            output = process.stdout or ""
            error_output = process.stderr or ""

            if process.returncode == 0:
                return {
                    "status": "PASS",
                    "message": (
                        "Offline application deployment "
                        "completed successfully."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "return_code": process.returncode,
                    "output": output,
                }

            message = (
                "Offline application deployment failed."
            )

            if error_output.strip():
                message = (
                    f"{message} {error_output.strip()}"
                )

            return {
                "status": "FAIL",
                "message": message,
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "return_code": process.returncode,
                "output": output,
                "error": error_output,
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "FAIL",
                "message": (
                    "Offline deployment test timed out."
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": (
                    f"Offline deployment test failed: {exc}"
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
            }
