"""Example: generate a schematic with DeepSeek.

Usage:
    export DEEPSEEK_API_KEY=sk-...
    python projects/deepseek_schematics/generate.py "single-stage gear reducer"
"""

from __future__ import annotations

import sys
from pathlib import Path

from schematics_ai import SchematicGenerator
from schematics_ai.clients import DeepSeekClient

OUTPUT_DIR = Path(__file__).parent / "output"
DEFAULT_DESCRIPTION = (
    "A single-stage gear reducer: an electric motor drives an input shaft into a "
    "gearbox containing a pinion and gear, with an output shaft to a coupling."
)


def main() -> int:
    description = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DESCRIPTION
    generator = SchematicGenerator(DeepSeekClient())
    schematic, files = generator.generate_and_render(
        description, OUTPUT_DIR, basename="deepseek_schematic"
    )
    print(f"Title: {schematic.title}")
    for fmt, path in files.items():
        print(f"  {fmt.upper()}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
