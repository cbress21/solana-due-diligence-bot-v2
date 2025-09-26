from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class MoralisClient:
    def __init__(self, base_url: str, api_key: Optional[str]) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        h = {"accept": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        return h

    @retry(wait=wait_exponential(multiplier=0.5, min=1, max=8), stop=stop_after_attempt(3), reraise=True,
           retry=retry_if_exception_type(requests.RequestException))
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{path}"
        r = requests.get(url, headers=self._headers(), params=params or {}, timeout=20)
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except Exception:
            return None

    # Placeholder endpoints for Solana; Moralis endpoints may differ across chains.
    def get_pair_stats(self, pair_address: str) -> Optional[Dict[str, Any]]:
        # Example placeholder path
        return self._get(f"/dex/pairs/{pair_address}/stats")

    def get_token_holders(self, mint: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        return self._get(f"/token/{mint}/holders", {"limit": limit})
