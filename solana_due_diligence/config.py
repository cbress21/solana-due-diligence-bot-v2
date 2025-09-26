import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


def _expand_env(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        # format: ${ENV:-default}
        inner = value[2:-1]
        if ":-" in inner:
            env_key, default = inner.split(":-", 1)
            return os.environ.get(env_key, default)
        return os.environ.get(inner, "")
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def load_config(path: str | Path) -> Dict[str, Any]:
    load_dotenv()  # load .env if present
    with open(path, "r") as f:
        raw = yaml.safe_load(f) or {}
    return _expand_env(raw)  # type: ignore[return-value]
