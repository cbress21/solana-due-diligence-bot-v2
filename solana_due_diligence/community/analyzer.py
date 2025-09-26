from __future__ import annotations

import json
import subprocess
from typing import Any, Dict, List, Optional


class CommunityAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        s = config.get("scrape", {})
        self.enable_x = bool(s.get("enable_x", True))

    def _run_snscrape(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        cmd = [
            "snscrape",
            "--jsonl",
            f"--max-results={limit}",
            "twitter-search",
            query,
        ]
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True)
            if proc.returncode != 0:
                return []
            out = proc.stdout
        except Exception:
            return []
        items: List[Dict[str, Any]] = []
        for line in out.splitlines():
            try:
                items.append(json.loads(line))
            except Exception:
                continue
        return items

    def analyze(self, mint: str, token_symbol: Optional[str] = None) -> Dict[str, Any]:
        if not self.enable_x:
            return {"x": None}
        terms = [mint]
        if token_symbol:
            terms.append(token_symbol)
            terms.append(f"${token_symbol}")
        query = " OR ".join(terms)
        tweets = self._run_snscrape(query)
        count = len(tweets)
        likes = sum((t.get("likeCount") or 0) for t in tweets)
        retweets = sum((t.get("retweetCount") or 0) for t in tweets)
        quotes = sum((t.get("quoteCount") or 0) for t in tweets)
        replies = sum((t.get("replyCount") or 0) for t in tweets)
        return {
            "x": {
                "query": query,
                "posts": count,
                "engagement": {
                    "likes": likes,
                    "retweets": retweets,
                    "quotes": quotes,
                    "replies": replies,
                },
            }
        }
