"""Service configuration.

Secrets are read from environment variables only. Never hardcode them.
"""
import os


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def get_tariff_api_key() -> str:
    """API key for the external tariff API. Set TARIFF_API_KEY in the environment."""
    key = os.environ.get("TARIFF_API_KEY")
    if not key:
        raise RuntimeError("TARIFF_API_KEY is not set")
    return key
