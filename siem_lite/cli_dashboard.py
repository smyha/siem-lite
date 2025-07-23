"""
CLI Dashboard for SIEM Lite.

This module provides a visual command-line interface to display
security alerts stored in the SIEM Lite system database.
"""

import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_URL: str = "http://127.0.0.1:8000/api/alerts"
API_STATS_URL: str = "http://127.0.0.1:8000/api/stats"
API_HEALTH_URL: str = "http://127.0.0.1:8000/health"

# Initialize console
console = Console()


class SIEMDashboard:
    """
    CLI Dashboard for the SIEM Lite system.

    This class provides a visual interface to display security alerts,
    system statistics, and API health status.
    """

    def __init__(self, api_url: str = API_URL):
        """
        Initialize the dashboard.

        Args:
            api_url (str): Base API URL
        """
        self.api_url = api_url
        self.stats_url = f"{api_url.replace('/alerts', '/stats')}"
        self.health_url = f"{api_url.replace('/alerts', '/health')}"

    def get_alerts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Gets alerts from the API.

        Returns:
            Optional[List[Dict[str, Any]]]: List of alerts or None if error
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]❌ Error connecting to API:[/bold red] {e}")
            return None

    def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        Gets system statistics from the API.

        Returns:
            Optional[Dict[str, Any]]: System statistics or None if error
        """
        try:
            response = requests.get(self.stats_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]❌ Error getting statistics:[/bold red] {e}")
            return None

    def get_health_status(self) -> Optional[Dict[str, Any]]:
        """
        Gets API health status.

        Returns:
            Optional[Dict[str, Any]]: Health status or None if error
        """
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 404:
                console.print(
                    "[bold yellow]⚠️ API health endpoint not found. Please check your API version.[/bold yellow]"
                )
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]❌ Error checking API health:[/bold red] {e}")
            return None

    def create_header(self) -> Panel:
        """
        Creates the dashboard header.

        Returns:
            Panel: Panel with dashboard title
        """
        title = Text(
            "SIEM Lite - Security Dashboard", justify="center", style="bold magenta"
        )
        subtitle = Text(
            "Security Information and Event Management System",
            justify="center",
            style="dim",
        )

        header_content = Align.center(title + "\n" + subtitle)
        return Panel(header_content, border_style="green", padding=(1, 2))

    def create_health_panel(self, health_data: Optional[Dict[str, Any]]) -> Panel:
        """
        Creates the system health status panel.

        Args:
            health_data (Optional[Dict[str, Any]]): System health data

        Returns:
            Panel: Panel with health status
        """
        if health_data is None:
            content = Text("❌ Not available", style="red")
            border_style = "red"
        else:
            status = health_data.get("status", "unknown")
            db_status = health_data.get("database", "unknown")

            if status == "healthy" and db_status == "connected":
                content = Text("✅ System Operational", style="green")
                border_style = "green"
            else:
                content = Text(f"⚠️ System: {status}, DB: {db_status}", style="yellow")
                border_style = "yellow"

        return Panel(content, title="System Status", border_style=border_style)

    def create_stats_panel(self, stats_data: Optional[Dict[str, Any]]) -> Panel:
        """
        Creates the system statistics panel.

        Args:
            stats_data (Optional[Dict[str, Any]]): Statistics data

        Returns:
            Panel: Panel with statistics
        """
        if stats_data is None:
            content = Text("❌ Not available", style="red")
            border_style = "red"
        else:
            total_alerts = stats_data.get("total_alerts", 0)
            alert_types = stats_data.get("alert_types", {})

            content_lines = [
                f"📊 Total alerts: {total_alerts:,}",
                f"📈 Alert types: {len(alert_types)}",
            ]

            # Show top IPs if available
            top_ips = stats_data.get("top_source_ips", {})
            if top_ips:
                content_lines.append(f"🌐 Unique IPs: {len(top_ips)}")

            content = Text("\n".join(content_lines), style="cyan")
            border_style = "blue"

        return Panel(content, title="Statistics", border_style=border_style)

    def create_alerts_table(self, alerts: List[Dict[str, Any]]) -> Table:
        """
        Creates the security alerts table.

        Args:
            alerts (List[Dict[str, Any]]): List of alerts to display

        Returns:
            Table: Table with formatted alerts
        """
        table = Table(
            title="🚨 Detected Security Alerts",
            show_header=True,
            header_style="bold blue",
            border_style="blue",
        )

        # Define columns
        table.add_column("ID", style="dim", width=6, justify="center")
        table.add_column("Timestamp", style="cyan", width=20)
        table.add_column("Alert Type", style="green", width=25)
        table.add_column("Source IP", style="yellow", width=15)
        table.add_column("Details", style="white", width=50)

        # Add rows
        for alert in alerts:
            # Format timestamp for better readability
            timestamp_str = alert.get("timestamp", "")
            if isinstance(timestamp_str, str):
                # Remove milliseconds if present
                timestamp = timestamp_str.replace("T", " ").split(".")[0]
            else:
                timestamp = str(timestamp_str)

            # Determine alert type style
            alert_type = alert.get("alert_type", "")
            if "SSH" in alert_type:
                alert_style = "bold red"
            elif "Web" in alert_type:
                alert_style = "bold orange"
            else:
                alert_style = "green"

            table.add_row(
                str(alert.get("id", "")),
                timestamp,
                Text(alert_type, style=alert_style),
                alert.get("source_ip", ""),
                alert.get("details", ""),
            )

        return table

    def display_dashboard(self, alerts: Optional[List[Dict[str, Any]]]) -> None:
        """
        Displays the complete dashboard with alerts and statistics.

        Args:
            alerts (Optional[List[Dict[str, Any]]]): List of alerts to display
        """
        # Get additional data
        health_data = self.get_health_status()
        stats_data = self.get_stats()

        # Create layout
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="main"))

        layout["main"].split_row(
            Layout(name="sidebar", ratio=1), Layout(name="content", ratio=3)
        )

        # Add content
        layout["header"].update(self.create_header())

        # Sidebar with statistics
        sidebar_panels = [
            self.create_health_panel(health_data),
            self.create_stats_panel(stats_data),
        ]
        layout["sidebar"].update(Panel(Columns(sidebar_panels), border_style="blue"))

        # Main content
        if alerts is None:
            content = Panel(
                "[yellow]Could not load alerts. Verify that the API is running.[/yellow]",
                title="Connection Error",
                border_style="yellow",
            )
        elif not alerts:
            content = Panel(
                "[green]✅ No security alerts found.[/green]",
                title="Security Status",
                border_style="green",
            )
        else:
            content = self.create_alerts_table(alerts)

        layout["content"].update(content)

        # Display dashboard
        console.print(layout)

        # Show summary
        if alerts:
            console.print(
                f"\n[bold cyan]📊 Displaying {len(alerts)} security alerts[/bold cyan]"
            )
        else:
            console.print(
                "\n[bold green]✅ System without security alerts[/bold green]"
            )

    def run(self) -> None:
        """
        Runs the dashboard.
        """
        try:
            console.print("[bold blue]🔄 Loading dashboard...[/bold blue]")
            alerts = self.get_alerts()
            self.display_dashboard(alerts)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]👋 Dashboard closed by user[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")
            logger.error(f"Error in dashboard: {e}")
            console.print("[bold yellow]Returning to main menu...[/bold yellow]")
            time.sleep(2)


def main() -> None:
    """
    Main function to run the dashboard.
    """
    try:
        dashboard = SIEMDashboard()
        dashboard.run()
    except Exception as e:
        console.print(f"[bold red]❌ Error starting dashboard: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
