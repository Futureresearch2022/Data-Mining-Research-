"""Shared client interface and JSON-extraction helpers."""

from __future__ import annotations

import json
import re
from typing import Protocol, runtime_checkable

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


@runtime_checkable
class ModelClient(Protocol):
    """A client that returns raw schematic JSON text for a prompt.

    Implementations talk to a specific provider (DeepSeek, Gemini, ...). They are
    intentionally thin: the higher-level :class:`~schematics_ai.generator.
    SchematicGenerator` is responsible for parsing and validation.
    """

    def generate_json(self, description: str) -> str:
        """Return raw JSON text describing a schematic for ``description``."""
        ...


def extract_json(text: str) -> dict:
    """Best-effort parse of model output into a JSON object.

    Models occasionally wrap JSON in markdown fences or add stray text despite
    instructions, so we strip fences and fall back to slicing the outermost
    ``{...}`` block before parsing.
    """
    if not text or not text.strip():
        raise ValueError("model returned empty output")

    candidate = text.strip()

    fenced = _FENCE_RE.search(candidate)
    if fenced:
        candidate = fenced.group(1).strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = candidate[start : end + 1]
        return json.loads(snippet)

    raise ValueError("could not locate a JSON object in model output")
