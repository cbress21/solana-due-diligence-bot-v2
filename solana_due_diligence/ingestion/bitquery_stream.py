from __future__ import annotations

import json
import time
from typing import Any, Dict, Generator, Optional

import requests


SUBSCRIPTION_QUERY = (
    "subscription{\n"
    "  Solana{\n"
    "    Instructions(\n"
    "      where: { programId: {is: \"pumpfun1111111111111111111111111111111111\"} }\n"
    "      limit: {count: 100} orderBy: {descending: Block_Time} \n"
    "    ){\n"
    "      Instruction{ ProgramId }\n"
    "      Transaction{ Signature Block{ Time } }\n"
    "      Accounts{ Address }\n"
    "    }\n"
    "  }\n"
    "}\n"
)


class BitqueryStream:
    def __init__(self, endpoint: str, api_key: Optional[str]) -> None:
        self.endpoint = endpoint
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        h = {"content-type": "application/json"}
        if self.api_key:
            h["X-API-KEY"] = self.api_key
        return h

    def subscribe_new_tokens(self) -> Generator[Dict[str, Any], None, None]:
        # NOTE: This is a simplified placeholder. True GraphQL WS subscriptions usually use websockets.
        # Bitquery supports HTTP streaming; if unavailable, fall back to polling.
        backoff = 1
        while True:
            try:
                resp = requests.post(self.endpoint, headers=self._headers(), json={"query": SUBSCRIPTION_QUERY}, timeout=60)
                if resp.status_code != 200:
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue
                data = resp.json()
                # Emit entries; in real-time scenarios, use websockets. Here we treat as a poll batch.
                items = (
                    data.get("data", {})
                    .get("Solana", {})
                    .get("Instructions", [])
                )
                for it in items:
                    yield it
                time.sleep(5)
                backoff = 1
            except Exception:
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
                continue
