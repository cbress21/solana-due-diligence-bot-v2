from __future__ import annotations

from typing import Any, Dict, List, Optional

from solana_due_diligence.providers.solscan import SolscanClient


class DeveloperAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        scfg = config.get("solscan", {})
        self.solscan_enabled: bool = bool(scfg.get("enabled", False))
        self.solscan: Optional[SolscanClient] = None
        if self.solscan_enabled:
            self.solscan = SolscanClient(
                base_url=scfg.get("base_url", "https://api.solscan.io"),
                api_key=scfg.get("api_key") or None,
            )

    def _extract_creator(self, tokenomics: Dict[str, Any]) -> Optional[str]:
        solscan = tokenomics.get("solscan") or {}
        meta = solscan.get("meta") or {}
        # Common fields observed
        for key in ("creator", "creater", "creatorAddress", "mintAuthority", "updateAuthority"):
            v = meta.get(key)
            if isinstance(v, str) and len(v) > 20:
                return v
        return None

    def analyze(self, tokenomics: Dict[str, Any]) -> Dict[str, Any]:
        if not self.solscan:
            return {"creator": None, "history": None, "risk_flags": ["solscan_disabled"]}

        creator = self._extract_creator(tokenomics)
        history: List[Dict[str, Any]] = []
        risk_flags: List[str] = []

        if creator:
            # Fetch tokens held by creator; heuristic: tokens where creator holds supply early
            tokens = self.solscan.get_account_tokens(creator, limit=50, offset=0) or {}
            items = tokens.get("data") or tokens.get("result") or []
            for it in items:
                mint = it.get("tokenAddress") or it.get("mint")
                amount = it.get("tokenAmount") or it.get("amount")
                if not mint:
                    continue
                history.append({"mint": mint, "amount": amount})

            # Basic heuristics for risk flags
            if len(history) >= 5:
                risk_flags.append("creator_has_many_tokens")
        else:
            risk_flags.append("creator_not_found_in_meta")

        return {
            "creator": creator,
            "history_sample": history[:20],
            "risk_flags": risk_flags,
        }
