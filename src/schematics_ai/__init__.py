"""Generate technical schematics from DeepSeek and Gemini models.

The package turns a natural-language prompt into a structured
:class:`~schematics_ai.schema.Schematic` (via an LLM client) and renders that
schematic to SVG and DXF drawing files.
"""

from schematics_ai.generator import SchematicGenerator
from schematics_ai.schema import Component, Connection, Schematic

__all__ = [
    "Component",
    "Connection",
    "Schematic",
    "SchematicGenerator",
]

__version__ = "0.1.0"
