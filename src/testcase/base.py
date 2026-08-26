#!/usr/bin/env python3

from abc import ABC, abstractmethod
from datetime import datetime


class TestCase(ABC):
    """Base class for compatibility test cases."""

    def __init__(
        self,
        name=None,
        category="general",
        description="",
        tags=None,
    ):
        self.name = name or self.__class__.__name__
        self.category = category
        self.description = description
        self.tags = tags or []

    @abstractmethod
    def execute(self):
        """Execute the test case and return a result."""
        raise NotImplementedError

    def run(self):
        start_time = datetime.now()

        try:
            result = self.execute()

            if not isinstance(result, dict):
                result = {
                    "status": "FAIL",
                    "message": "Test case returned an invalid result.",
                }

        except Exception as exc:
            result = {
                "status": "FAIL",
                "message": str(exc),
            }

        end_time = datetime.now()

        result["name"] = self.name
        result["category"] = self.category
        result["description"] = self.description
        result["tags"] = self.tags
        result["started_at"] = start_time.isoformat(timespec="seconds")
        result["finished_at"] = end_time.isoformat(timespec="seconds")

        return result
