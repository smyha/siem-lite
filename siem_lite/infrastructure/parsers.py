import json
from typing import Any, Dict


def parse_log_line(line: str) -> Dict[str, Any]:
    """
    Parses a single log line (JSON or simple format) into a dictionary.
    """
    try:
        return json.loads(line)
    except Exception:
        # Fallback: parse space-separated key=value
        parts = line.strip().split()
        log = {}
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                log[k] = v
        return log
