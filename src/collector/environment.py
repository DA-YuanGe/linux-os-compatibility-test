#!/usr/bin/env python3

import json
import platform
import subprocess
from pathlib import Path


class EnvironmentCollector:
    """Collect Linux environment information."""

    def collect_os(self):
        os_info = {}

        try:
            content = Path("/etc/os-release").read_text(encoding="utf-8")

            for line in content.splitlines():
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                os_info[key] = value.strip('"')

        except OSError as exc:
            os_info["error"] = str(exc)

        return {
            "name": os_info.get("NAME", ""),
            "pretty_name": os_info.get("PRETTY_NAME", ""),
            "version_id": os_info.get("VERSION_ID", ""),
            "version": os_info.get("VERSION", ""),
            "id": os_info.get("ID", ""),
            "id_like": os_info.get("ID_LIKE", ""),
        }

    def collect_kernel(self):
        uname = platform.uname()

        return {
            "system": uname.system,
            "release": uname.release,
            "version": uname.version,
            "node": uname.node,
        }

    def collect_cpu(self):
        result = subprocess.run(
            ["lscpu"],
            capture_output=True,
            text=True,
            check=True,
        )

        cpu_info = {}

        for line in result.stdout.splitlines():
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            cpu_info[key.strip()] = value.strip()

        return {
            "architecture": cpu_info.get("Architecture", ""),
            "model_name": cpu_info.get("Model name", ""),
            "logical_cpus": int(cpu_info.get("CPU(s)", "0")),
            "cores_per_socket": int(
                cpu_info.get("Core(s) per socket", "0")
            ),
            "sockets": int(cpu_info.get("Socket(s)", "0")),
            "threads_per_core": int(
                cpu_info.get("Thread(s) per core", "0")
            ),
            "virtualization": cpu_info.get("Virtualization", ""),
            "hypervisor_vendor": cpu_info.get("Hypervisor vendor", ""),
        }

    def collect_memory(self):
        result = subprocess.run(
            ["free", "-m"],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.splitlines()

        for line in lines:
            if line.startswith("Mem:"):
                parts = line.split()

                return {
                    "total_mb": int(parts[1]),
                    "used_mb": int(parts[2]),
                    "free_mb": int(parts[3]),
                    "available_mb": int(parts[6]),
                }

        return {}

    def collect_disk(self):
        result = subprocess.run(
            ["df", "-B1", "/"],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.splitlines()

        if len(lines) < 2:
            return {}

        parts = lines[1].split()

        total_bytes = int(parts[1])
        used_bytes = int(parts[2])
        available_bytes = int(parts[3])
        usage_percent = int(parts[4].rstrip("%"))

        return {
            "mount": parts[5],
            "total_bytes": total_bytes,
            "used_bytes": used_bytes,
            "available_bytes": available_bytes,
            "usage_percent": usage_percent,
        }

    def collect(self):
        return {
            "os": self.collect_os(),
            "kernel": self.collect_kernel(),
            "cpu": self.collect_cpu(),
            "memory": self.collect_memory(),
            "disk": self.collect_disk(),
        }


def main():
    collector = EnvironmentCollector()
    result = collector.collect()

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
