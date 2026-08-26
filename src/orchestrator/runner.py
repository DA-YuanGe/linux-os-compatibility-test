#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path

from collector.environment import EnvironmentCollector
from executor.test_runner import TestRunner


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORT_DIR / "result.json"


def run_test():
    collector = EnvironmentCollector()
    environment = collector.collect()

    test_runner = TestRunner()
    test_results = test_runner.run_all()

    passed = sum(
        1 for result in test_results
        if result["status"] == "PASS"
    )

    failed = sum(
        1 for result in test_results
        if result["status"] == "FAIL"
    )

    skipped = sum(
        1 for result in test_results
        if result["status"] == "SKIP"
    )

    if failed > 0:
        status = "FAIL"
    else:
        status = "PASS"

    return {
        "project": "linux-os-compatibility-test",
        "status": status,
        "message": "Compatibility tests completed.",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "total": len(test_results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "environment": environment,
        "tests": test_results,
    }


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    result = run_test()

    print(json.dumps(result, indent=2, ensure_ascii=False))

    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
        file.write("\n")

    print()
    print(f"Report generated: {REPORT_FILE}")


if __name__ == "__main__":
    main()
