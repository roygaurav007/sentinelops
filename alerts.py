"""
alerts.py
Turns raw metrics/log data into actionable alerts once they cross
configurable thresholds, and hands them to db.py for persistence.
"""

from db import insert_alert


def check_metric_thresholds(
    metrics: dict, cpu_threshold: float = 80.0, mem_threshold: float = 85.0
) -> list:
    """Compare live metrics against thresholds and return triggered alerts."""
    triggered = []

    if metrics["cpu_percent"] >= cpu_threshold:
        triggered.append(
            {
                "source": "system",
                "severity": "WARNING" if metrics["cpu_percent"] < 95 else "CRITICAL",
                "message": f"CPU usage at {metrics['cpu_percent']}% (threshold {cpu_threshold}%)",
            }
        )

    if metrics["memory_percent"] >= mem_threshold:
        triggered.append(
            {
                "source": "system",
                "severity": "WARNING" if metrics["memory_percent"] < 95 else "CRITICAL",
                "message": f"Memory usage at {metrics['memory_percent']}% (threshold {mem_threshold}%)",
            }
        )

    for alert in triggered:
        insert_alert(alert["source"], alert["severity"], alert["message"])

    return triggered


def check_log_spikes(level_counts_df, error_threshold: int = 5) -> list:
    """Flag when ERROR/CRITICAL counts in a parsed log batch exceed a threshold."""
    triggered = []
    for _, row in level_counts_df.iterrows():
        if row["level"] in ("ERROR", "CRITICAL") and row["count"] >= error_threshold:
            alert = {
                "source": "logs",
                "severity": row["level"],
                "message": f"{row['count']} '{row['level']}' entries found in the analyzed log",
            }
            triggered.append(alert)
            insert_alert(alert["source"], alert["severity"], alert["message"])
    return triggered
