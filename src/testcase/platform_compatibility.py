#!/usr/bin/env python3

import json
from pathlib import Path

from compatibility.platform import PlatformDetector


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_FILE = PROJECT_ROOT / "configs" / "compatibility-rules.json"


class PlatformCompatibilityTest:
    """Test Linux distribution and CPU architecture compatibility."""

    def __init__(self):
        self.name = "platform_compatibility"
        self.category = "compatibility"
        self.description = (
            "Detect the current Linux platform and validate "
            "OS and CPU architecture against compatibility rules."
        )

    def _load_rules(self):
        if not RULES_FILE.exists():
            raise FileNotFoundError(
                f"Compatibility rules file not found: {RULES_FILE}"
            )

        with RULES_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _normalize_os_id(self, os_id):
        return (os_id or "").strip().lower()

    def _normalize_architecture(self, architecture):
        return (architecture or "").strip().lower()

    def _find_platform_rule(self, os_id, os_family, rules):
        platforms = rules.get(
            "platforms",
            {},
        )

        normalized_os = self._normalize_os_id(
            os_id
        )

        normalized_family = self._normalize_os_id(
            os_family
        )

        for platform_id, platform_rule in platforms.items():
            ids = platform_rule.get(
                "ids",
                [],
            )

            normalized_ids = [
                self._normalize_os_id(item)
                for item in ids
            ]

            if normalized_os in normalized_ids:
                return platform_id, platform_rule

        for platform_id, platform_rule in platforms.items():
            if platform_id == normalized_family:
                return platform_id, platform_rule

        if "generic-linux" in platforms:
            return (
                "generic-linux",
                platforms["generic-linux"],
            )

        return None, None

    def _find_architecture_rule(
        self,
        architecture,
        rules,
    ):
        architectures = rules.get(
            "architectures",
            {},
        )

        normalized_arch = self._normalize_architecture(
            architecture
        )

        for architecture_id, architecture_rule in architectures.items():
            aliases = architecture_rule.get(
                "aliases",
                [],
            )

            normalized_aliases = [
                self._normalize_architecture(item)
                for item in aliases
            ]

            if normalized_arch == architecture_id:
                return (
                    architecture_id,
                    architecture_rule,
                )

            if normalized_arch in normalized_aliases:
                return (
                    architecture_id,
                    architecture_rule,
                )

        return None, None

    def run(self):
        try:
            rules = self._load_rules()

            detector = PlatformDetector()
            platform_info = detector.detect()

            os_info = platform_info.get(
                "os",
                {},
            )

            architecture_info = platform_info.get(
                "architecture",
                {},
            )

            kernel_info = platform_info.get(
                "kernel",
                {},
            )

            os_id = self._normalize_os_id(
                os_info.get(
                    "id",
                    "",
                )
            )

            os_version = os_info.get(
                "version_id",
                "",
            )

            os_family = self._normalize_os_id(
                os_info.get(
                    "family",
                    "generic-linux",
                )
            )

            architecture = self._normalize_architecture(
                architecture_info.get(
                    "normalized",
                    "",
                )
            )

            kernel = kernel_info.get(
                "release",
                "unknown",
            )

            if not os_id:
                return {
                    "status": "FAIL",
                    "message": (
                        "Unable to identify the Linux distribution."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "platform": platform_info,
                }

            if not architecture:
                return {
                    "status": "FAIL",
                    "message": (
                        "Unable to identify CPU architecture."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "platform": platform_info,
                }

            platform_id, platform_rule = (
                self._find_platform_rule(
                    os_id,
                    os_family,
                    rules,
                )
            )

            architecture_id, architecture_rule = (
                self._find_architecture_rule(
                    architecture,
                    rules,
                )
            )

            if platform_rule is None:
                return {
                    "status": "FAIL",
                    "message": (
                        f"Operating system '{os_id}' "
                        "is not supported by compatibility rules."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "platform": platform_info,
                    "os": os_id,
                    "os_version": os_version,
                    "os_family": os_family,
                    "architecture": architecture,
                    "kernel": kernel,
                }

            if not platform_rule.get(
                "supported",
                False,
            ):
                return {
                    "status": "FAIL",
                    "message": (
                        f"Platform '{platform_id}' "
                        "is marked as unsupported."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "platform": platform_info,
                    "os": os_id,
                    "os_version": os_version,
                    "os_family": os_family,
                    "platform_id": platform_id,
                    "architecture": architecture,
                    "kernel": kernel,
                }

            if architecture_rule is None:
                return {
                    "status": "FAIL",
                    "message": (
                        f"Architecture '{architecture}' "
                        "is not supported by compatibility rules."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "platform": platform_info,
                    "os": os_id,
                    "os_version": os_version,
                    "os_family": os_family,
                    "platform_id": platform_id,
                    "architecture": architecture,
                    "kernel": kernel,
                }

            if not architecture_rule.get(
                "supported",
                False,
            ):
                return {
                    "status": "FAIL",
                    "message": (
                        f"Architecture '{architecture_id}' "
                        "is marked as unsupported."
                    ),
                    "name": self.name,
                    "category": self.category,
                    "description": self.description,
                    "platform": platform_info,
                    "os": os_id,
                    "os_version": os_version,
                    "os_family": os_family,
                    "platform_id": platform_id,
                    "architecture": architecture,
                    "architecture_id": architecture_id,
                    "kernel": kernel,
                }

            platform_name = platform_rule.get(
                "name",
                platform_id,
            )

            architecture_name = architecture_rule.get(
                "name",
                architecture_id,
            )

            return {
                "status": "PASS",
                "message": (
                    f"Platform compatible: "
                    f"{platform_name} "
                    f"{os_version} "
                    f"on {architecture_name}."
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
                "platform": platform_info,
                "os": os_id,
                "os_version": os_version,
                "os_family": os_family,
                "platform_id": platform_id,
                "architecture": architecture,
                "architecture_id": architecture_id,
                "kernel": kernel,
            }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": (
                    f"Platform compatibility test failed: {exc}"
                ),
                "name": self.name,
                "category": self.category,
                "description": self.description,
            }
