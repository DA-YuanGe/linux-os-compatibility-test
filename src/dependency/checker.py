#!/usr/bin/env python3

import shutil


class DependencyChecker:
    """Check whether required system dependencies are available."""

    def check_command(self, command):
        path = shutil.which(command)

        if path is None:
            return {
                "name": command,
                "status": "FAIL",
                "message": "Command not found.",
            }

        return {
            "name": command,
            "status": "PASS",
            "path": path,
            "message": "Command is available.",
        }

    def check_all(self, commands):
        results = []

        for command in commands:
            results.append(self.check_command(command))

        return results
