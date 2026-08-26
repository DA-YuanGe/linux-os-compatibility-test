#!/usr/bin/env python3

from dependency.checker import DependencyChecker
from testcase.base import TestCase


class DependencyTest(TestCase):
    """Test required application dependencies."""

    def __init__(self):
        super().__init__()
        self.name = "dependency_check"
        self.category = "dependency"

    def execute(self):
        checker = DependencyChecker()

        required_commands = [
            "python3",
            "bash",
        ]

        results = checker.check_all(required_commands)

        failed = [
            item for item in results
            if item["status"] == "FAIL"
        ]

        return {
            "status": "FAIL" if failed else "PASS",
            "message": (
                "All required dependencies are available."
                if not failed
                else "Some required dependencies are unavailable."
            ),
            "dependencies": results,
        }
