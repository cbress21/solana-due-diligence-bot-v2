from __future__ import annotations

from typing import Any, Dict, Optional  # noqa: F401


class SecurityAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def analyze(self, tokenomics: Dict[str, Any], market: Dict[str, Any]) -> Dict[str, Any]:
        solscan = tokenomics.get("solscan") or {}
        meta = solscan.get("meta") or {}

        # Authority checks from Solscan meta if present
        mint_authority = meta.get("mintAuthority") or meta.get("mint_authority")
        freeze_authority = meta.get("freezeAuthority") or meta.get("freeze_authority")
        is_mint_revoked = mint_authority in (None, "")
        is_freeze_revoked = freeze_authority in (None, "")

        # Basic LP heuristics from market best pair
        best = market.get("best_pair") or {}
        liq = best.get("liquidity", {})
        liquidity_usd = liq.get("usd")
        dex = best.get("dexId")
        pair_age = best.get("createdAt") or best.get("pairCreatedAt")

        notes = []
        if is_mint_revoked:
            notes.append("Mint authority appears revoked (null)")
        else:
            notes.append(f"Mint authority present: {mint_authority}")
        if is_freeze_revoked:
            notes.append("Freeze authority appears revoked (null)")
        else:
            notes.append(f"Freeze authority present: {freeze_authority}")
        if liquidity_usd is not None:
            notes.append(f"Liquidity USD: {liquidity_usd}")
        if dex:
            notes.append(f"Primary DEX: {dex}")

        return {
            "authorities": {
                "mint_authority": mint_authority,
                "freeze_authority": freeze_authority,
                "mint_revoked": is_mint_revoked,
                "freeze_revoked": is_freeze_revoked,
            },
            "lp": {
                "dex": dex,
                "liquidity_usd": liquidity_usd,
                "pair_created_at": pair_age,
            },
            "notes": notes,
        }
