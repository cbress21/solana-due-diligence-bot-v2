#!/usr/bin/env python3
import argparse

from solana_due_diligence.config import load_config
from solana_due_diligence.analysis import analyze_once
from solana_due_diligence.streaming.controller import StreamController


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solana Meme Coin Due Diligence")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Analyze a single token")
    run.add_argument("token", help="Token mint address or symbol")
    run.add_argument("--symbol", dest="symbol", default=None, help="Optional symbol override for report file naming")
    run.add_argument("--config", dest="config_path", default="config.yaml", help="Path to config.yaml")
    run.add_argument("--no-telegram", action="store_true", help="Do not send Telegram notifications")

    stream = sub.add_parser("stream", help="Stream new tokens (Bitquery)")
    stream.add_argument("action", choices=["start", "stop", "status"], help="Stream action")
    stream.add_argument("--config", dest="config_path", default="config.yaml", help="Path to config.yaml")

    return parser




def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # default to 'run' if no subcommand
    command = args.command or "run"

    config = load_config(getattr(args, "config_path", "config.yaml"))

    if command == "run":
        analyze_once(config, args.token, symbol_for_filename=getattr(args, "symbol", None), notify=not getattr(args, "no_telegram", False))
        return

    if command == "stream":
        controller = StreamController(args.config_path)
        action = args.action
        if action == "start":
            controller.start()
        elif action == "stop":
            controller.stop()
        elif action == "status":
            controller.status()
        return


if __name__ == "__main__":
    main()
