from __future__ import annotations

import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from rich import print
from rich.console import Console

from solana_due_diligence.config import load_config
from solana_due_diligence.ingestion.bitquery_stream import BitqueryStream
from solana_due_diligence.main import analyze_once


class StreamController:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.console = Console()
        self.running = False
        self.pid_file = Path("stream.pid")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.console.print("\n[yellow]Shutting down stream controller...[/yellow]")
        self.stop()

    def start(self):
        if self.pid_file.exists():
            with open(self.pid_file, "r") as f:
                old_pid = int(f.read().strip())
            try:
                os.kill(old_pid, 0)  # Check if process exists
                self.console.print(f"[red]Stream already running with PID {old_pid}[/red]")
                return
            except OSError:
                # Process doesn't exist, remove stale PID file
                self.pid_file.unlink()

        # Write current PID
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

        self.running = True
        self.console.print("[green]Starting live token stream...[/green]")
        
        bcfg = self.config.get("bitquery", {})
        if not bcfg.get("enabled"):
            self.console.print("[yellow]Bitquery streaming disabled in config[/yellow]")
            return

        stream = BitqueryStream(
            endpoint=bcfg.get("endpoint", "https://streaming.bitquery.io/graphql"),
            api_key=bcfg.get("api_key")
        )

        try:
            for item in stream.subscribe_new_tokens():
                if not self.running:
                    break
                    
                # Extract mint from instruction data (simplified)
                accounts = item.get("Accounts", [])
                if accounts and len(accounts) > 0:
                    mint = accounts[0].get("Address")
                    if mint and len(mint) > 20:  # Basic validation
                        self.console.print(f"[blue]New token detected: {mint}[/blue]")
                        try:
                            analyze_once(self.config, mint, symbol_for_filename=mint, notify=True)
                        except Exception as e:
                            self.console.print(f"[red]Error analyzing {mint}: {e}[/red]")
                            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Stream interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Stream error: {e}[/red]")
        finally:
            self.stop()

    def stop(self):
        if not self.running:
            if self.pid_file.exists():
                self.console.print("[yellow]No active stream found[/yellow]")
            return

        self.running = False
        if self.pid_file.exists():
            self.pid_file.unlink()
        self.console.print("[green]Stream stopped[/green]")

    def status(self):
        if self.pid_file.exists():
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # Check if process exists
                self.console.print(f"[green]Stream is running (PID: {pid})[/green]")
                return True
            except OSError:
                self.pid_file.unlink()
                self.console.print("[yellow]Stream PID file exists but process not found[/yellow]")
                return False
        else:
            self.console.print("[yellow]No active stream[/yellow]")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Stream Controller")
    parser.add_argument("action", choices=["start", "stop", "status"], help="Action to perform")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    
    args = parser.parse_args()
    controller = StreamController(args.config)
    
    if args.action == "start":
        controller.start()
    elif args.action == "stop":
        controller.stop()
    elif args.action == "status":
        controller.status()


if __name__ == "__main__":
    main()
