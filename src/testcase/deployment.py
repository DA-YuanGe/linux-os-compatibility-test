#!/usr/bin/env python3

import socket
import subprocess
import time
from pathlib import Path
import sys
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analyzer.log_analyzer import LogAnalyzer


class DeploymentTest:
    """Test application deployment, health and runtime logs."""

    def __init__(self, application):
        self.application = application or {}

    def _check_port(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            result = sock.connect_ex((host, port))
            return result == 0
        finally:
            sock.close()

    def _check_http(self, url):
        try:
            with urlopen(url, timeout=3) as response:
                body = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

                return {
                    "status": (
                        "PASS"
                        if response.status == 200
                        else "FAIL"
                    ),
                    "http_status": response.status,
                    "body": body,
                }

        except Exception as exc:
            return {
                "status": "FAIL",
                "message": str(exc),
            }

    def _write_logs(self, name, stdout, stderr):
        log_dir = PROJECT_ROOT / "logs" / "application"

        log_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        stdout_file = (
            log_dir / f"{name}-stdout.log"
        )

        stderr_file = (
            log_dir / f"{name}-stderr.log"
        )

        stdout_file.write_text(
            stdout or "",
            encoding="utf-8",
        )

        stderr_file.write_text(
            stderr or "",
            encoding="utf-8",
        )

        return stdout_file, stderr_file

    def _analyze_logs(self, stdout_file, stderr_file):
        analyzer = LogAnalyzer(
            [
                stdout_file,
                stderr_file,
            ]
        )

        findings = analyzer.analyze()

        summary = analyzer.summarize(
            findings
        )

        return {
            "summary": summary,
            "findings": findings,
        }

    def _stop_and_collect(self, process):
        if process is None:
            return "", ""

        if process.poll() is None:
            process.terminate()

            try:
                stdout, stderr = process.communicate(
                    timeout=5
                )
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
        else:
            stdout, stderr = process.communicate()

        return stdout or "", stderr or ""

    def _build_result(
        self,
        status,
        message,
        name,
        host,
        port,
        checks,
        process,
        stdout_file,
        stderr_file,
        log_analysis,
    ):
        return {
            "status": status,
            "message": message,
            "name": "deployment_test",
            "category": "deployment",
            "description": (
                "Verify application deployment, "
                "health and runtime compatibility."
            ),
            "application": name,
            "pid": (
                process.pid
                if process is not None
                else None
            ),
            "host": host,
            "port": port,
            "checks": checks,
            "stdout_log": (
                str(stdout_file)
                if stdout_file
                else None
            ),
            "stderr_log": (
                str(stderr_file)
                if stderr_file
                else None
            ),
            "log_analysis": log_analysis,
        }
    def run(self):
        name = self.application.get(
            "name",
            "",
        )

        command = self.application.get(
            "command",
            [],
        )

        host = self.application.get(
            "host",
            "127.0.0.1",
        )

        port = int(
            self.application.get(
                "port",
                8080,
            )
        )

        health_path = self.application.get(
            "health_path",
            "/health",
        )

        api_path = self.application.get(
            "api_path",
            "/api/test",
        )

        if not name:
            return {
                "status": "FAIL",
                "message": (
                    "Application name is not configured."
                ),
            }

        if not isinstance(command, list) or not command:
            return {
                "status": "FAIL",
                "message": (
                    "Application command is not configured."
                ),
                "application": name,
            }

        process = None
        checks = []

        stdout_file = None
        stderr_file = None

        log_analysis = {
            "summary": {
                "status": "PASS",
                "total": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "findings": [],
        }

        try:
            # 1. Start application
            process = subprocess.Popen(
                command,
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            checks.append({
                "name": "application_start",
                "status": "PASS",
                "message": (
                    "Application process started."
                ),
                "pid": process.pid,
            })

            # 2. Wait for application port
            port_ready = False

            for _ in range(20):
                if process.poll() is not None:
                    break

                if self._check_port(
                    host,
                    port,
                ):
                    port_ready = True
                    break

                time.sleep(0.5)

            if not port_ready:
                stdout, stderr = (
                    self._stop_and_collect(process)
                )

                stdout_file, stderr_file = (
                    self._write_logs(
                        name,
                        stdout,
                        stderr,
                    )
                )

                log_analysis = self._analyze_logs(
                    stdout_file,
                    stderr_file,
                )

                checks.append({
                    "name": "application_stop",
                    "status": "PASS",
                    "message": (
                        "Application process stopped."
                    ),
                    "pid": process.pid,
                })

                return self._build_result(
                    "FAIL",
                    (
                        "Application port did not "
                        "become available."
                    ),
                    name,
                    host,
                    port,
                    checks,
                    process,
                    stdout_file,
                    stderr_file,
                    log_analysis,
                )

            checks.append({
                "name": "port_check",
                "status": "PASS",
                "message": (
                    "Application port is listening."
                ),
                "host": host,
                "port": port,
            })

            # 3. Process check
            if process.poll() is None:
                checks.append({
                    "name": "process_check",
                    "status": "PASS",
                    "message": (
                        "Application process is running."
                    ),
                    "pid": process.pid,
                })
            else:
                stdout, stderr = process.communicate()

                stdout_file, stderr_file = (
                    self._write_logs(
                        name,
                        stdout,
                        stderr,
                    )
                )

                log_analysis = self._analyze_logs(
                    stdout_file,
                    stderr_file,
                )

                return self._build_result(
                    "FAIL",
                    (
                        "Application process exited "
                        "unexpectedly."
                    ),
                    name,
                    host,
                    port,
                    checks,
                    process,
                    stdout_file,
                    stderr_file,
                    log_analysis,
                )

            # 4. Health check
            health_url = (
                f"http://{host}:{port}"
                f"{health_path}"
            )

            health_result = self._check_http(
                health_url
            )

            checks.append({
                "name": "health_check",
                "status": health_result["status"],
                "message": (
                    "Application health endpoint "
                    "checked."
                ),
                "url": health_url,
                "http_status": health_result.get(
                    "http_status"
                ),
                "body": health_result.get(
                    "body"
                ),
            })

            if health_result["status"] != "PASS":
                stdout, stderr = (
                    self._stop_and_collect(process)
                )

                stdout_file, stderr_file = (
                    self._write_logs(
                        name,
                        stdout,
                        stderr,
                    )
                )

                log_analysis = self._analyze_logs(
                    stdout_file,
                    stderr_file,
                )

                checks.append({
                    "name": "application_stop",
                    "status": "PASS",
                    "message": (
                        "Application process stopped."
                    ),
                    "pid": process.pid,
                })

                return self._build_result(
                    "FAIL",
                    (
                        "Application health check failed."
                    ),
                    name,
                    host,
                    port,
                    checks,
                    process,
                    stdout_file,
                    stderr_file,
                    log_analysis,
                )

            # 5. API check
            api_url = (
                f"http://{host}:{port}"
                f"{api_path}"
            )

            api_result = self._check_http(
                api_url
            )

            checks.append({
                "name": "api_check",
                "status": api_result["status"],
                "message": (
                    "Application API endpoint checked."
                ),
                "url": api_url,
                "http_status": api_result.get(
                    "http_status"
                ),
                "body": api_result.get(
                    "body"
                ),
            })

            if api_result["status"] != "PASS":
                stdout, stderr = (
                    self._stop_and_collect(process)
                )

                stdout_file, stderr_file = (
                    self._write_logs(
                        name,
                        stdout,
                        stderr,
                    )
                )

                log_analysis = self._analyze_logs(
                    stdout_file,
                    stderr_file,
                )

                checks.append({
                    "name": "application_stop",
                    "status": "PASS",
                    "message": (
                        "Application process stopped."
                    ),
                    "pid": process.pid,
                })

                return self._build_result(
                    "FAIL",
                    (
                        "Application API check failed."
                    ),
                    name,
                    host,
                    port,
                    checks,
                    process,
                    stdout_file,
                    stderr_file,
                    log_analysis,
                )

            # 6. Stop application and collect logs
            stdout, stderr = (
                self._stop_and_collect(process)
            )

            stdout_file, stderr_file = (
                self._write_logs(
                    name,
                    stdout,
                    stderr,
                )
            )

            log_analysis = self._analyze_logs(
                stdout_file,
                stderr_file,
            )

            checks.append({
                "name": "application_stop",
                "status": "PASS",
                "message": (
                    "Application process stopped."
                ),
                "pid": process.pid,
            })

            return self._build_result(
                "PASS",
                (
                    "Application deployment and "
                    "health checks completed successfully."
                ),
                name,
                host,
                port,
                checks,
                process,
                stdout_file,
                stderr_file,
                log_analysis,
            )

        except Exception as exc:
            if process is not None:
                try:
                    stdout, stderr = (
                        self._stop_and_collect(process)
                    )

                    stdout_file, stderr_file = (
                        self._write_logs(
                            name,
                            stdout,
                            stderr,
                        )
                    )

                    log_analysis = (
                        self._analyze_logs(
                            stdout_file,
                            stderr_file,
                        )
                    )
                except Exception:
                    pass

            return self._build_result(
                "FAIL",
                "Deployment test failed.",
                name,
                host,
                port,
                checks,
                process,
                stdout_file,
                stderr_file,
                log_analysis,
            )
