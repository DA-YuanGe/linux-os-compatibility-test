#!/usr/bin/env python3

import os
import tempfile
from pathlib import Path

from testcase.base import TestCase


class FilesystemCompatibilityTest(TestCase):
    """Test basic filesystem operations required by Linux applications."""

    def __init__(self):
        super().__init__(
            name="filesystem_compatibility",
            category="filesystem",
            description="Verify that basic filesystem operations are available and executable.",
            tags=["filesystem", "io", "compatibility", "basic"],
        )

    def execute(self):
        checks = []

        try:
            with tempfile.TemporaryDirectory(
                prefix="compatibility-test-"
            ) as temp_dir:

                temp_path = Path(temp_dir)
                test_file = temp_path / "test.txt"
                test_dir = temp_path / "test-dir"
                renamed_file = temp_path / "renamed.txt"

                # 1. Directory creation
                test_dir.mkdir()

                checks.append({
                    "name": "directory_create",
                    "status": "PASS",
                    "message": "Directory can be created.",
                })

                # 2. File creation and write
                test_file.write_text(
                    "compatibility-test-ok\n",
                    encoding="utf-8",
                )

                checks.append({
                    "name": "file_write",
                    "status": "PASS",
                    "message": "File can be created and written.",
                })

                # 3. File read
                content = test_file.read_text(
                    encoding="utf-8"
                ).strip()

                if content != "compatibility-test-ok":
                    return {
                        "status": "FAIL",
                        "message": "File content verification failed.",
                        "checks": checks,
                        "content": content,
                    }

                checks.append({
                    "name": "file_read",
                    "status": "PASS",
                    "message": "File can be read and content is correct.",
                })

                # 4. File append
                with test_file.open(
                    "a",
                    encoding="utf-8",
                ) as file:
                    file.write("append-test\n")

                checks.append({
                    "name": "file_append",
                    "status": "PASS",
                    "message": "File can be appended.",
                })

                # 5. File rename
                test_file.rename(renamed_file)

                if not renamed_file.exists():
                    return {
                        "status": "FAIL",
                        "message": "File rename verification failed.",
                        "checks": checks,
                    }

                checks.append({
                    "name": "file_rename",
                    "status": "PASS",
                    "message": "File can be renamed.",
                })

                # 6. Directory listing
                entries = list(temp_path.iterdir())

                if not entries:
                    return {
                        "status": "FAIL",
                        "message": "Directory listing returned no entries.",
                        "checks": checks,
                    }

                checks.append({
                    "name": "directory_list",
                    "status": "PASS",
                    "message": "Directory contents can be listed.",
                })

                # 7. File delete
                renamed_file.unlink()

                if renamed_file.exists():
                    return {
                        "status": "FAIL",
                        "message": "File deletion verification failed.",
                        "checks": checks,
                    }

                checks.append({
                    "name": "file_delete",
                    "status": "PASS",
                    "message": "File can be deleted.",
                })

                # 8. Directory delete
                test_dir.rmdir()

                if test_dir.exists():
                    return {
                        "status": "FAIL",
                        "message": "Directory deletion verification failed.",
                        "checks": checks,
                    }

                checks.append({
                    "name": "directory_delete",
                    "status": "PASS",
                    "message": "Directory can be deleted.",
                })

            return {
                "status": "PASS",
                "message": "Basic filesystem operations are supported.",
                "checks": checks,
            }

        except PermissionError as exc:
            return {
                "status": "FAIL",
                "message": "Filesystem permission test failed.",
                "error": str(exc),
                "checks": checks,
            }

        except OSError as exc:
            return {
                "status": "FAIL",
                "message": "Filesystem operation failed.",
                "error": str(exc),
                "checks": checks,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": "Unexpected filesystem test error.",
                "error": str(exc),
                "checks": checks,
            }
