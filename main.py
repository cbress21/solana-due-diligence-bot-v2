#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from rich import print

from solana_due_diligence.config import load_config
from solana_due_diligence.market.analyzer import MarketAnalyzer
from solana_due_diligence.reporting.report import ReportBuilder
from solana_due_diligence.tokenomics.analyzer import TokenomicsAnalyzer
from solana_due_diligence.security.analyzer import SecurityAnalyzer
from solana_due_diligence.community.analyzer import CommunityAnalyzer
from solana_due_diligence.developer.analyzer import DeveloperAnalyzer
from solana_due_diligence.github.analyzer import GitHubAnalyzer
from solana_due_diligence.metrics.analyzer import MetricsAnalyzer
from solana_due_diligence.signals.engine import evaluate_buy_signal
from solana_due_diligence.notify.telegram import send_message
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


def analyze_once(config: dict, mint_or_symbol: str, symbol_for_filename: str | None = None, notify: bool = True) -> dict:
    output_dir = Path(config["report"]["output_dir"])  # type: ignore[index]
    output_dir.mkdir(parents=True, exist_ok=True)

    symbol_for_filename = symbol_for_filename or mint_or_symbol

    tokenomics = TokenomicsAnalyzer(config)
    tokenomics_result = tokenomics.analyze(mint_or_symbol)

    market = MarketAnalyzer(config)
    market_result = market.analyze(mint_or_symbol)

    security = SecurityAnalyzer(config)
    security_result = security.analyze(tokenomics_result, market_result)

    token_symbol = None
    solscan_meta = tokenomics_result.get("solscan") or {}
    meta = solscan_meta.get("meta") if isinstance(solscan_meta, dict) else {}
    if isinstance(meta, dict):
        token_symbol = meta.get("symbol") or meta.get("tokenSymbol")

    community = CommunityAnalyzer(config)
    community_result = community.analyze(mint_or_symbol, token_symbol=token_symbol)

    developer = DeveloperAnalyzer(config)
    developer_result = developer.analyze(tokenomics_result)

    github = GitHubAnalyzer(config)
    github_result = github.analyze(tokenomics_result)

    metrics = MetricsAnalyzer(config)
    # decimals for concentration normalization
    decimals = tokenomics_result.get("supply", {}).get("decimals")
    metrics_result = metrics.analyze(mint_or_symbol, decimals)

    report = ReportBuilder(config)
    report_data = {
        "input": {"token": mint_or_symbol},
        "tokenomics": tokenomics_result,
        "market": market_result,
        "security": security_result,
        "community": community_result,
        "developer": developer_result,
        "github": github_result,
        "metrics": metrics_result,
        "summary": report.summarize(tokenomics_result, market_result),
    }

    json_path = output_dir / f"{symbol_for_filename}.json"
    md_path = output_dir / f"{symbol_for_filename}.md"

    if config["report"].get("include_json", True):  # type: ignore[call-arg]
        json_path.write_text(json.dumps(report_data, indent=2))
        print(f"[green]Wrote[/green] {json_path}")

    if config["report"].get("include_markdown", True):  # type: ignore[call-arg]
        md_path.write_text(report.to_markdown(report_data))
        print(f"[green]Wrote[/green] {md_path}")

    # Optional buy-signal + Telegram
    sig = evaluate_buy_signal(report_data)
    tcfg = config.get("telegram", {})
    if not sig["passed"]:
        print(f"[yellow]Signal not passed:[/yellow] {', '.join(sig['reasons'])}")
    elif notify and tcfg.get("enabled") and tcfg.get("bot_token") and tcfg.get("chat_id"):
        text = f"Buy signal for {symbol_for_filename or mint_or_symbol}: reasons OK"
        send_message(tcfg.get("bot_token"), tcfg.get("chat_id"), text)
        print("[green]Telegram notification sent[/green]")

    return report_data


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
