import pytest
from solana_due_diligence.signals.engine import evaluate_buy_signal


def test_evaluate_buy_signal_passed():
    """Test buy signal evaluation when all conditions are met"""
    report_data = {
        "security": {
            "authorities": {
                "mint_revoked": True,
                "freeze_revoked": True
            },
            "lp": {
                "liquidity_usd": 10000
            }
        },
        "metrics": {
            "moralis": {
                "concentration": {
                    "top10": 0.3
                }
            }
        }
    }
    
    result = evaluate_buy_signal(report_data)
    assert result["passed"] is True
    assert len(result["reasons"]) == 0


def test_evaluate_buy_signal_failed_mint_authority():
    """Test buy signal evaluation when mint authority is not revoked"""
    report_data = {
        "security": {
            "authorities": {
                "mint_revoked": False,
                "freeze_revoked": True
            },
            "lp": {
                "liquidity_usd": 10000
            }
        }
    }
    
    result = evaluate_buy_signal(report_data)
    assert result["passed"] is False
    assert "Mint authority not revoked" in result["reasons"]


def test_evaluate_buy_signal_failed_low_liquidity():
    """Test buy signal evaluation when liquidity is too low"""
    report_data = {
        "security": {
            "authorities": {
                "mint_revoked": True,
                "freeze_revoked": True
            },
            "lp": {
                "liquidity_usd": 1000
            }
        }
    }
    
    result = evaluate_buy_signal(report_data)
    assert result["passed"] is False
    assert "Liquidity below $5000.0" in result["reasons"]


def test_evaluate_buy_signal_custom_thresholds():
    """Test buy signal evaluation with custom thresholds"""
    report_data = {
        "security": {
            "authorities": {
                "mint_revoked": True,
                "freeze_revoked": True
            },
            "lp": {
                "liquidity_usd": 2000
            }
        }
    }
    
    custom_thresholds = {
        "min_liquidity_usd": 1000.0
    }
    
    result = evaluate_buy_signal(report_data, custom_thresholds)
    assert result["passed"] is True
