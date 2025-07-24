#!/usr/bin/env python3
"""
SIEM Lite - Main CLI Application

A comprehensive command-line interface for the SIEM Lite security system.
Provides access to all features including dashboard, analysis, monitoring, and reporting.
"""

import os
import platform
import signal
import subprocess
import sys
import threading
import time
import atexit
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click
import questionary
try:
    import psutil
    import requests
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    import requests
    import psutil

from siem_lite.domain.entities import Alert
from siem_lite.domain.services import AlertService
from siem_lite.infrastructure.database import get_db, init_database
from siem_lite.infrastructure.log_generator import generate_sample_logs
from siem_lite.infrastructure.parsers import parse_log_line
from siem_lite.infrastructure.processor import LogProcessor
from siem_lite.infrastructure.report_generator import LaTeXReportGenerator
from siem_lite.infrastructure.repositories import SQLAlchemyAlertRepository
from siem_lite.utils.i18n import i18n
from siem_lite.utils.i18n import set_language as set_global_language
from siem_lite.utils.i18n import t
from siem_lite.utils.config import get_settings

# ASCII banner for CLI (Bloody ASCII art)
ASCII_BANNER = r"""
  ██████  ███▄ ▄███▓▓██   ██▓ ██░ ██  ▄▄▄        ██████      ██████  ██▓▓█████  ███▄ ▄███▓
▒██    ▒ ▓██▒▀█▀ ██▒ ▒██  ██▒▓██░ ██▒▒████▄    ▒██    ▒    ▒██    ▒ ▓██▒▓█   ▀ ▓██▒▀█▀ ██▒
░ ▓██▄   ▓██    ▓██░  ▒██ ██░▒██▀▀██░▒██  ▀█▄  ░ ▓██▄      ░ ▓██▄   ▒██▒▒███   ▓██    ▓██░
  ▒   ██▒▒██    ▒██   ░ ▐██▓░░▓█ ░██ ░██▄▄▄▄██   ▒   ██▒     ▒   ██▒░██░▒▓█  ▄ ▒██    ▒██ 
▒██████▒▒▒██▒   ░██▒  ░ ██▒▓░░▓█▒░██▓ ▓█   ▓██▒▒██████▒▒   ▒██████▒▒░██░░▒████▒▒██▒   ░██▒
▒ ▒▓▒ ▒ ░░ ▒░   ░  ░   ██▒▒▒  ▒ ░░▒░▒ ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░   ▒ ▒▓▒ ▒ ░░▓  ░░ ▒░ ░░ ▒░   ░  ░
░ ░▒  ░ ░░  ░      ░ ▓██ ░▒░  ▒ ░▒░ ░  ▒   ▒▒ ░░ ░▒  ░ ░   ░ ░▒  ░ ░ ▒ ░ ░ ░  ░░  ░      ░
░  ░  ░  ░      ░    ▒ ▒ ░░   ░  ░░ ░  ░   ▒   ░  ░  ░     ░  ░  ░   ▒ ░   ░   ░      ░   
      ░         ░    ░ ░      ░  ░  ░      ░  ░      ░           ░   ░     ░  ░       ░  
 🛡️  Security Information and Event Management System
"""

# Global console for output
if RICH_AVAILABLE:
    console = Console()
else:
    console = None

# Global process manager for cleanup
class ProcessManager:
    """Manages background processes for the CLI."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.is_shutting_down = False
        
    def add_process(self, process: subprocess.Popen) -> None:
        """Add a process to be managed."""
        self.processes.append(process)
        
    def cleanup_all(self) -> None:
        """Clean up all managed processes."""
        if self.is_shutting_down:
            return
            
        self.is_shutting_down = True
        if console:
            console.print("\n🧹 Cleaning up processes...", style="yellow")
        else:
            print("\n🧹 Cleaning up processes...")
        
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            except Exception as e:
                if console:
                    console.print(f"Error cleaning up process: {e}", style="red")
                else:
                    print(f"Error cleaning up process: {e}")
        
        if console:
            console.print("✅ Cleanup completed", style="green")
        else:
            print("✅ Cleanup completed")

# Global instance
process_manager = ProcessManager()

# Initialize Rich console
console = None
if RICH_AVAILABLE:
    console = Console()

# Register cleanup on exit
atexit.register(process_manager.cleanup_all)

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    process_manager.cleanup_all()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class ServiceMonitor:
    """Monitor the status of various services."""
    
    def __init__(self):
        self.settings = get_settings()
        
    def check_api_server(self) -> dict:
        """Check API server status."""
        try:
            response = requests.get(
                f"http://{self.settings.api.host}:{self.settings.api.port}/api/health",
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "running",
                    "uptime": data.get("uptime", "unknown"),
                    "version": data.get("version", "unknown")
                }
            else:
                return {"status": "unhealthy", "code": response.status_code}
        except requests.RequestException:
            return {"status": "stopped"}
    
    def check_database(self) -> dict:
        """Check database status."""
        try:
            from siem_lite.infrastructure.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            return {"status": "running"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_system_stats(self) -> dict:
        """Get system resource statistics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if platform.system() != "Windows" 
                           else psutil.disk_usage('C:').percent
        }



def print_banner():
    """Print the SIEM Lite banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                         🛡️  SIEM LITE                         ║
║                   Security Information & Event                ║
║                      Management System                        ║
╚═══════════════════════════════════════════════════════════════╝
"""
    if console:
        console.print(banner, style="bold cyan")
    else:
        print(banner)


def create_status_table() -> Table:
    """Create a status table for the live display."""
    if not RICH_AVAILABLE:
        return None
        
    table = Table(title="🛡️ SIEM Lite System Status")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")
    
    monitor = ServiceMonitor()
    
    # API Server status
    api_status = monitor.check_api_server()
    if api_status["status"] == "running":
        table.add_row("🌐 API Server", "✅ Running", 
                     f"Uptime: {api_status.get('uptime', 'Unknown')}")
    elif api_status["status"] == "unhealthy":
        table.add_row("🌐 API Server", "⚠️ Unhealthy", 
                     f"HTTP {api_status.get('code', 'Unknown')}")
    else:
        table.add_row("🌐 API Server", "❌ Stopped", "Not responding")
    
    # Database status
    db_status = monitor.check_database()
    if db_status["status"] == "running":
        table.add_row("🗄️ Database", "✅ Running", "Connection OK")
    else:
        table.add_row("🗄️ Database", "❌ Error", 
                     db_status.get("error", "Unknown error"))
    
    # System resources
    sys_stats = monitor.get_system_stats()
    table.add_row("💻 CPU Usage", f"{sys_stats['cpu_percent']:.1f}%", "")
    table.add_row("🧠 Memory Usage", f"{sys_stats['memory_percent']:.1f}%", "")
    table.add_row("💾 Disk Usage", f"{sys_stats['disk_percent']:.1f}%", "")
    
    return table


def start_api_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> subprocess.Popen:
    """Start the FastAPI server as a background process."""
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "siem_lite.main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", "info",
    ]
    
    if reload:
        cmd.append("--reload")
    
    if console:
        console.print(f"🚀 Starting API server on http://{host}:{port}")
    else:
        print(f"🚀 Starting API server on http://{host}:{port}")
    
    # Use environment variables for subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd(),
        env=env
    )
    
    process_manager.add_process(process)
    return process


def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wait for a service to become available."""
    start_time = time.time()
    
    if RICH_AVAILABLE and console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Waiting for service...", total=None)
            
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        progress.update(task, description="✅ Service ready!")
                        return True
                except requests.RequestException:
                    pass
                time.sleep(1)
                progress.update(task, description=f"Waiting... ({int(time.time() - start_time)}s)")
    else:
        print("⏳ Waiting for API server to start...")
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print("✅ Service ready!")
                    return True
            except requests.RequestException:
                pass
            time.sleep(1)
            print(f"Waiting... ({int(time.time() - start_time)}s)")
    
    return False


def confirm_exit():
    """Show confirmation dialog for exiting the program."""
    try:
        confirm = questionary.confirm(
            "🤔 Are you sure you want to exit SIEM Lite?",
            default=False,
            style=questionary.Style([
                ("question", "bold fg:#ff6b6b"),
                ("answer", "fg:#4ecdc4 bold"),
            ])
        ).ask()
        return confirm
    except (KeyboardInterrupt, EOFError):
        return True  # If user presses Ctrl+C, exit


def handle_esc_key():
    """Handle Esc key press - return to previous menu or exit with confirmation."""
    return None  # This will be handled by questionary's built-in Esc handling


def create_menu_choices(menu_type="main"):
    """Create menu choices based on menu type."""
    if menu_type == "main":
        return [
            questionary.Choice(
                f"📊  {t('dashboard_title', 'Live Dashboard')}", "dashboard"
            ),
            questionary.Choice(
                f"📈  {t('statistics', 'System Status')}", "status"
            ),
            questionary.Choice(
                f"🔍  {t('monitor', 'Monitor (real-time)')}", "monitor"
            ),
            questionary.Choice(
                f"📝  {t('log_generation_start', 'Generate Logs')}", "generate"
            ),
            questionary.Choice(
                f"⚙️  {t('processing_start', 'Process Logs')}", "process"
            ),
            questionary.Choice(
                f"🛡️  {t('analyze_threats', 'Analyze Threats')}",
                "analyze-threats",
            ),
            questionary.Choice(f"📤  {t('export', 'Export Data')}", "export"),
            questionary.Choice(f"🛠️  {t('setup', 'Regenerate Environment')}", "setup"),
            questionary.Choice(
                f"🌐  {t('change_language', 'Change Language')}",
                "change-language",
            ),
            questionary.Choice(f"🛑  Stop Services", "stop"),
            questionary.Choice(f"❌  {t('exit', 'Exit')}", "exit"),
        ]
    return []


def get_settings():
    """Get application settings with defaults."""
    class Settings:
        class API:
            host = "127.0.0.1"
            port = 8000
        
        api = API()
    
    return Settings()


# --- Utility: Start API server if not running ---
def is_api_running():
    try:
        settings = get_settings()
        r = requests.get(f"http://{settings.api.host}:{settings.api.port}/api/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


# --- Improved Interactive Menu ---
def show_interactive_menu():
    """Enhanced interactive menu with automatic API and database startup."""
    language = i18n.language if hasattr(i18n, "language") else "en"
    
    # Initialize console
    if RICH_AVAILABLE:
        console = Console()
    else:
        pass
    
    # Auto-start services
    if console and RICH_AVAILABLE:
        console.print("🚀 Starting SIEM Lite System...", style="bold blue")
        console.print("1️⃣ Initializing database...", style="cyan")
    else:
        click.echo("🚀 Starting SIEM Lite System...")
        click.echo("1️⃣ Initializing database...")
    
    try:
        init_database()
        if console and RICH_AVAILABLE:
            console.print("✅ Database initialized successfully!", style="green")
        else:
            click.echo("✅ Database initialized successfully!")
    except Exception as e:
        if console and RICH_AVAILABLE:
            console.print(f"❌ Database initialization failed: {e}", style="red")
        else:
            click.echo(f"❌ Database initialization failed: {e}")
        return
    
    # Start API server if not running
    if not is_api_running():
        if console and RICH_AVAILABLE:
            console.print("2️⃣ Starting API server...", style="cyan")
        else:
            click.echo("2️⃣ Starting API server...")
        
        api_process = start_api_server()
        
        # Wait for server to be ready
        health_url = "http://127.0.0.1:8000/api/health"
        if wait_for_service(health_url, timeout=30):
            if console and RICH_AVAILABLE:
                console.print("✅ API server started successfully!", style="green")
                console.print("🌐 API available at: http://127.0.0.1:8000", style="bold green")
                console.print("📚 Documentation: http://127.0.0.1:8000/docs", style="blue")
            else:
                click.echo("✅ API server started successfully!")
                click.echo("🌐 API available at: http://127.0.0.1:8000")
                click.echo("📚 Documentation: http://127.0.0.1:8000/docs")
        else:
            if console and RICH_AVAILABLE:
                console.print("❌ Failed to start API server", style="red")
            else:
                click.echo("❌ Failed to start API server")
    else:
        if console and RICH_AVAILABLE:
            console.print("✅ API server already running!", style="green")
        else:
            click.echo("✅ API server already running!")
    
    # Main interactive loop
    while True:
        if console and RICH_AVAILABLE:
            console.clear()
            print_banner()
            
            # Show system status
            monitor = ServiceMonitor()
            api_status = monitor.check_api_server()
            db_status = monitor.check_database()
            
            status_panel = Panel(
                f"🌐 API Server: {'✅ Running' if api_status['status'] == 'running' else '❌ Stopped'}\n"
                f"🗄️ Database: {'✅ Connected' if db_status['status'] == 'running' else '❌ Error'}\n"
                f"🕐 {datetime.now().strftime('%H:%M:%S')}",
                title="System Status",
                border_style="green" if api_status['status'] == 'running' else "red"
            )
            console.print(status_panel)
        else:
            click.clear()
            click.echo(ASCII_BANNER)
            click.echo(f"\n🛡️ SIEM Lite - Security Information and Event Management [{language.upper()}]\n")
        
        click.echo(f"{t('cli_exit', 'Press Esc to exit, Ctrl+C at any time to force exit.')}\n")
        
        try:
            choice = questionary.select(
                f"\n{t('cli_refresh', '[Main Menu] What do you want to do?')}",
                choices=create_menu_choices("main"),
                style=questionary.Style(
                    [
                        ("qmark", "fg:#ff9d00 bold"),
                        ("question", "bold"),
                        ("answer", "fg:#00ff6f bold"),
                        ("pointer", "fg:#00bfff bold"),
                        ("highlighted", "fg:#ff9d00 bold"),
                        ("selected", "fg:#00ff6f bold"),
                    ]
                ),
                use_shortcuts=True,
                instruction="(Use arrow keys, Enter to select, Esc to exit)"
            ).ask()
            
            # Handle Esc key (questionary returns None when Esc is pressed)
            if choice is None:
                if confirm_exit():
                    if console and RICH_AVAILABLE:
                        console.print("🛑 Stopping services...", style="yellow")
                    else:
                        click.echo("🛑 Stopping services...")
                    
                    process_manager.cleanup_all()
                    
                    if console and RICH_AVAILABLE:
                        console.print("👋 Goodbye!", style="bold blue")
                    else:
                        click.echo("👋 Goodbye!")
                    break
                else:
                    continue  # Return to menu
            
            if choice == "dashboard":
                launch_live_dashboard()
            elif choice == "status":
                show_detailed_status()
                input("\nPress Enter to continue...")
            elif choice == "monitor":
                try:
                    monitor_cmd()
                except Exception as e:
                    click.echo(f"❌ {t('error_generic', 'Error in monitoring')}: {e}")
                    time.sleep(2)
            elif choice == "generate":
                interactive_generate()
            elif choice == "process":
                interactive_process()
            elif choice == "analyze-threats":
                try:
                    analyze_threats_cmd()
                except Exception as e:
                    click.echo(
                        f"❌ {t('error_generic', 'Error analyzing threats')}: {e}"
                    )
                    time.sleep(2)
            elif choice == "export":
                interactive_export()
            elif choice == "setup":
                try:
                    setup_cmd()
                except Exception as e:
                    click.echo(f"❌ {t('error_generic', 'Error during setup')}: {e}")
                    time.sleep(2)
            elif choice == "stop":
                stop_services()
            elif choice == "change-language":
                change_language_interactive()
            elif choice == "exit":
                if console and RICH_AVAILABLE:
                    console.print("🛑 Stopping services...", style="yellow")
                else:
                    click.echo("🛑 Stopping services...")
                
                process_manager.cleanup_all()
                
                if console and RICH_AVAILABLE:
                    console.print("👋 Goodbye!", style="bold blue")
                else:
                    click.echo(f"👋 {t('cli_exit', 'Goodbye!')}")
                break
            else:
                click.echo(
                    f"❓ {t('error_generic', 'Unknown option. Returning to menu.')}"
                )
                time.sleep(1)
        except (KeyboardInterrupt, EOFError):
            if console and RICH_AVAILABLE:
                console.print("\n🛑 Stopping services...", style="yellow")
            else:
                click.echo(f"\n🛑 Stopping services...")
            
            process_manager.cleanup_all()
            
            if console and RICH_AVAILABLE:
                console.print("👋 Exiting SIEM Lite. Goodbye!", style="bold blue")
            else:
                click.echo(f"\n👋 {t('cli_exit', 'Exiting SIEM Lite. Goodbye!')}")
            break


def launch_live_dashboard():
    """Launch the live monitoring dashboard."""
    if RICH_AVAILABLE and console:
        console.clear()
        print_banner()
        console.print("📱 Starting Live Dashboard...", style="bold cyan")
        console.print("Press Ctrl+C or Esc to return to main menu", style="yellow")
        
        with Live(console=console, refresh_per_second=2) as live:
            try:
                while True:
                    table = create_status_table()
                    live.update(table)
                    time.sleep(0.5)
            except KeyboardInterrupt:
                console.print("\n👋 Returning to main menu", style="yellow")
    else:
        # Fallback dashboard without Rich
        try:
            while True:
                click.clear()
                click.echo("🛡️ SIEM Lite Live Dashboard")
                click.echo("="*50)
                
                monitor = ServiceMonitor()
                
                # API Server status
                api_status = monitor.check_api_server()
                click.echo(f"🌐 API Server: {api_status['status']}")
                
                # Database status
                db_status = monitor.check_database()
                click.echo(f"🗄️ Database: {db_status['status']}")
                
                # System stats
                sys_stats = monitor.get_system_stats()
                click.echo(f"💻 CPU: {sys_stats['cpu_percent']:.1f}%")
                click.echo(f"🧠 Memory: {sys_stats['memory_percent']:.1f}%")
                click.echo(f"💾 Disk: {sys_stats['disk_percent']:.1f}%")
                
                click.echo("\nPress Ctrl+C to return to main menu")
                time.sleep(2)
                
        except KeyboardInterrupt:
            click.echo("\n👋 Returning to main menu")


def show_detailed_status():
    """Show detailed system status."""
    if RICH_AVAILABLE and console:
        table = create_status_table()
        console.print(table)
        
        # Additional details
        try:
            db = next(get_db())
            try:
                service = AlertService(SQLAlchemyAlertRepository(db))
                alerts = service.list_alerts()
                alert_count = len(alerts)
                
                from datetime import datetime, timedelta
                yesterday = datetime.now() - timedelta(days=1)
                recent_count = len([a for a in alerts if a.timestamp >= yesterday])
                
                details_panel = Panel(
                    f"📊 Total Alerts: {alert_count}\n"
                    f"🕒 Recent Alerts (24h): {recent_count}\n"
                    f"📁 Log Files: {len(list(Path('data').glob('*.log')))}\n"
                    f"📄 Reports: {len(list(Path('reports').glob('*.pdf')))}",
                    title="Database Statistics",
                    border_style="blue"
                )
                console.print(details_panel)
            finally:
                db.close()
        except Exception as e:
            console.print(f"❌ Error getting database stats: {e}", style="red")
    else:
        click.echo("\n📈 System Status")
        click.echo("=" * 50)
        
        monitor = ServiceMonitor()
        
        # API Server status
        api_status = monitor.check_api_server()
        click.echo(f"🌐 API Server: {api_status['status']}")
        
        # Database status
        db_status = monitor.check_database()
        click.echo(f"🗄️ Database: {db_status['status']}")
        
        # System stats
        sys_stats = monitor.get_system_stats()
        click.echo(f"💻 CPU Usage: {sys_stats['cpu_percent']:.1f}%")
        click.echo(f"🧠 Memory Usage: {sys_stats['memory_percent']:.1f}%")
        click.echo(f"💾 Disk Usage: {sys_stats['disk_percent']:.1f}%")


def stop_services():
    """Stop all SIEM Lite services."""
    if console and RICH_AVAILABLE:
        console.print("🛑 Stopping SIEM Lite services...", style="yellow")
    else:
        click.echo("🛑 Stopping SIEM Lite services...")
    
    stopped_count = process_manager.cleanup_all()
    
    if console and RICH_AVAILABLE:
        console.print(f"✅ Stopped {stopped_count} processes", style="green")
    else:
        click.echo(f"✅ Stopped {stopped_count} processes")
    
    time.sleep(2)


def change_language_interactive():
    """Interactive language change."""
    try:
        from siem_lite.utils.config import AVAILABLE_LANGUAGES
        
        new_lang = questionary.select(
            t("change_language", "Select language:"),
            choices=[
                questionary.Choice(i18n.get_language_name(l), l)
                for l in AVAILABLE_LANGUAGES
            ],
            instruction="(Press Esc to return to main menu)"
        ).ask()
        
        if new_lang is None:  # User pressed Esc
            return
            
        if new_lang:
            set_global_language(new_lang)
            if console and RICH_AVAILABLE:
                console.print(f"🌐 Language changed to {i18n.get_language_name(new_lang)}", style="green")
            else:
                click.echo(f"🌐 {t('change_language', 'Language changed to')} {i18n.get_language_name(new_lang)}.")
            time.sleep(1)
    except (KeyboardInterrupt, EOFError):
        return  # Return to main menu


def interactive_generate():
    """Interactive log generation."""
    try:
        count = questionary.text(
            "How many log entries to generate?", 
            default="100",
            instruction="(Press Esc to return to main menu)"
        ).ask()
        
        if count is None:  # User pressed Esc
            return
            
        output = questionary.text(
            "Output file path:", 
            default="data/simulated.log",
            instruction="(Press Esc to return to main menu)"
        ).ask()
        
        if output is None:  # User pressed Esc
            return
        
        if count and output:
            try:
                generate_sample_logs(count=int(count), output_file=output)
                if console and RICH_AVAILABLE:
                    console.print(f"✅ Generated {count} log entries in {output}", style="green")
                else:
                    click.echo(f"✅ Generated {count} log entries in {output}")
            except Exception as e:
                if console and RICH_AVAILABLE:
                    console.print(f"❌ Error generating logs: {e}", style="red")
                else:
                    click.echo(f"❌ Error generating logs: {e}")
            time.sleep(2)
    except (KeyboardInterrupt, EOFError):
        return  # Return to main menu


def interactive_process():
    """Interactive log processing."""
    try:
        input_file = questionary.text(
            "Input log file path:", 
            default="data/simulated.log",
            instruction="(Press Esc to return to main menu)"
        ).ask()
        
        if input_file is None:  # User pressed Esc
            return
        
        if input_file:
            try:
                logs = []
                with open(input_file, "r") as f:
                    import json
                    try:
                        logs = json.load(f)
                    except Exception:
                        f.seek(0)
                        logs = [parse_log_line(line) for line in f if line.strip()]
                
                processor = LogProcessor()
                results = processor.process_logs(logs)
                
                if console and RICH_AVAILABLE:
                    console.print(f"✅ Log processing completed. Results: {results}", style="green")
                else:
                    click.echo(f"✅ Log processing completed. Results: {results}")
            except Exception as e:
                if console and RICH_AVAILABLE:
                    console.print(f"❌ Error processing logs: {e}", style="red")
                else:
                    click.echo(f"❌ Error processing logs: {e}")
            time.sleep(2)
    except (KeyboardInterrupt, EOFError):
        return  # Return to main menu


def interactive_export():
    """Interactive data export."""
    try:
        format_choice = questionary.select(
            "Export format:", 
            choices=["json", "csv"],
            instruction="(Press Esc to return to main menu)"
        ).ask()
        
        if format_choice is None:  # User pressed Esc
            return
            
        output = questionary.text(
            "Output file name (leave empty for auto-generated):",
            instruction="(Press Esc to return to main menu)"
        ).ask()
        
        if output is None:  # User pressed Esc
            return
        
        if format_choice:
            try:
                db = next(get_db())
                try:
                    service = AlertService(SQLAlchemyAlertRepository(db))
                    alerts = service.list_alerts()
                    import csv
                    import json
                    from datetime import datetime

                    if not output:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output = f"analysis_export_{timestamp}.{format_choice}"
                    
                    if format_choice == "json":
                        data = {
                            "exported_at": datetime.now().isoformat(),
                            "total_alerts": len(alerts),
                            "alerts": [a.__dict__ for a in alerts],
                        }
                        with open(output, "w") as f:
                            json.dump(data, f, indent=2, default=str)
                    elif format_choice == "csv":
                        with open(output, "w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(["ID", "Alert Type", "Source IP", "Details", "Timestamp"])
                            for a in alerts:
                                writer.writerow([a.id, a.alert_type, a.source_ip, a.details, a.timestamp])
                    
                    if console and RICH_AVAILABLE:
                        console.print(f"✅ Data exported to {output}", style="green")
                    else:
                        click.echo(f"✅ Data exported to {output}")
                finally:
                    db.close()
            except Exception as e:
                if console and RICH_AVAILABLE:
                    console.print(f"❌ Error exporting data: {e}", style="red")
                else:
                    click.echo(f"❌ Error exporting data: {e}")
            time.sleep(2)
    except (KeyboardInterrupt, EOFError):
        return  # Return to main menu


# --- Command Functions ---
def setup_cmd():
    """Setup the SIEM Lite environment."""
    if console and RICH_AVAILABLE:
        console.print("🔧 Setting up SIEM Lite environment...", style="cyan")
        console.print("🗄️ Initializing database...", style="cyan")
    else:
        click.echo("🔧 Setting up SIEM Lite environment...")
        click.echo("🗄️ Initializing database...")
    
    try:
        init_database()
        if console and RICH_AVAILABLE:
            console.print("📝 Generating sample logs...", style="cyan")
        else:
            click.echo("📝 Generating sample logs...")
        
        generate_sample_logs()
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("reports/plots", exist_ok=True)
        
        if console and RICH_AVAILABLE:
            console.print("✅ Setup completed successfully!", style="green")
        else:
            click.echo("✅ Setup completed successfully!")
    except Exception as e:
        if console and RICH_AVAILABLE:
            console.print(f"❌ Error during setup: {e}", style="red")
        else:
            click.echo(f"❌ Error during setup: {e}")
    
    input("\nPress Enter to continue...")


def monitor_cmd(interval: int = 5):
    """Start real-time monitoring."""
    if console and RICH_AVAILABLE:
        console.print(f"🔍 Starting real-time monitoring (interval: {interval} minutes)...", style="cyan")
        console.print("Press Ctrl+C to stop", style="yellow")
    else:
        click.echo(f"🔍 Starting real-time monitoring (interval: {interval} minutes)...")
        click.echo("Press Ctrl+C to stop")
    
    try:
        db = next(get_db())
        try:
            service = AlertService(SQLAlchemyAlertRepository(db))
            from datetime import datetime, timedelta
            
            while True:
                recent_time = datetime.now() - timedelta(minutes=interval)
                recent_count = len([a for a in service.list_alerts() if a.timestamp >= recent_time])
                
                if recent_count > 0:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    if console and RICH_AVAILABLE:
                        console.print(f'🚨 {recent_count} new alerts detected at {timestamp}', style="red")
                    else:
                        print(f'🚨 {recent_count} new alerts detected at {timestamp}')
                
                time.sleep(interval * 60)
        finally:
            db.close()
    except KeyboardInterrupt:
        if console and RICH_AVAILABLE:
            console.print("\n👋 Monitoring stopped", style="yellow")
        else:
            click.echo("\n👋 Monitoring stopped")
    except Exception as e:
        if console and RICH_AVAILABLE:
            console.print(f"❌ Error in monitoring: {e}", style="red")
        else:
            click.echo(f"❌ Error in monitoring: {e}")


def analyze_threats_cmd():
    """Analyze threat patterns and statistics."""
    if console and RICH_AVAILABLE:
        console.print("🛡️ Analyzing threat patterns...", style="cyan")
    else:
        click.echo("🛡️ Analyzing threat patterns...")
    
    try:
        db = next(get_db())
        try:
            service = AlertService(SQLAlchemyAlertRepository(db))
            alerts = service.list_alerts()
            from collections import Counter
            from datetime import datetime, timedelta

            total_alerts = len(alerts)
            top_sources = Counter(a.source_ip for a in alerts).most_common(10)
            alert_types = Counter(a.alert_type for a in alerts).items()
            yesterday = datetime.now() - timedelta(days=1)
            recent_alerts = [a for a in alerts if a.timestamp >= yesterday]
            
            if console and RICH_AVAILABLE:
                # Create analysis table
                analysis_table = Table(title="🛡️ Threat Analysis")
                analysis_table.add_column("Metric", style="cyan")
                analysis_table.add_column("Value", style="magenta")
                
                analysis_table.add_row("📊 Total Alerts", str(total_alerts))
                analysis_table.add_row("🕒 Recent Alerts (24h)", str(len(recent_alerts)))
                
                console.print(analysis_table)
                
                # Top sources table
                if top_sources:
                    sources_table = Table(title="🎯 Top Attack Sources")
                    sources_table.add_column("IP Address", style="red")
                    sources_table.add_column("Attack Count", style="yellow")
                    
                    for ip, count in top_sources:
                        sources_table.add_row(ip, str(count))
                    
                    console.print(sources_table)
                
                # Alert types table
                if alert_types:
                    types_table = Table(title="📈 Alert Type Distribution")
                    types_table.add_column("Alert Type", style="blue")
                    types_table.add_column("Count", style="green")
                    
                    for alert_type, count in alert_types:
                        types_table.add_row(alert_type, str(count))
                    
                    console.print(types_table)
            else:
                click.echo(f"📊 Total Alerts: {total_alerts}")
                click.echo(f"🕒 Recent Alerts (24h): {len(recent_alerts)}")
                click.echo("\n🎯 Top Attack Sources:")
                for ip, count in top_sources:
                    click.echo(f"  {ip}: {count} attacks")
                click.echo("\n📈 Alert Type Distribution:")
                for alert_type, count in alert_types:
                    click.echo(f"  {alert_type}: {count}")
        finally:
            db.close()
    except Exception as e:
        if console and RICH_AVAILABLE:
            console.print(f"❌ Error analyzing threats: {e}", style="red")
        else:
            click.echo(f"❌ Error analyzing threats: {e}")
    
    input("\nPress Enter to continue...")


# Legacy function aliases for compatibility
def setup():
    setup_cmd()

def dashboard():
    launch_live_dashboard()

def monitor():
    monitor_cmd()

def generate():
    interactive_generate()

def process():
    interactive_process()

def analyze_threats():
    analyze_threats_cmd()

def export():
    interactive_export()

def status():
    show_detailed_status()


# --- Main CLI entrypoint ---
@click.group(invoke_without_command=True)
@click.version_option(version="1.0.0")
@click.option("--language", "-l", default="en", help="Language for output (en/es)")
def cli(language: str) -> None:
    """
    SIEM Lite - Security Information and Event Management System
    """
    i18n.set_language(language)
    click.clear()
    click.echo(ASCII_BANNER)
    click.echo(f"🔒 SIEM Lite CLI - Language: {language.upper()}")
    # --- Environment setup ---
    click.echo("\n🔧 Initializing environment...")
    try:
        init_database()
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("reports/plots", exist_ok=True)
        click.echo("✅ Database and folders ready.")
    except Exception as e:
        click.echo(f"❌ Error initializing environment: {e}")
        sys.exit(1)
    # --- Show menu ---
    try:
        show_interactive_menu()
    finally:
        pass


# --- CLI Commands ---


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind the API server")
@click.option("--port", default=8000, help="Port to bind the API server")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--monitor", is_flag=True, help="Start with live monitoring dashboard")
def run(host: str, port: int, reload: bool, monitor: bool):
    """🚀 Start the complete SIEM Lite system (database + API server)."""
    print_banner()
    
    if console:
        console.print("🚀 Starting SIEM Lite System...", style="bold blue")
    else:
        print("🚀 Starting SIEM Lite System...")
    
    # 1. Initialize database
    if console:
        console.print("1️⃣ Initializing database...", style="cyan")
    else:
        print("1️⃣ Initializing database...")
    
    try:
        init_database()
        if console:
            console.print("✅ Database initialized successfully!", style="green")
        else:
            print("✅ Database initialized successfully!")
    except Exception as e:
        if console:
            console.print(f"❌ Database initialization failed: {e}", style="red")
        else:
            print(f"❌ Database initialization failed: {e}")
        return
    
    # 2. Start API server
    if console:
        console.print("2️⃣ Starting API server...", style="cyan")
    else:
        print("2️⃣ Starting API server...")
    
    api_process = start_api_server(host=host, port=port, reload=reload)
    
    # 3. Wait for server to be ready
    health_url = f"http://{host}:{port}/api/health"
    if wait_for_service(health_url, timeout=30):
        if console:
            console.print("✅ API server started successfully!", style="green")
            console.print(f"\n🌐 API is available at: http://{host}:{port}", style="bold green")
            console.print(f"📚 Documentation: http://{host}:{port}/docs", style="blue")
        else:
            print("✅ API server started successfully!")
            print(f"\n🌐 API is available at: http://{host}:{port}")
            print(f"📚 Documentation: http://{host}:{port}/docs")
    else:
        if console:
            console.print("❌ Failed to start API server", style="red")
        else:
            print("❌ Failed to start API server")
        return
    
    # 4. Start monitoring if requested
    if monitor:
        if console:
            console.print("\n3️⃣ Starting live monitoring dashboard...", style="cyan")
        else:
            print("\n3️⃣ Starting live monitoring dashboard...")
        dashboard()
    else:
        if console:
            console.print("\n💡 Use 'siem-lite status' to check system status", style="yellow")
            console.print("💡 Use 'siem-lite dashboard' for live monitoring", style="yellow")
            console.print("💡 Press Ctrl+C to stop all services", style="yellow")
        else:
            print("\n💡 Use 'siem-lite status' to check system status")
            print("💡 Use 'siem-lite dashboard' for live monitoring")
            print("💡 Press Ctrl+C to stop all services")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            if console:
                console.print("\n🛑 Stopping SIEM Lite System...", style="yellow")
            else:
                print("\n🛑 Stopping SIEM Lite System...")


@cli.command()
def dashboard_cmd():
    """📱 Launch the interactive monitoring dashboard."""
    dashboard()


def dashboard():
    """Interactive dashboard for monitoring the SIEM Lite system."""
    if console:
        console.clear()
    print_banner()
    
    if not is_api_running():
        if console:
            console.print("⚠️ API server is not running. Starting...", style="yellow")
        else:
            print("⚠️ API server is not running. Starting...")
        
        api_process = start_api_server()
        
        # Wait for server to be ready
        health_url = f"http://127.0.0.1:8000/api/health"
        if wait_for_service(health_url, timeout=30):
            if console:
                console.print("✅ API server started successfully!", style="green")
            else:
                print("✅ API server started successfully!")
        else:
            if console:
                console.print("❌ Failed to start API server", style="red")
            else:
                print("❌ Failed to start API server")
            return
    
    if RICH_AVAILABLE and console:
        # Rich live dashboard
        with Live(console=console, refresh_per_second=1) as live:
            try:
                while True:
                    table = create_status_table()
                    live.update(table)
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n👋 Dashboard stopped", style="yellow")
    else:
        # Fallback dashboard without Rich
        try:
            while True:
                print("\n" + "="*50)
                print("🛡️ SIEM Lite System Status")
                print("="*50)
                
                monitor = ServiceMonitor()
                
                # API Server status
                api_status = monitor.check_api_server()
                print(f"🌐 API Server: {api_status['status']}")
                
                # Database status
                db_status = monitor.check_database()
                print(f"🗄️ Database: {db_status['status']}")
                
                # System stats
                sys_stats = monitor.get_system_stats()
                print(f"💻 CPU: {sys_stats['cpu_percent']:.1f}%")
                print(f"🧠 Memory: {sys_stats['memory_percent']:.1f}%")
                print(f"💾 Disk: {sys_stats['disk_percent']:.1f}%")
                
                print("\nPress Ctrl+C to exit")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped")


@cli.command()
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def status(output_format: str):
    """📊 Check the status of SIEM Lite services."""
    if output_format == "json":
        monitor = ServiceMonitor()
        api_status = monitor.check_api_server()
        db_status = monitor.check_database()
        sys_stats = monitor.get_system_stats()
        
        status_data = {
            "api_server": api_status,
            "database": db_status,
            "system": sys_stats,
            "timestamp": time.time()
        }
        
        import json
        print(json.dumps(status_data, indent=2))
    else:
        if RICH_AVAILABLE and console:
            table = create_status_table()
            console.print(table)
        else:
            print("\n🛡️ SIEM Lite System Status")
            print("="*30)
            
            monitor = ServiceMonitor()
            
            # API Server status
            api_status = monitor.check_api_server()
            print(f"🌐 API Server: {api_status['status']}")
            if api_status.get('uptime'):
                print(f"   Uptime: {api_status['uptime']}")
            
            # Database status
            db_status = monitor.check_database()
            print(f"🗄️ Database: {db_status['status']}")
            if db_status.get('error'):
                print(f"   Error: {db_status['error']}")
            
            # System stats
            sys_stats = monitor.get_system_stats()
            print(f"💻 CPU Usage: {sys_stats['cpu_percent']:.1f}%")
            print(f"🧠 Memory Usage: {sys_stats['memory_percent']:.1f}%")
            print(f"💾 Disk Usage: {sys_stats['disk_percent']:.1f}%")


@cli.command()
def stop():
    """🛑 Stop all SIEM Lite services."""
    if console:
        console.print("🛑 Stopping SIEM Lite services...", style="yellow")
    else:
        print("🛑 Stopping SIEM Lite services...")
    
    stopped_count = process_manager.cleanup_all()
    
    if console:
        console.print(f"✅ Stopped {stopped_count} processes", style="green")
    else:
        print(f"✅ Stopped {stopped_count} processes")


@cli.command()
@click.option("--format", "output_format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def processes(output_format: str):
    """📋 List running SIEM Lite processes."""
    active_processes = process_manager.get_active_processes()
    
    if not active_processes:
        if console:
            console.print("No SIEM Lite processes running", style="yellow")
        else:
            print("No SIEM Lite processes running")
        return
    
    if output_format == "json":
        import json
        process_data = []
        for proc in active_processes:
            try:
                process_data.append({
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "create_time": proc.create_time()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(json.dumps(process_data, indent=2))
    else:
        if RICH_AVAILABLE and console:
            table = Table(title="🔄 Active SIEM Lite Processes")
            table.add_column("PID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("CPU %", style="yellow")
            table.add_column("Memory %", style="blue")
            
            for proc in active_processes:
                try:
                    table.add_row(
                        str(proc.pid),
                        proc.name(),
                        proc.status(),
                        f"{proc.cpu_percent():.1f}",
                        f"{proc.memory_percent():.1f}"
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            console.print(table)
        else:
            print("\n🔄 Active SIEM Lite Processes")
            print("="*40)
            print(f"{'PID':<8} {'Name':<20} {'Status':<10} {'CPU%':<8} {'Memory%'}")
            print("-" * 60)
            
            for proc in active_processes:
                try:
                    print(f"{proc.pid:<8} {proc.name():<20} {proc.status():<10} "
                          f"{proc.cpu_percent():<8.1f} {proc.memory_percent():.1f}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host for the API server.")
@click.option("--port", default=8000, help="Port for the API server.")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development.")
def api(host, port, reload):
    """
    Start the FastAPI API server using uvicorn.
    """
    import uvicorn

    # Always use the absolute import path for the app
    click.echo(f"🚀 Starting API server on http://{host}:{port}")
    uvicorn.run(
        "siem_lite.main:app", host=host, port=port, reload=reload, factory=False
    )


@cli.command()
def setup():
    """Setup the SIEM Lite environment."""
    click.echo("🔧 Setting up SIEM Lite environment...")
    try:
        click.echo("🗄️ Initializing database...")
        init_database()
        click.echo("📝 Generating sample logs...")
        generate_sample_logs()
        os.makedirs("data", exist_ok=True)
        os.makedirs("reports", exist_ok=True)
        os.makedirs("reports/plots", exist_ok=True)
        click.echo("✅ Setup completed successfully!")
    except Exception as e:
        click.echo(f"❌ Error during setup: {e}")
        sys.exit(1)


@cli.command()
def dashboard():
    """Launch the advanced CLI dashboard."""
    click.echo("📊 Launching SIEM Lite Dashboard...")
    try:
        from siem_lite.cli_dashboard import SIEMDashboard

        dashboard = SIEMDashboard()
        dashboard.run()
    except Exception as e:
        click.echo(f"❌ Error launching dashboard: {e}")
        click.echo("Returning to main menu in 3 seconds...")
        time.sleep(3)
        # Do not exit, just return to menu


@cli.command()
@click.option("--interval", default=5, help="Monitoring interval in minutes")
def monitor(interval: int = 5):
    """Start real-time monitoring."""
    click.echo(f"🔍 Starting real-time monitoring (interval: {interval} minutes)...")
    click.echo("Press Ctrl+C to stop")
    try:
        db = next(get_db())
        try:
            service = AlertService(SQLAlchemyAlertRepository(db))
            import time
            from datetime import datetime, timedelta

            while True:
                recent_time = datetime.now() - timedelta(minutes=interval)
                recent_count = len(
                    [a for a in service.list_alerts() if a.timestamp >= recent_time]
                )
                if recent_count > 0:
                    print(
                        f'🚨 {recent_count} new alerts detected at {datetime.now().strftime("%H:%M:%S")}'
                    )
                time.sleep(interval * 60)
        finally:
            db.close()
    except Exception as e:
        click.echo(f"❌ Error in monitoring: {e}")
        sys.exit(1)


@cli.command()
@click.option("--count", default=100, help="Number of log entries to generate")
@click.option("--output", "-o", default="data/simulated.log", help="Output log file")
def generate(count: int = 100, output: str = "data/simulated.log"):
    """Generate simulated security logs."""
    click.echo(f"📝 Generating {count} log entries...")
    try:
        generate_sample_logs(count=count, output_file=output)
        click.echo(f"✅ Generated {count} log entries in {output}")
    except Exception as e:
        click.echo(f"❌ Error generating logs: {e}")
        sys.exit(1)


@cli.command()
@click.option("--input", "-i", default="data/simulated.log", help="Input log file")
def process(input: str = "data/simulated.log"):
    """Process logs and generate alerts."""
    click.echo(f"⚙️ Processing logs from {input}...")
    try:
        logs = []
        with open(input, "r") as f:
            import json

            try:
                logs = json.load(f)
            except Exception:
                f.seek(0)
                logs = [parse_log_line(line) for line in f if line.strip()]
        processor = LogProcessor()
        results = processor.process_logs(logs)
        click.echo(f"✅ Log processing completed. Results: {results}")
    except Exception as e:
        click.echo(f"❌ Error processing logs: {e}")
        sys.exit(1)


@cli.command()
def analyze_threats():
    """Analyze threat patterns and statistics."""
    click.echo("🛡️ Analyzing threat patterns...")
    try:
        db = next(get_db())
        try:
            service = AlertService(SQLAlchemyAlertRepository(db))
            alerts = service.list_alerts()
            from collections import Counter

            total_alerts = len(alerts)
            top_sources = Counter(a.source_ip for a in alerts).most_common(10)
            alert_types = Counter(a.alert_type for a in alerts).items()
            from datetime import datetime, timedelta

            yesterday = datetime.now() - timedelta(days=1)
            recent_alerts = [a for a in alerts if a.timestamp >= yesterday]
            click.echo(f"📊 Total Alerts: {total_alerts}")
            click.echo(f"🕒 Recent Alerts (24h): {len(recent_alerts)}")
            click.echo("\n🎯 Top Attack Sources:")
            for ip, count in top_sources:
                click.echo(f"  {ip}: {count} attacks")
            click.echo("\n📈 Alert Type Distribution:")
            for alert_type, count in alert_types:
                click.echo(f"  {alert_type}: {count}")
        finally:
            db.close()
    except Exception as e:
        click.echo(f"❌ Error analyzing threats: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--format",
    "export_format",
    default="json",
    type=click.Choice(["json", "csv"]),
    help="Export format",
)
@click.option("--output", "-o", help="Output file name")
def export(export_format: str = "json", output: str = None):
    """Export data in specified format."""
    click.echo(f"📤 Exporting data in {export_format} format...")
    try:
        db = next(get_db())
        try:
            service = AlertService(SQLAlchemyAlertRepository(db))
            alerts = service.list_alerts()
            import csv
            import json
            from datetime import datetime

            if not output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = f"analysis_export_{timestamp}.{export_format}"
            if export_format == "json":
                data = {
                    "exported_at": datetime.now().isoformat(),
                    "total_alerts": len(alerts),
                    "alerts": [a.__dict__ for a in alerts],
                }
                with open(output, "w") as f:
                    json.dump(data, f, indent=2, default=str)
            elif export_format == "csv":
                with open(output, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ["ID", "Alert Type", "Source IP", "Details", "Timestamp"]
                    )
                    for a in alerts:
                        writer.writerow(
                            [a.id, a.alert_type, a.source_ip, a.details, a.timestamp]
                        )
            click.echo(f"✅ Data exported to {output}")
        finally:
            db.close()
    except Exception as e:
        click.echo(f"❌ Error exporting data: {e}")
        sys.exit(1)


@cli.command()
@click.option("--type", "attack_type", type=click.Choice(["brute-force", "sql-injection", "ddos", "mixed", "continuous"]), default="mixed", help="Type of attack to simulate")
@click.option("--count", default=50, help="Number of attack events to generate")
@click.option("--duration", default=0, help="Duration in seconds for continuous attacks (0 = single burst)")
@click.option("--output", "-o", default="data/attack_simulation.log", help="Output file for attack logs")
def simulate_attacks(attack_type: str, count: int, duration: int, output: str):
    """🚨 Simulate various types of cyber attacks for testing."""
    click.echo(f"🚨 Starting {attack_type} attack simulation...")
    
    try:
        from siem_lite.infrastructure.attack_simulator import AttackSimulator
        
        simulator = AttackSimulator()
        
        if duration > 0:
            click.echo(f"⏱️ Running continuous simulation for {duration} seconds...")
            simulator.run_continuous_simulation(attack_type, duration, output)
        else:
            click.echo(f"💥 Generating {count} {attack_type} attack events...")
            simulator.generate_attack_events(attack_type, count, output)
        
        click.echo(f"✅ Attack simulation completed. Events saved to {output}")
        click.echo("💡 Run 'siem-lite process' to generate alerts from these events")
        
    except Exception as e:
        click.echo(f"❌ Error during attack simulation: {e}")
        sys.exit(1)


@cli.command()
@click.option("--scenario", type=click.Choice(["brute-force", "data-exfiltration", "insider-threat", "all"]), default="all", help="Response scenario to test")
def test_responses(scenario: str):
    """🛡️ Test automated incident response workflows."""
    click.echo(f"🛡️ Testing incident response for {scenario} scenario...")
    
    try:
        from siem_lite.infrastructure.incident_response import IncidentResponseTester
        
        tester = IncidentResponseTester()
        results = tester.test_scenario(scenario)
        
        click.echo("📊 Response Test Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            click.echo(f"  {test_name}: {status} ({result['duration']:.2f}s)")
            if result.get("details"):
                click.echo(f"    Details: {result['details']}")
        
    except Exception as e:
        click.echo(f"❌ Error testing responses: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
