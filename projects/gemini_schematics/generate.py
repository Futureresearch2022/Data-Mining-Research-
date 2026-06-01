"""Example: generate a schematic with Gemini.

Usage:
    export GEMINI_API_KEY=...
    python projects/gemini_schematics/generate.py "low-pass RC filter"
"""

from __future__ import annotations

import sys
from pathlib import Path

from schematics_ai import SchematicGenerator
from schematics_ai.clients import GeminiClient

OUTPUT_DIR = Path(__file__).parent / "output"
DEFAULT_DESCRIPTION = (
    "A first-order low-pass RC filter: an AC source feeds a series resistor into a "
    "shunt capacitor, with the output taken across the capacitor."
)


def main() -> int:
    description = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DESCRIPTION
    generator = SchematicGenerator(GeminiClient())
    schematic, files = generator.generate_and_render(
        description, OUTPUT_DIR, basename="gemini_schematic"
    )
    print(f"Title: {schematic.title}")
    for fmt, path in files.items():
        print(f"  {fmt.upper()}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
