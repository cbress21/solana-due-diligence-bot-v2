#!/usr/bin/env python3
"""
Stream Control Wrapper Script

This script provides easy management of the live token streaming system.
It wraps the StreamController with simple start/stop/status commands.
"""

import sys
from pathlib import Path

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from solana_due_diligence.streaming.controller import StreamController


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Stream Control - Manage live token streaming")
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
