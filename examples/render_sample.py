"""Render the bundled sample schematic to SVG + DXF without calling any model.

Useful for verifying the rendering pipeline offline (no API key required).

Usage:
    python examples/render_sample.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schematics_ai.drawing import render_dxf, render_svg
from schematics_ai.schema import Schematic

HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"


def main() -> int:
    data = json.loads((HERE / "sample_schematic.json").read_text(encoding="utf-8"))
    schematic = Schematic.model_validate(data)
    svg_path = render_svg(schematic, OUTPUT_DIR / "sample.svg")
    dxf_path = render_dxf(schematic, OUTPUT_DIR / "sample.dxf")
    print(f"Rendered '{schematic.title}':")
    print(f"  SVG: {svg_path}")
    print(f"  DXF: {dxf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
