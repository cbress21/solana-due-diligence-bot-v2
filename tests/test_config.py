import pytest
from pathlib import Path
import tempfile
import yaml
import os

from solana_due_diligence.config import load_config


def test_load_config_basic(temp_config_file):
    """Test basic config loading"""
    config = load_config(temp_config_file)
    assert config["solana"]["rpc_url"] == "https://api.mainnet-beta.solana.com"
    assert config["solscan"]["enabled"] is True


def test_load_config_with_env_vars():
    """Test config loading with environment variables"""
    # Set environment variables
    os.environ["TEST_API_KEY"] = "env_test_key"
    os.environ["TEST_BOT_TOKEN"] = "env_bot_token"
    
    config_data = {
        "solscan": {
            "api_key": "${TEST_API_KEY:-default_key}"
        },
        "telegram": {
            "bot_token": "${TEST_BOT_TOKEN:-default_token}"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_file = f.name
    
    try:
        config = load_config(config_file)
        assert config["solscan"]["api_key"] == "env_test_key"
        assert config["telegram"]["bot_token"] == "env_bot_token"
    finally:
        os.unlink(config_file)
        # Clean up environment variables
        os.environ.pop("TEST_API_KEY", None)
        os.environ.pop("TEST_BOT_TOKEN", None)
