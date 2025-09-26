from __future__ import annotations

from typing import Any, Dict


def evaluate_buy_signal(report_data: Dict[str, Any], thresholds: Dict[str, float] | None = None) -> Dict[str, Any]:
    thr = {
        "min_liquidity_usd": 5000.0,
        "max_top10_concentration": 0.6,
    }
    if thresholds:
        thr.update(thresholds)

    # Authorities
    security = report_data.get("security", {})
    auth = security.get("authorities", {})
    mint_revoked = bool(auth.get("mint_revoked"))
    freeze_revoked = bool(auth.get("freeze_revoked"))

    # Liquidity
    market = report_data.get("market", {})
    lp = security.get("lp", {})
    liq = lp.get("liquidity_usd") or 0

    # Concentration (optional from moralis metrics)
    moralis = report_data.get("metrics", {})
    concentration = None
    if isinstance(moralis, dict):
        m = moralis.get("moralis") or {}
        concentration = (m.get("concentration") or {}).get("top10")

    reasons = []
    passed = True

    if not mint_revoked:
        passed = False
        reasons.append("Mint authority not revoked")
    if not freeze_revoked:
        passed = False
        reasons.append("Freeze authority not revoked")
    if liq < thr["min_liquidity_usd"]:
        passed = False
        reasons.append(f"Liquidity below ${thr['min_liquidity_usd']}")
    if concentration is not None and concentration > thr["max_top10_concentration"]:
        passed = False
        reasons.append("Top-10 holder concentration too high")

    return {"passed": passed, "reasons": reasons}
