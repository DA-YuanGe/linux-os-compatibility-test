#!/usr/bin/env python3

import re
import shutil
import subprocess


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

    def check_java(self, min_major_version=17):
        path = shutil.which("java")

        if path is None:
            return {
                "name": "java",
                "status": "FAIL",
                "message": "Java runtime not found.",
                "required_major_version": min_major_version,
            }

        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            output = result.stderr + result.stdout

            if result.returncode != 0:
                return {
                    "name": "java",
                    "status": "FAIL",
                    "path": path,
                    "message": "Java runtime could not be executed.",
                    "error": output.strip(),
                    "required_major_version": min_major_version,
                }

            match = re.search(
                r'version "(\d+)(?:\.(\d+))?',
                output,
            )

            if not match:
                return {
                    "name": "java",
                    "status": "FAIL",
                    "path": path,
                    "message": "Unable to determine Java version.",
                    "required_major_version": min_major_version,
                }

            major_version = int(match.group(1))
            version = match.group(0).split('"')[1]

            if major_version < min_major_version:
                return {
                    "name": "java",
                    "status": "FAIL",
                    "path": path,
                    "version": version,
                    "major_version": major_version,
                    "required_major_version": min_major_version,
                    "message": "Java version is below the minimum requirement.",
                }

            return {
                "name": "java",
                "status": "PASS",
                "path": path,
                "version": version,
                "major_version": major_version,
                "required_major_version": min_major_version,
                "message": "Java version requirement satisfied.",
            }

        except subprocess.TimeoutExpired:
            return {
                "name": "java",
                "status": "FAIL",
                "path": path,
                "message": "Java version check timed out.",
                "required_major_version": min_major_version,
            }

        except Exception as exc:
            return {
                "name": "java",
                "status": "FAIL",
                "path": path,
                "message": "Unexpected Java version check error.",
                "error": str(exc),
                "required_major_version": min_major_version,
            }

    def check_all(self, commands):
        results = []

        for command in commands:
            results.append(self.check_command(command))

        return results
