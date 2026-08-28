#!/usr/bin/env python3

import platform as python_platform
from pathlib import Path


class PlatformDetector:
    """Detect Linux distribution and CPU architecture."""

    OS_RELEASE_PATHS = [
        Path("/etc/os-release"),
        Path("/usr/lib/os-release"),
    ]

    ARCHITECTURE_MAP = {
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "armv8": "arm64",
        "armv8l": "arm64",
        "ppc64le": "ppc64le",
        "s390x": "s390x",
    }

    def _read_os_release(self):
        os_release_file = None

        for path in self.OS_RELEASE_PATHS:
            if path.exists():
                os_release_file = path
                break

        if os_release_file is None:
            return {}

        data = {}

        for line in os_release_file.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines():
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1,
            )

            value = value.strip()

            if (
                len(value) >= 2
                and value[0] == '"'
                and value[-1] == '"'
            ):
                value = value[1:-1]

            elif (
                len(value) >= 2
                and value[0] == "'"
                and value[-1] == "'"
            ):
                value = value[1:-1]

            data[key] = value

        return data

    def detect_os(self):
        data = self._read_os_release()

        os_id = data.get(
            "ID",
            "linux",
        ).lower()

        id_like = data.get(
            "ID_LIKE",
            "",
        ).lower()

        pretty_name = data.get(
            "PRETTY_NAME",
            "Linux",
        )

        version_id = data.get(
            "VERSION_ID",
            "",
        )

        if os_id == "kylin":
            family = "kylin"

        elif os_id in (
            "uos",
            "uniontech",
        ):
            family = "uos"

        elif os_id == "ubuntu":
            family = "debian"

        elif os_id == "debian":
            family = "debian"

        elif "debian" in id_like:
            family = "debian"

        elif os_id in (
            "rhel",
            "centos",
            "rocky",
            "almalinux",
            "fedora",
        ):
            family = "rhel"

        elif os_id in (
            "openeuler",
            "openEuler".lower(),
        ):
            family = "openeuler"

        elif "rhel" in id_like:
            family = "rhel"

        else:
            family = "generic-linux"

        return {
            "id": os_id,
            "version_id": version_id,
            "id_like": id_like,
            "pretty_name": pretty_name,
            "family": family,
        }

    def detect_architecture(self):
        machine = python_platform.machine().lower()

        normalized = self.ARCHITECTURE_MAP.get(
            machine,
            machine,
        )

        return {
            "raw": machine,
            "normalized": normalized,
            "family": (
                "x86_64"
                if normalized == "x86_64"
                else (
                    "arm64"
                    if normalized == "arm64"
                    else normalized
                )
            ),
        }

    def detect_kernel(self):
        return {
            "name": python_platform.system(),
            "release": python_platform.release(),
            "version": python_platform.version(),
        }

    def detect(self):
        return {
            "os": self.detect_os(),
            "architecture": self.detect_architecture(),
            "kernel": self.detect_kernel(),
        }
