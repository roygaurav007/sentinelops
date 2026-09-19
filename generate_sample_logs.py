"""
generate_sample_logs.py
Creates a synthetic app.log with realistic, repeating error patterns so
the dashboard has something meaningful to analyze out of the box —
useful both for local testing and for the deployed demo, where there's
no real production traffic to point at.

Run: python generate_sample_logs.py
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent / "sample_logs" / "app.log"

INFO_MESSAGES = [
    "Request completed in 124ms",
    "User session started",
    "Scheduled job 'cleanup_temp_files' finished",
    "Cache refreshed successfully",
    "Health check OK",
]

WARNING_MESSAGES = [
    "Response time exceeded 800ms threshold",
    "Retrying request to payment-service (attempt 2/3)",
    "Deprecated API endpoint /v1/users called",
    "Memory usage above 70%",
]

ERROR_MESSAGES = [
    "Database connection timeout after 30s",
    "NullPointerException in OrderProcessor.finalize()",
    "504 Gateway Timeout calling inventory-service",
    "Failed to write to disk: No space left on device",
    "Unhandled exception in async worker: KeyError('user_id')",
]

CRITICAL_MESSAGES = [
    "Primary database node unreachable — failing over to replica",
    "Out of memory: process killed by OS",
]


def generate(num_lines: int = 400) -> str:
    lines = []
    start = datetime.now() - timedelta(hours=6)

    for i in range(num_lines):
        ts = start + timedelta(seconds=i * random.randint(2, 9))
        roll = random.random()
        if roll < 0.75:
            level, msg = "INFO", random.choice(INFO_MESSAGES)
        elif roll < 0.90:
            level, msg = "WARNING", random.choice(WARNING_MESSAGES)
        elif roll < 0.985:
            level, msg = "ERROR", random.choice(ERROR_MESSAGES)
        else:
            level, msg = "CRITICAL", random.choice(CRITICAL_MESSAGES)
        lines.append(f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {level} {msg}")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(generate())
    print(f"Wrote sample log to {OUTPUT_PATH}")
