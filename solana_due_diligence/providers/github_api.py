from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class GitHubClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.base = "https://api.github.com"
        self.token = token

    def _headers(self) -> Dict[str, str]:
        h = {"accept": "application/vnd.github+json"}
        if self.token:
            h["authorization"] = f"Bearer {self.token}"
        return h

    @retry(wait=wait_exponential(multiplier=0.5, min=1, max=8), stop=stop_after_attempt(3), reraise=True,
           retry=retry_if_exception_type(requests.RequestException))
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base}{path}"
        r = requests.get(url, headers=self._headers(), params=params or {}, timeout=20)
        if r.status_code != 200:
            return None
        try:
            return r.json()
        except Exception:
            return None

    def search_repos(self, query: str, sort: str = "stars", order: str = "desc", per_page: int = 5) -> List[Dict[str, Any]]:
        data = self._get("/search/repositories", {"q": query, "sort": sort, "order": order, "per_page": per_page}) or {}
        return data.get("items", [])

    def get_repo(self, full_name: str) -> Optional[Dict[str, Any]]:
        return self._get(f"/repos/{full_name}")
