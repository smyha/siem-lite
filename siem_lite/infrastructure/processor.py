from typing import Any, Dict, List

from siem_lite.domain.rules import analyze_ssh_bruteforce, analyze_web_attacks


class LogProcessor:
    """
    Processes logs and applies detection rules.
    """

    def process_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes logs and returns detected events.
        """
        ssh_events = analyze_ssh_bruteforce(logs)
        web_events = analyze_web_attacks(logs)
        return {"ssh_bruteforce": ssh_events, "web_attacks": web_events}
