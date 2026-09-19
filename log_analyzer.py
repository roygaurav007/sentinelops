"""
log_analyzer.py
Parses application log files into structured data and surfaces
error trends. This is the "software detective" core of the project:
turning raw, unstructured log lines into something you can act on.
"""

import re
from io import StringIO

import pandas as pd

# Matches lines like: 2026-09-19 10:23:01 ERROR Database connection timeout
LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>INFO|WARNING|ERROR|CRITICAL)\s+"
    r"(?P<message>.+)$"
)

SEVERITY_ORDER = {"CRITICAL": 3, "ERROR": 2, "WARNING": 1, "INFO": 0}


def parse_log_text(text: str) -> pd.DataFrame:
    """Parse raw log text into a DataFrame with timestamp/level/message columns."""
    rows = []
    for line in StringIO(text):
        line = line.strip()
        if not line:
            continue
        match = LOG_PATTERN.match(line)
        if match:
            rows.append(match.groupdict())
        else:
            # Keep unparsable lines instead of silently dropping them —
            # this is exactly the kind of "malformed input" handling
            # that matters in a real support/monitoring tool.
            rows.append({"timestamp": None, "level": "UNKNOWN", "message": line})

    df = pd.DataFrame(rows, columns=["timestamp", "level", "message"])
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def parse_log_file(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return parse_log_text(f.read())


def get_level_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Count log lines per severity level."""
    if df.empty:
        return pd.DataFrame(columns=["level", "count"])
    counts = df["level"].value_counts().reset_index()
    counts.columns = ["level", "count"]
    return counts


def get_top_errors(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Return the most frequently recurring ERROR/CRITICAL messages."""
    problem_df = df[df["level"].isin(["ERROR", "CRITICAL"])]
    if problem_df.empty:
        return pd.DataFrame(columns=["message", "count"])
    counts = problem_df["message"].value_counts().head(n).reset_index()
    counts.columns = ["message", "count"]
    return counts


def worst_severity(df: pd.DataFrame) -> str:
    """Return the single worst severity level present in the logs."""
    if df.empty:
        return "INFO"
    levels_present = [lvl for lvl in df["level"].unique() if lvl in SEVERITY_ORDER]
    if not levels_present:
        return "INFO"
    return max(levels_present, key=lambda lvl: SEVERITY_ORDER[lvl])
