from datetime import datetime, timedelta
from typing import Any, Dict, List


def analyze_ssh_bruteforce(
    logs: List[Dict[str, Any]], window_seconds: int = 60, threshold: int = 5
) -> List[Dict[str, Any]]:
    """
    Detects SSH brute-force attempts in logs.
    Returns a list of detected brute-force events.
    """
    events = []
    logs = [l for l in logs if l.get("log_type") == "sshd"]
    logs.sort(key=lambda l: l["timestamp"])
    for i, log in enumerate(logs):
        ip = log.get("ip")
        if not ip:
            continue
        window = [l for l in logs[max(0, i - threshold + 1) : i + 1] if l["ip"] == ip]
        if len(window) >= threshold:
            t0 = window[0]["timestamp"]
            t1 = window[-1]["timestamp"]
            if (t1 - t0).total_seconds() <= window_seconds:
                events.append({"ip": ip, "start": t0, "end": t1, "count": len(window)})
    return events


def analyze_web_attacks(
    logs: List[Dict[str, Any]], window_seconds: int = 60, threshold: int = 10
) -> List[Dict[str, Any]]:
    """
    Detects web attacks (e.g., many HTTP errors) in logs.
    Returns a list of detected web attack events.
    """
    events = []
    logs = [l for l in logs if l.get("log_type") == "nginx"]
    logs.sort(key=lambda l: l["timestamp"])
    for i, log in enumerate(logs):
        ip = log.get("ip")
        if not ip:
            continue
        window = [
            l
            for l in logs[max(0, i - threshold + 1) : i + 1]
            if l["ip"] == ip and l.get("status_code", 200) >= 400
        ]
        if len(window) >= threshold:
            t0 = window[0]["timestamp"]
            t1 = window[-1]["timestamp"]
            if (t1 - t0).total_seconds() <= window_seconds:
                events.append({"ip": ip, "start": t0, "end": t1, "count": len(window)})
    return events
