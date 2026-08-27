#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path

from collector.environment import EnvironmentCollector
from executor.test_runner import TestRunner
from compatibility.evaluator import CompatibilityEvaluator
from report.generator import ReportGenerator


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    PROJECT_ROOT
    / "configs"
    / "test-case.json"
)

COMPATIBILITY_RULES_FILE = (
    PROJECT_ROOT
    / "configs"
    / "compatibility-rules.json"
)

REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORT_DIR / "result.json"


def load_config():
    with CONFIG_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def load_compatibility_rules():
    with COMPATIBILITY_RULES_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def run_test():
    config = load_config()

    collector = EnvironmentCollector()
    environment = collector.collect()

    test_runner = TestRunner(config)
    test_results = test_runner.run_all()

    passed = sum(
        1
        for result in test_results
        if result["status"] == "PASS"
    )

    failed = sum(
        1
        for result in test_results
        if result["status"] == "FAIL"
    )

    skipped = sum(
        1
        for result in test_results
        if result["status"] == "SKIP"
    )

    status = "FAIL" if failed > 0 else "PASS"

    rules = load_compatibility_rules()

    evaluator = CompatibilityEvaluator(rules)

    compatibility = evaluator.evaluate(
        environment,
        test_results,
    )

    return {
        "project": "linux-os-compatibility-test",
        "status": status,
        "message": "Compatibility tests completed.",
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "summary": {
            "total": len(test_results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "environment": environment,
        "tests": test_results,
        "compatibility": compatibility,
    }


def main():
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    result = run_test()

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False,
        )
        file.write("\n")

    report_generator = ReportGenerator(
        result,
        REPORT_DIR,
    )

    markdown_report = (
        report_generator.generate_markdown()
    )

    html_report = (
        report_generator.generate_html()
    )

    print()
    print(
        f"Report generated: {REPORT_FILE}"
    )
    print(
        f"Markdown report generated: "
        f"{markdown_report}"
    )
    print(
        f"HTML report generated: "
        f"{html_report}"
    )


if __name__ == "__main__":
    main()
