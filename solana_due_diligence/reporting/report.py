from __future__ import annotations

from typing import Any, Dict


class ReportBuilder:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def summarize(self, tokenomics: Dict[str, Any], market: Dict[str, Any]) -> Dict[str, Any]:
        supply_ui = tokenomics.get("supply", {}).get("ui_amount")
        pairs = market.get("pairs_found", 0)
        best_pair = market.get("best_pair") or {}
        price = (best_pair.get("priceUsd") or best_pair.get("price", None))
        holder_count = None
        if tokenomics.get("solscan"):
            holder_count = tokenomics["solscan"].get("holder_count")
        return {
            "headline": "Initial Solana token scan",
            "notes": [
                f"Supply (ui): {supply_ui}",
                f"Pairs found: {pairs}",
                f"Best pair priceUsd: {price}",
                f"Holder count (Solscan): {holder_count}",
            ],
        }

    def to_markdown(self, report_data: Dict[str, Any]) -> str:
        token = report_data.get("input", {}).get("token")
        tokenomics = report_data.get("tokenomics", {})
        market = report_data.get("market", {})
        security = report_data.get("security", {})
        community = report_data.get("community", {})
        developer = report_data.get("developer", {})
        github = report_data.get("github", {})
        summary = report_data.get("summary", {})

        lines = []
        lines.append(f"# Solana Meme Coin Due Diligence — {token}")
        lines.append("")
        lines.append("## Tokenomics")
        lines.append(f"- Mint: {tokenomics.get('mint')}")
        s = tokenomics.get("supply", {})
        lines.append(f"- Supply (amount): {s.get('amount')} (decimals: {s.get('decimals')})")
        lines.append(f"- Supply (ui): {s.get('ui_amount')}")
        lines.append(f"- Top holders sample: {len(tokenomics.get('top_holders_sample', []))}")
        solscan = tokenomics.get("solscan") or {}
        if solscan:
            lines.append(f"- Holder count (Solscan): {solscan.get('holder_count')}")
            meta = solscan.get("meta") or {}
            symbol = meta.get("symbol") or meta.get("tokenSymbol")
            name = meta.get("name") or meta.get("tokenName")
            if name or symbol:
                lines.append(f"- Name/Symbol: {name} / {symbol}")
        lines.append("")
        lines.append("## Market")
        lines.append(f"- Pairs found: {market.get('pairs_found')}")
        best = market.get("best_pair") or {}
        if best:
            lines.append(f"- Best pair DEX: {best.get('dexId')} — {best.get('pairAddress')}")
            lines.append(f"- Price USD: {best.get('priceUsd')}")
            liq = best.get('liquidity', {})
            lines.append(f"- Liquidity USD: {liq.get('usd')}")
            txns = best.get('txns', {})
            if isinstance(txns, dict) and 'h24' in txns:
                lines.append(f"- 24h Txns: {txns['h24'].get('buys')} buys / {txns['h24'].get('sells')} sells")
        lines.append("")
        lines.append("## Security")
        auth = security.get("authorities", {}) if isinstance(security, dict) else {}
        lines.append(f"- Mint authority: {auth.get('mint_authority')} (revoked: {auth.get('mint_revoked')})")
        lines.append(f"- Freeze authority: {auth.get('freeze_authority')} (revoked: {auth.get('freeze_revoked')})")
        lp = security.get("lp", {}) if isinstance(security, dict) else {}
        lines.append(f"- LP DEX: {lp.get('dex')}, Liquidity USD: {lp.get('liquidity_usd')}")
        lines.append("")
        lines.append("## Community")
        x = community.get("x", {}) if isinstance(community, dict) else {}
        if x:
            lines.append(f"- X query: {x.get('query')}")
            lines.append(f"- Posts: {x.get('posts')}")
            eng = x.get('engagement', {})
            lines.append(f"- Engagement — likes: {eng.get('likes')}, retweets: {eng.get('retweets')}, quotes: {eng.get('quotes')}, replies: {eng.get('replies')}")
        lines.append("")
        lines.append("## Developer")
        lines.append(f"- Creator wallet: {developer.get('creator')}")
        rf = developer.get('risk_flags', []) if isinstance(developer, dict) else []
        if rf:
            lines.append(f"- Risk flags: {', '.join(rf)}")
        hist = developer.get('history_sample', []) if isinstance(developer, dict) else []
        lines.append(f"- Creator tokens sample: {len(hist)}")
        lines.append("")
        lines.append("## GitHub")
        repos = github.get('repos', []) if isinstance(github, dict) else []
        if repos:
            for r in repos:
                lines.append(f"- {r.get('full_name')} — {r.get('language')} — ⭐ {r.get('stargazers')} — {r.get('html_url')}")
        else:
            lines.append("- No relevant repositories found")
        lines.append("")
        lines.append("## Summary")
        lines.append(f"- {summary.get('headline')}")
        for n in summary.get("notes", []):
            lines.append(f"- {n}")
        lines.append("")
        return "\n".join(lines)
