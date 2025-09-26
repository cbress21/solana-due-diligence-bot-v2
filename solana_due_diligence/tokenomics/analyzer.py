from __future__ import annotations

from typing import Any, Dict, Optional

from solana_due_diligence.providers.solana_rpc import SolanaRPC, SolanaRPCError
from solana_due_diligence.providers.solscan import SolscanClient


class TokenomicsAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        s = config.get("solana", {})
        self.rpc = SolanaRPC(
            rpc_url=s.get("rpc_url"),
            commitment=s.get("commitment", "confirmed"),
            timeout_seconds=s.get("timeout_seconds", 20),
        )
        scfg = config.get("solscan", {})
        self.solscan_enabled: bool = bool(scfg.get("enabled", False))
        self.solscan: Optional[SolscanClient] = None
        if self.solscan_enabled:
            self.solscan = SolscanClient(
                base_url=scfg.get("base_url", "https://api.solscan.io"),
                api_key=scfg.get("api_key") or None,
            )

    def analyze(self, mint: str) -> Dict[str, Any]:
        mint_str = str(mint)
        supply_res = self.rpc.get_token_supply(mint_str) or {}

        # Avoid rate-limited call on public RPC when Solscan is available
        top_holders = []
        if not self.solscan_enabled:
            try:
                largest = self.rpc.get_token_largest_accounts(mint_str) or {}
                if largest and largest.get("value"):
                    for entry in largest["value"][:10]:
                        top_holders.append({
                            "address": entry.get("address"),
                            "amount": entry.get("amount"),
                            "uiAmount": entry.get("uiAmount"),
                        })
            except SolanaRPCError:
                top_holders = []

        amount = None
        decimals = None
        ui_amount = None
        if supply_res and supply_res.get("value"):
            value = supply_res["value"]
            amount = value.get("amount")
            decimals = value.get("decimals")
            ui_amount = value.get("uiAmountString") or value.get("uiAmount")

        solscan_meta: Dict[str, Any] = {}
        holder_count: Optional[int] = None
        solscan_holders_sample = []
        if self.solscan:
            meta = self.solscan.get_token_meta(mint_str) or {}
            if isinstance(meta, dict):
                solscan_meta = meta.get("data") or meta
            holders = self.solscan.get_token_holders(mint_str, limit=20, offset=0) or {}
            if isinstance(holders, dict):
                holder_count = holders.get("total") or holders.get("count")
                items = holders.get("data") or holders.get("result") or []
                for h in items[:10]:
                    solscan_holders_sample.append({
                        "owner": h.get("owner") or h.get("address"),
                        "amount": h.get("amount"),
                        "decimals": h.get("decimals"),
                        "ownerProgram": h.get("ownerProgram")
                    })

        return {
            "mint": mint_str,
            "supply": {
                "amount": amount,
                "decimals": decimals,
                "ui_amount": ui_amount,
            },
            "top_holders_sample": top_holders,
            "solscan": {
                "meta": solscan_meta,
                "holder_count": holder_count,
                "holders_sample": solscan_holders_sample,
            } if self.solscan else None,
        }
