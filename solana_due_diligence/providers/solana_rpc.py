from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class SolanaRPCError(Exception):
    pass


class SolanaRPC:
    def __init__(self, rpc_url: str, commitment: str = "confirmed", timeout_seconds: int = 20) -> None:
        self.rpc_url = rpc_url
        self.commitment = commitment
        self.timeout = timeout_seconds

    @retry(wait=wait_exponential(multiplier=0.5, min=1, max=8), stop=stop_after_attempt(3), reraise=True,
           retry=retry_if_exception_type((requests.RequestException, SolanaRPCError)))
    def _call(self, method: str, params: list[Any]) -> Any:
        payload = {"jsonrpc": "2.0", "id": int(time.time()*1000) % 1000000, "method": method, "params": params}
        r = requests.post(self.rpc_url, json=payload, timeout=self.timeout)
        if r.status_code != 200:
            raise SolanaRPCError(f"HTTP {r.status_code}: {r.text[:200]}")
        data = r.json()
        if "error" in data:
            raise SolanaRPCError(str(data["error"]))
        return data.get("result")

    def get_token_supply(self, mint: str) -> Optional[Dict[str, Any]]:
        params = [mint, {"commitment": self.commitment}]
        res = self._call("getTokenSupply", params)
        return res

    def get_mint(self, mint: str) -> Optional[Dict[str, Any]]:
        # getMint was added in recent RPCs; fallback to getAccountInfo if unavailable is omitted for simplicity
        params = [mint, {"commitment": self.commitment}]
        try:
            return self._call("getMint", params)
        except SolanaRPCError:
            return None

    def get_token_largest_accounts(self, mint: str) -> Dict[str, Any]:
        params = [mint, {"commitment": self.commitment}]
        return self._call("getTokenLargestAccounts", params)
