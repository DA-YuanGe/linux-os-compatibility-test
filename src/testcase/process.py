#!/usr/bin/env python3

import signal
import subprocess
import sys

from testcase.base import TestCase


class ProcessCompatibilityTest(TestCase):
    """Test Linux process creation, exit codes and signal handling."""

    def __init__(self):
        super().__init__(
            name="process_compatibility",
            category="process",
            description=(
                "Verify Linux process creation, execution, "
                "exit codes and signal handling."
            ),
            tags=[
                "process",
                "subprocess",
                "signal",
                "compatibility",
            ],
        )

    def execute(self):
        checks = []

        try:
            # 1. Process creation and execution
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "print('process-test-ok')",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            output = (
                result.stdout.strip()
                or result.stderr.strip()
            )

            if result.returncode != 0:
                return {
                    "status": "FAIL",
                    "message": "Child process execution failed.",
                    "return_code": result.returncode,
                    "output": output,
                    "checks": checks,
                }

            if output != "process-test-ok":
                return {
                    "status": "FAIL",
                    "message": (
                        "Child process returned "
                        "unexpected output."
                    ),
                    "output": output,
                    "checks": checks,
                }

            checks.append({
                "name": "process_create",
                "status": "PASS",
                "message": (
                    "Child process can be created "
                    "and executed."
                ),
                "output": output,
            })

            # 2. Process exit code
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.exit(7)",
                ],
                timeout=10,
            )

            if result.returncode != 7:
                return {
                    "status": "FAIL",
                    "message": (
                        "Child process return code "
                        "was not preserved."
                    ),
                    "return_code": result.returncode,
                    "expected_return_code": 7,
                    "checks": checks,
                }

            checks.append({
                "name": "process_return_code",
                "status": "PASS",
                "message": (
                    "Child process return code "
                    "can be obtained correctly."
                ),
                "return_code": result.returncode,
            })

            # 3. Process signal handling
            proc = subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    (
                        "import signal, time; "
                        "signal.signal("
                        "signal.SIGTERM, "
                        "signal.SIG_DFL"
                        "); "
                        "time.sleep(30)"
                    ),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            try:
                proc.send_signal(signal.SIGTERM)

                stdout, stderr = proc.communicate(
                    timeout=10
                )

            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()

                return {
                    "status": "FAIL",
                    "message": (
                        "Child process did not "
                        "terminate after SIGTERM."
                    ),
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "checks": checks,
                }

            expected_return_code = -signal.SIGTERM

            if proc.returncode != expected_return_code:
                return {
                    "status": "FAIL",
                    "message": (
                        "Child process did not "
                        "terminate correctly after SIGTERM."
                    ),
                    "return_code": proc.returncode,
                    "expected_return_code": (
                        expected_return_code
                    ),
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "checks": checks,
                }

            checks.append({
                "name": "signal_termination",
                "status": "PASS",
                "message": (
                    "Child process can be terminated "
                    "using SIGTERM."
                ),
                "signal": "SIGTERM",
                "return_code": proc.returncode,
            })

            return {
                "status": "PASS",
                "message": (
                    "Linux process creation, execution "
                    "and signal handling are supported."
                ),
                "checks": checks,
            }

        except subprocess.TimeoutExpired as exc:
            return {
                "status": "FAIL",
                "message": "Process operation timed out.",
                "error": str(exc),
                "checks": checks,
            }

        except OSError as exc:
            return {
                "status": "FAIL",
                "message": (
                    "Operating system process "
                    "operation failed."
                ),
                "error": str(exc),
                "checks": checks,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": "Unexpected process test error.",
                "error": str(exc),
                "checks": checks,
            }
