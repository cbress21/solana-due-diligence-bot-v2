from __future__ import annotations

from typing import Any, Dict, List

from solana_due_diligence.market import dexscreener


class MarketAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def analyze(self, mint: str) -> Dict[str, Any]:
        pairs = dexscreener.fetch_pairs_for_token(self.config, mint)
        best = None
        if pairs:
            best = max(pairs, key=lambda p: (p.get("liquidity", {}).get("usd", 0) or 0))
        return {
            "pairs_found": len(pairs or []),
            "best_pair": best,
        }
