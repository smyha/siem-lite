import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

LOG_TYPES = ["sshd", "nginx"]


def generate_sample_logs(
    count: int = 100, output_file: Optional[str] = None
) -> List[Dict[str, any]]:
    """
    Generates simulated log entries for testing and analysis.
    If output_file is provided, writes logs to file. Otherwise, returns a list.
    """
    logs = []
    now = datetime.now()
    for i in range(count):
        log_type = random.choice(LOG_TYPES)
        ip = f"192.168.1.{random.randint(1, 254)}"
        status_code = (
            random.choice([200, 404, 403, 500]) if log_type == "nginx" else None
        )
        log = {
            "log_type": log_type,
            "ip": ip,
            "status_code": status_code,
            "timestamp": now - timedelta(seconds=random.randint(0, 3600)),
        }
        logs.append(log)
    if output_file:
        import json

        with open(output_file, "w") as f:
            json.dump(logs, f, default=str, indent=2)
    return logs
