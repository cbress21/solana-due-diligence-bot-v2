from __future__ import annotations

from typing import Any, Dict, List, Optional

from solana_due_diligence.providers.github_api import GitHubClient


class GitHubAnalyzer:
    def __init__(self, config: Dict[str, Any]) -> None:
        gcfg = config.get("github", {})
        token = gcfg.get("token") or None
        self.client = GitHubClient(token=token)
        self.enabled = bool(gcfg.get("enabled", True))

    def _score_repo(self, repo: Dict[str, Any]) -> int:
        score = 0
        # Heuristics: stars, size, recent updates
        score += min(int(repo.get("stargazers_count", 0)), 200)
        score += min(int(repo.get("size", 0)) // 50, 200)
        if repo.get("updated_at"):
            score += 50
        # Language hint
        lang = (repo.get("language") or "").lower()
        if lang in ("rust", "typescript", "javascript"):
            score += 50
        return score

    def analyze(self, tokenomics: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"repos": []}
        solscan = tokenomics.get("solscan") or {}
        meta = solscan.get("meta") or {}
        terms: List[str] = []
        for k in ("symbol", "tokenSymbol", "name", "tokenName"):
            v = meta.get(k)
            if isinstance(v, str) and len(v) >= 2:
                terms.append(v)
        queries = [t for t in set(terms)]
        repos: List[Dict[str, Any]] = []
        for q in queries:
            for item in self.client.search_repos(f"{q} solana token"):
                repos.append({
                    "full_name": item.get("full_name"),
                    "html_url": item.get("html_url"),
                    "stargazers": item.get("stargazers_count"),
                    "language": item.get("language"),
                    "updated_at": item.get("updated_at"),
                    "score": self._score_repo(item),
                })
        # Deduplicate by full_name
        seen = set()
        deduped = []
        for r in sorted(repos, key=lambda x: x.get("score", 0), reverse=True):
            fn = r.get("full_name")
            if fn in seen:
                continue
            seen.add(fn)
            deduped.append(r)
        return {"repos": deduped[:5]}
