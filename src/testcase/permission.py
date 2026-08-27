#!/usr/bin/env python3

import os
import stat
import subprocess
import tempfile
from pathlib import Path

from testcase.base import TestCase


class PermissionCompatibilityTest(TestCase):
    """Test basic Linux file permission operations."""

    def __init__(self):
        super().__init__(
            name="permission_compatibility",
            category="permission",
            description="Verify that basic Linux file permission and executable operations are supported.",
            tags=["permission", "chmod", "execute", "compatibility"],
        )

    def execute(self):
        checks = []

        try:
            with tempfile.TemporaryDirectory(
                prefix="compatibility-permission-"
            ) as temp_dir:

                temp_path = Path(temp_dir)
                test_file = temp_path / "permission-test.sh"

                # 1. Create executable shell script
                test_file.write_text(
                    "#!/bin/sh\n"
                    "printf 'permission-test-ok\\n'\n",
                    encoding="utf-8",
                )

                checks.append({
                    "name": "file_create",
                    "status": "PASS",
                    "message": "Permission test file can be created.",
                })

                # 2. Remove executable permission
                os.chmod(
                    test_file,
                    stat.S_IRUSR | stat.S_IWUSR,
                )

                mode = stat.S_IMODE(
                    test_file.stat().st_mode
                )

                if mode != 0o600:
                    return {
                        "status": "FAIL",
                        "message": "File permission could not be set to 600.",
                        "checks": checks,
                        "mode": oct(mode),
                    }

                checks.append({
                    "name": "permission_set",
                    "status": "PASS",
                    "message": "File permissions can be changed.",
                    "mode": oct(mode),
                })

                # 3. Add executable permission
                os.chmod(
                    test_file,
                    stat.S_IRUSR
                    | stat.S_IWUSR
                    | stat.S_IXUSR,
                )

                mode = stat.S_IMODE(
                    test_file.stat().st_mode
                )

                if not mode & stat.S_IXUSR:
                    return {
                        "status": "FAIL",
                        "message": "Executable permission could not be enabled.",
                        "checks": checks,
                        "mode": oct(mode),
                    }

                checks.append({
                    "name": "executable_permission",
                    "status": "PASS",
                    "message": "Executable permission can be enabled.",
                    "mode": oct(mode),
                })

                # 4. Execute script directly
                result = subprocess.run(
                    [str(test_file)],
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
                        "message": "Executable file could not be executed.",
                        "checks": checks,
                        "return_code": result.returncode,
                        "output": output,
                    }

                if output != "permission-test-ok":
                    return {
                        "status": "FAIL",
                        "message": "Executable file returned unexpected output.",
                        "checks": checks,
                        "output": output,
                    }

                checks.append({
                    "name": "direct_execution",
                    "status": "PASS",
                    "message": "Executable file can be executed successfully.",
                    "output": output,
                })

                # 5. Remove executable permission again
                os.chmod(
                    test_file,
                    stat.S_IRUSR | stat.S_IWUSR,
                )

                mode = stat.S_IMODE(
                    test_file.stat().st_mode
                )

                if mode & stat.S_IXUSR:
                    return {
                        "status": "FAIL",
                        "message": "Executable permission could not be removed.",
                        "checks": checks,
                        "mode": oct(mode),
                    }

                checks.append({
                    "name": "permission_remove",
                    "status": "PASS",
                    "message": "Executable permission can be removed.",
                    "mode": oct(mode),
                })

            return {
                "status": "PASS",
                "message": "Basic Linux file permission operations are supported.",
                "checks": checks,
            }

        except PermissionError as exc:
            return {
                "status": "FAIL",
                "message": "Permission operation failed.",
                "error": str(exc),
                "checks": checks,
            }

        except OSError as exc:
            return {
                "status": "FAIL",
                "message": "Operating system permission operation failed.",
                "error": str(exc),
                "checks": checks,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": "Unexpected permission test error.",
                "error": str(exc),
                "checks": checks,
            }
