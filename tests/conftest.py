import pytest
from pathlib import Path
import tempfile
import yaml


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "solana": {
            "rpc_url": "https://api.mainnet-beta.solana.com",
            "commitment": "confirmed",
            "timeout_seconds": 20
        },
        "solscan": {
            "enabled": True,
            "base_url": "https://api.solscan.io",
            "api_key": "test_key"
        },
        "github": {
            "enabled": True,
            "token": "test_token"
        },
        "telegram": {
            "enabled": True,
            "bot_token": "test_bot_token",
            "chat_id": "test_chat_id"
        },
        "report": {
            "output_dir": "test_reports",
            "include_json": True,
            "include_markdown": True
        }
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        return f.name


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
