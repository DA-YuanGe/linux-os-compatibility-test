#!/usr/bin/env python3

from testcase.runtime import PythonRuntimeTest
from testcase.command import CommandAvailabilityTest
from testcase.shell import ShellRuntimeTest
from testcase.dependency import DependencyTest
from testcase.os_compatibility import OSCompatibilityTest
from testcase.application import ApplicationRuntimeTest


class TestRunner:
    """Execute registered compatibility test cases."""

    def __init__(self):
        self.test_cases = [
            PythonRuntimeTest(),
            CommandAvailabilityTest(),
            ShellRuntimeTest(),
            DependencyTest(),
            OSCompatibilityTest(),
            ApplicationRuntimeTest(),
        ]

    def run_all(self):
        results = []

        for test_case in self.test_cases:
            result = test_case.run()
            results.append(result)

        return results
