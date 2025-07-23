from typing import Any, Dict, List


class FeatureExtractor:
    """
    Extracts features from logs or alerts for further analysis or ML.
    """

    @staticmethod
    def extract_basic_features(log: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts basic features from a log entry."""
        return {
            "ip": log.get("ip"),
            "log_type": log.get("log_type"),
            "status_code": log.get("status_code"),
            "timestamp": log.get("timestamp"),
        }

    @staticmethod
    def extract_advanced_features(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extracts aggregate features from a list of logs."""
        return {
            "unique_ips": len(set(l["ip"] for l in logs)),
            "error_count": sum(1 for l in logs if l.get("status_code", 200) >= 400),
        }
