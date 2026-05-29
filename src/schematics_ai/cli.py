"""Command-line interface for generating schematics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from schematics_ai.clients import DeepSeekClient, GeminiClient
from schematics_ai.generator import SchematicGenerator


def _build_client(provider: str, model: str | None):
    if provider == "deepseek":
        return DeepSeekClient(model=model) if model else DeepSeekClient()
    if provider == "gemini":
        return GeminiClient(model=model) if model else GeminiClient()
    raise ValueError(f"unknown provider: {provider}")


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``schematics-ai`` console script."""
    parser = argparse.ArgumentParser(
        prog="schematics-ai",
        description="Generate technical schematics (SVG + DXF) using DeepSeek or Gemini.",
    )
    parser.add_argument(
        "description",
        help="Natural-language description of the system to draw.",
    )
    parser.add_argument(
        "-p",
        "--provider",
        choices=["deepseek", "gemini"],
        default="deepseek",
        help="Model provider to use (default: deepseek).",
    )
    parser.add_argument("-m", "--model", default=None, help="Override the model name.")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Directory to write drawings into (default: ./output).",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="schematic",
        help="Base filename for the generated files (default: schematic).",
    )
    args = parser.parse_args(argv)

    try:
        client = _build_client(args.provider, args.model)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    generator = SchematicGenerator(client)
    schematic, files = generator.generate_and_render(
        args.description, Path(args.output_dir), args.name
    )

    print(f"Generated schematic: {schematic.title}")
    print(f"  components: {len(schematic.components)}  connections: {len(schematic.connections)}")
    for fmt, path in files.items():
        print(f"  {fmt.upper()}: {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
