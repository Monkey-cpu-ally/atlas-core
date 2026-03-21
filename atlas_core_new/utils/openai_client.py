import os
from typing import Optional

from openai import OpenAI


def get_openai_api_key() -> Optional[str]:
    """Return OpenAI API key from preferred env vars."""
    return os.getenv("AI_INTEGRATIONS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")


def get_openai_base_url() -> Optional[str]:
    """Return optional custom OpenAI-compatible base URL."""
    return os.getenv("AI_INTEGRATIONS_OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")


def create_openai_client(require_base_url: bool = False) -> Optional[OpenAI]:
    """
    Build an OpenAI client from environment variables.

    If `require_base_url` is True, returns None when no base URL is set.
    """
    api_key = get_openai_api_key()
    base_url = get_openai_base_url()
    if not api_key:
        return None
    if require_base_url and not base_url:
        return None

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)
