"""Service configuration.

Secrets are read from environment variables only. Never hardcode them.
"""
import os


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)
