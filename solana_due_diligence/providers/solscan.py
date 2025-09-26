from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class SolscanClient:
    def __init__(self, base_url: str, api_key: Optional[str]) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["token"] = self.api_key
        return headers

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

    def get_token_meta(self, mint: str) -> Optional[Dict[str, Any]]:
        # GET /v2/token/meta?tokenAddress=
        return self._get("/v2/token/meta", {"tokenAddress": mint})

    def get_token_holders(self, mint: str, limit: int = 20, offset: int = 0) -> Optional[Dict[str, Any]]:
        # GET /v2/token/holders?tokenAddress=&offset=&limit=
        return self._get("/v2/token/holders", {"tokenAddress": mint, "offset": offset, "limit": limit})

    def get_account_tokens(self, account: str, limit: int = 50, offset: int = 0) -> Optional[Dict[str, Any]]:
        # GET /v2/account/tokens?address=&offset=&limit=
        return self._get("/v2/account/tokens", {"address": account, "offset": offset, "limit": limit})
