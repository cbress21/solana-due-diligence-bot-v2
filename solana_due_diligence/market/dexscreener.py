from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@retry(wait=wait_exponential(multiplier=0.5, min=1, max=8), stop=stop_after_attempt(3), reraise=True,
       retry=retry_if_exception_type(requests.RequestException))
def fetch_pairs_for_token(config: Dict[str, Any], mint: str) -> Optional[List[Dict[str, Any]]]:
    base = config.get("market", {}).get("dexscreener_base", "https://api.dexscreener.com/latest/dex/tokens")
    url = f"{base}/{mint}"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get("pairs")
