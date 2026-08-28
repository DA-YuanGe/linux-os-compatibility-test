#!/usr/bin/env python3

import json
import sqlite3
from pathlib import Path


class TestHistoryStore:
    """Store compatibility test execution history in SQLite."""

    def __init__(self, database_path):
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    project TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_tests INTEGER NOT NULL DEFAULT 0,
                    passed_tests INTEGER NOT NULL DEFAULT 0,
                    failed_tests INTEGER NOT NULL DEFAULT 0,
                    skipped_tests INTEGER NOT NULL DEFAULT 0,
                    compatibility_status TEXT,
                    supported INTEGER NOT NULL DEFAULT 0,
                    result_json TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_test_runs_timestamp
                ON test_runs(timestamp)
                """
            )

    def save(self, result):
        summary = result.get(
            "summary",
            {},
        )

        compatibility = result.get(
            "compatibility",
            {},
        )

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO test_runs (
                    timestamp,
                    project,
                    status,
                    total_tests,
                    passed_tests,
                    failed_tests,
                    skipped_tests,
                    compatibility_status,
                    supported,
                    result_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.get(
                        "timestamp",
                        "",
                    ),
                    result.get(
                        "project",
                        "linux-os-compatibility-test",
                    ),
                    result.get(
                        "status",
                        "UNKNOWN",
                    ),
                    summary.get(
                        "total",
                        0,
                    ),
                    summary.get(
                        "passed",
                        0,
                    ),
                    summary.get(
                        "failed",
                        0,
                    ),
                    summary.get(
                        "skipped",
                        0,
                    ),
                    compatibility.get(
                        "status",
                        "UNKNOWN",
                    ),
                    (
                        1
                        if compatibility.get(
                            "supported",
                            False,
                        )
                        else 0
                    ),
                    json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                ),
            )

            return cursor.lastrowid

    def list_runs(self, limit=20):
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    timestamp,
                    project,
                    status,
                    total_tests,
                    passed_tests,
                    failed_tests,
                    skipped_tests,
                    compatibility_status,
                    supported
                FROM test_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_run(self, run_id):
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM test_runs
                WHERE id = ?
                """,
                (run_id,),
            ).fetchone()

        if row is None:
            return None

        result = dict(row)

        result["supported"] = bool(
            result["supported"]
        )

        result["result"] = json.loads(
            result.pop("result_json")
        )

        return result

    def count(self):
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM test_runs
                """
            ).fetchone()

        return row["count"]
