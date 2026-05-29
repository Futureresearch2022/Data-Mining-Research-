"""High-level pipeline: prompt -> model client -> Schematic -> drawings."""

from __future__ import annotations

from pathlib import Path

from schematics_ai.clients.base import ModelClient, extract_json
from schematics_ai.drawing import render_dxf, render_svg
from schematics_ai.schema import Schematic


class SchematicGenerator:
    """Drive a :class:`ModelClient` and render its output to disk.

    The generator is provider-agnostic: pass any object implementing
    :class:`~schematics_ai.clients.base.ModelClient` (DeepSeek, Gemini, or a test
    double).
    """

    def __init__(self, client: ModelClient) -> None:
        self.client = client

    def generate(self, description: str) -> Schematic:
        """Return a validated :class:`Schematic` for ``description``."""
        raw = self.client.generate_json(description)
        data = extract_json(raw)
        return Schematic.model_validate(data)

    def render(
        self,
        schematic: Schematic,
        output_dir: str | Path,
        basename: str = "schematic",
    ) -> dict[str, Path]:
        """Write ``schematic`` to SVG + DXF and return the file paths."""
        out_dir = Path(output_dir)
        return {
            "svg": render_svg(schematic, out_dir / f"{basename}.svg"),
            "dxf": render_dxf(schematic, out_dir / f"{basename}.dxf"),
        }

    def generate_and_render(
        self,
        description: str,
        output_dir: str | Path,
        basename: str = "schematic",
    ) -> tuple[Schematic, dict[str, Path]]:
        """Generate a schematic and write SVG + DXF files.

        Returns the validated schematic and a mapping of format name to the
        written file path.
        """
        schematic = self.generate(description)
        return schematic, self.render(schematic, output_dir, basename)
