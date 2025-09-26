from __future__ import annotations

from typing import Any, Dict, List, Optional

from solana_due_diligence.providers.moralis import MoralisClient


class MetricsAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        mcfg = config.get("moralis", {})
        self.enabled = bool(mcfg.get("enabled", False))
        self.client: Optional[MoralisClient] = None
        if self.enabled:
            self.client = MoralisClient(
                base_url=mcfg.get("base_url", "https://solana-gateway.moralis.io"),
                api_key=mcfg.get("api_key") or None,
            )

    @staticmethod
    def _compute_concentration(entries: List[Dict[str, Any]], decimals: int | None) -> Dict[str, Any]:
        # entries should include numeric amounts; this is a simplified computation
        amounts = []
        for e in entries:
            amt = e.get("amount") or e.get("balance") or 0
            try:
                amt = float(amt)
            except Exception:
                amt = 0.0
            amounts.append(amt)
        total = sum(amounts) or 1.0
        amounts_sorted = sorted(amounts, reverse=True)
        top10 = sum(amounts_sorted[:10]) / total
        top20 = sum(amounts_sorted[:20]) / total
        return {"top10": top10, "top20": top20}

    def analyze(self, mint: str, decimals: int | None) -> Dict[str, Any]:
        if not self.client:
            return {"moralis": None}
        holders = self.client.get_token_holders(mint, limit=100) or {}
        items = holders.get("result") or holders.get("data") or []
        concentration = self._compute_concentration(items, decimals)
        return {
            "moralis": {
                "holders_fetched": len(items),
                "concentration": concentration,
            }
        }
