"""
monitor.py
Collects live system health metrics (CPU, memory, disk, uptime).
Isolated from the UI so it can be unit-tested or reused by a
non-Streamlit entry point (e.g. a CLI or a scheduled job) later.
"""

from datetime import datetime, timedelta

import psutil


def get_system_metrics() -> dict:
    """Return a snapshot of current system health."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "cpu_percent": cpu_percent,
        "memory_percent": mem.percent,
        "memory_used_gb": round(mem.used / (1024**3), 2),
        "memory_total_gb": round(mem.total / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "uptime": str(timedelta(seconds=int(uptime.total_seconds()))),
        "process_count": len(psutil.pids()),
    }


def get_top_processes(n: int = 5) -> list:
    """Return the n processes using the most CPU right now."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
    return procs[:n]
