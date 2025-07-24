"""
Attack simulation module for generating realistic security events for testing.
"""
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import ipaddress
from pathlib import Path


class AttackSimulator:
    """Simulates various types of cyber attacks for testing SIEM capabilities."""
    
    def __init__(self):
        self.attack_patterns = {
            "brute-force": {
                "source_ips": ["192.168.1.100", "10.0.0.50", "172.16.0.200", "203.0.113.10"],
                "user_agents": [
                    "Mozilla/5.0 (compatible; AttackBot/1.0)",
                    "curl/7.68.0",
                    "python-requests/2.25.1",
                    "Hydra/9.0"
                ],
                "target_services": ["ssh", "ftp", "http", "rdp"],
                "common_usernames": ["admin", "root", "user", "test", "guest"],
                "severity": "HIGH"
            },
            "sql-injection": {
                "source_ips": ["198.51.100.25", "203.0.113.50", "192.0.2.100"],
                "payloads": [
                    "' OR '1'='1",
                    "'; DROP TABLE users; --",
                    "' UNION SELECT * FROM passwords --",
                    "1' AND (SELECT COUNT(*) FROM information_schema.tables) > 0 --"
                ],
                "target_urls": ["/login", "/search", "/api/users", "/admin/panel"],
                "severity": "CRITICAL"
            },
            "ddos": {
                "source_ips": self._generate_botnet_ips(50),
                "request_rates": [1000, 5000, 10000],  # requests per minute
                "target_ports": [80, 443, 8080, 3000],
                "attack_vectors": ["SYN flood", "HTTP flood", "UDP flood"],
                "severity": "HIGH"
            }
        }
    
    def _generate_botnet_ips(self, count: int) -> List[str]:
        """Generate realistic botnet IP addresses from various ranges."""
        ranges = [
            "192.168.0.0/16",
            "10.0.0.0/8", 
            "172.16.0.0/12",
            "203.0.113.0/24",
            "198.51.100.0/24"
        ]
        
        ips = []
        for _ in range(count):
            network = ipaddress.IPv4Network(random.choice(ranges))
            ip = str(network.network_address + random.randint(1, network.num_addresses - 2))
            ips.append(ip)
        return ips
    
    def generate_attack_events(self, attack_type: str, count: int, output_file: str) -> None:
        """Generate a batch of attack events."""
        events = []
        
        for i in range(count):
            if attack_type == "mixed":
                current_type = random.choice(["brute-force", "sql-injection", "ddos"])
            else:
                current_type = attack_type
            
            event = self._create_attack_event(current_type, i)
            events.append(event)
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Write events to log file
        with open(output_file, "w", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
    
    def run_continuous_simulation(self, attack_type: str, duration: int, output_file: str) -> None:
        """Run continuous attack simulation for specified duration."""
        start_time = time.time()
        event_count = 0
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            while time.time() - start_time < duration:
                if attack_type == "mixed":
                    current_type = random.choice(["brute-force", "sql-injection", "ddos"])
                else:
                    current_type = attack_type
                
                event = self._create_attack_event(current_type, event_count)
                f.write(json.dumps(event) + "\n")
                f.flush()  # Ensure immediate write
                
                event_count += 1
                
                # Variable delay between events (1-10 seconds)
                delay = random.uniform(1, 10)
                time.sleep(delay)
    
    def _create_attack_event(self, attack_type: str, sequence: int) -> Dict[str, Any]:
        """Create a realistic attack event based on type."""
        base_time = datetime.now() - timedelta(minutes=random.randint(0, 60))
        
        if attack_type == "brute-force":
            return self._create_brute_force_event(base_time, sequence)
        elif attack_type == "sql-injection":
            return self._create_sql_injection_event(base_time, sequence)
        elif attack_type == "ddos":
            return self._create_ddos_event(base_time, sequence)
        else:
            raise ValueError(f"Unknown attack type: {attack_type}")
    
    def _create_brute_force_event(self, timestamp: datetime, sequence: int) -> Dict[str, Any]:
        """Create a brute force attack event."""
        pattern = self.attack_patterns["brute-force"]
        
        return {
            "id": f"bf_{sequence:05d}_{int(timestamp.timestamp())}",
            "timestamp": timestamp.isoformat(),
            "event_type": "authentication_failure",
            "source_ip": random.choice(pattern["source_ips"]),
            "destination_ip": "192.168.1.10",
            "service": random.choice(pattern["target_services"]),
            "username": random.choice(pattern["common_usernames"]),
            "user_agent": random.choice(pattern["user_agents"]),
            "attempts": random.randint(5, 50),
            "severity": pattern["severity"],
            "details": {
                "attack_type": "brute-force",
                "failed_passwords": random.randint(10, 100),
                "attack_duration": random.randint(30, 300),
                "protocol": "SSH" if random.random() > 0.5 else "HTTP"
            },
            "raw_log": f"Failed login attempt for user '{random.choice(pattern['common_usernames'])}' from {random.choice(pattern['source_ips'])}"
        }
    
    def _create_sql_injection_event(self, timestamp: datetime, sequence: int) -> Dict[str, Any]:
        """Create a SQL injection attack event."""
        pattern = self.attack_patterns["sql-injection"]
        
        return {
            "id": f"sqli_{sequence:05d}_{int(timestamp.timestamp())}",
            "timestamp": timestamp.isoformat(),
            "event_type": "web_attack",
            "source_ip": random.choice(pattern["source_ips"]),
            "destination_ip": "192.168.1.20",
            "target_url": random.choice(pattern["target_urls"]),
            "payload": random.choice(pattern["payloads"]),
            "http_method": "POST",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "severity": pattern["severity"],
            "details": {
                "attack_type": "sql-injection",
                "injection_type": random.choice(["union", "boolean", "time-based", "error-based"]),
                "database_targeted": random.choice(["users", "products", "orders", "admin"]),
                "response_code": random.choice([200, 500, 403])
            },
            "raw_log": f"Suspicious SQL query detected in parameter: {random.choice(pattern['payloads'])}"
        }
    
    def _create_ddos_event(self, timestamp: datetime, sequence: int) -> Dict[str, Any]:
        """Create a DDoS attack event."""
        pattern = self.attack_patterns["ddos"]
        
        return {
            "id": f"ddos_{sequence:05d}_{int(timestamp.timestamp())}",
            "timestamp": timestamp.isoformat(),
            "event_type": "network_attack",
            "source_ip": random.choice(pattern["source_ips"]),
            "destination_ip": "192.168.1.30",
            "destination_port": random.choice(pattern["target_ports"]),
            "request_rate": random.choice(pattern["request_rates"]),
            "attack_vector": random.choice(pattern["attack_vectors"]),
            "severity": pattern["severity"],
            "details": {
                "attack_type": "ddos",
                "packet_size": random.randint(64, 1500),
                "connection_count": random.randint(1000, 50000),
                "bandwidth_mbps": random.randint(100, 1000),
                "botnet_size": random.randint(100, 10000)
            },
            "raw_log": f"High traffic volume detected from {random.choice(pattern['source_ips'])} - {random.choice(pattern['request_rates'])} req/min"
        }
    
    def generate_normal_traffic(self, count: int, output_file: str) -> None:
        """Generate normal/legitimate traffic events for baseline comparison."""
        events = []
        
        legitimate_ips = ["192.168.1.50", "192.168.1.51", "192.168.1.52"]
        legitimate_activities = [
            "user_login", "file_access", "email_sent", "report_generated",
            "backup_completed", "system_update", "password_changed"
        ]
        
        for i in range(count):
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # Last 24 hours
            
            event = {
                "id": f"normal_{i:05d}_{int(timestamp.timestamp())}",
                "timestamp": timestamp.isoformat(),
                "event_type": random.choice(legitimate_activities),
                "source_ip": random.choice(legitimate_ips),
                "user": f"user{random.randint(1, 50)}",
                "severity": "INFO",
                "details": {
                    "activity": "normal_operations",
                    "success": True,
                    "duration": random.randint(1, 30)
                },
                "raw_log": f"Normal activity: {random.choice(legitimate_activities)} by user{random.randint(1, 50)}"
            }
            events.append(event)
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
