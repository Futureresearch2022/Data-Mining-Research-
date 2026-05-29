"""Gemini model client.

Uses Google's ``google-genai`` SDK, imported lazily so the rest of the package
works without it installed.
"""

from __future__ import annotations

import os

from schematics_ai.prompts import SYSTEM_PROMPT, build_user_prompt

DEFAULT_MODEL = "gemini-1.5-flash"


class GeminiClient:
    """Thin wrapper over the Google Gemini API."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Pass api_key= or set GEMINI_API_KEY."
            )
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
            except ImportError as exc:  # pragma: no cover - exercised via env without dep
                raise ImportError(
                    "The 'google-genai' package is required for GeminiClient. "
                    "Install it with: pip install 'schematics-ai[gemini]'"
                ) from exc
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_json(self, description: str) -> str:
        """Return raw schematic JSON for ``description``."""
        client = self._get_client()
        from google.genai import types

        response = client.models.generate_content(
            model=self.model,
            contents=build_user_prompt(description),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return response.text or ""
