#!/usr/bin/env python3
"""
Core analysis functionality for the Solana Due Diligence Bot.
"""

import json
from pathlib import Path
from typing import Any, Dict

from rich import print

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


def analyze_once(config: Dict[str, Any], mint_or_symbol: str, symbol_for_filename: str | None = None, notify: bool = True) -> Dict[str, Any]:
    """
    Perform comprehensive due diligence analysis on a single token.
    
    Args:
        config: Configuration dictionary
        mint_or_symbol: Token mint address or symbol
        symbol_for_filename: Optional symbol override for report file naming
        notify: Whether to send Telegram notifications
        
    Returns:
        Dictionary containing complete analysis results
    """
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
