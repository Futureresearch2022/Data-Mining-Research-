"""DeepSeek model client.

DeepSeek exposes an OpenAI-compatible Chat Completions API, so we reuse the
``openai`` SDK pointed at the DeepSeek base URL. The SDK is imported lazily so
the rest of the package works without it installed.
"""

from __future__ import annotations

import os

from schematics_ai.prompts import SYSTEM_PROMPT, build_user_prompt

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekClient:
    """Thin wrapper over DeepSeek's OpenAI-compatible chat API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key not provided. Pass api_key= or set DEEPSEEK_API_KEY."
            )
        self.model = model
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:  # pragma: no cover - exercised via env without dep
                raise ImportError(
                    "The 'openai' package is required for DeepSeekClient. "
                    "Install it with: pip install 'schematics-ai[deepseek]'"
                ) from exc
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def generate_json(self, description: str) -> str:
        """Return raw schematic JSON for ``description``."""
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(description)},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
