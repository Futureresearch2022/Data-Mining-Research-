"""Render a schematic to a standalone SVG document.

The SVG has no third-party dependencies -- it is assembled from plain strings so
the output is easy to inspect and diff. One user unit equals one millimetre.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from schematics_ai.schema import Schematic, Shape

_STYLE = """\
text { font-family: Helvetica, Arial, sans-serif; }
.block { fill: #f5f7fa; stroke: #1f2933; stroke-width: 0.6; }
.label { fill: #1f2933; font-size: 4px; text-anchor: middle; dominant-baseline: middle; }
.wire { stroke: #2b6cb0; stroke-width: 0.6; fill: none; }
.wire-label { fill: #2b6cb0; font-size: 3px; text-anchor: middle; }
.title { fill: #102a43; font-size: 7px; font-weight: bold; }
.note { fill: #486581; font-size: 3.4px; }
"""


def _component_svg(component) -> str:
    cx, cy = component.center
    label = escape(component.label)
    if component.shape == Shape.ELLIPSE:
        outline = (
            f'<ellipse class="block" cx="{cx:.2f}" cy="{cy:.2f}" '
            f'rx="{component.width / 2:.2f}" ry="{component.height / 2:.2f}" />'
        )
    else:
        radius = 3 if component.shape == Shape.ROUNDED else 0
        outline = (
            f'<rect class="block" x="{component.x:.2f}" y="{component.y:.2f}" '
            f'width="{component.width:.2f}" height="{component.height:.2f}" '
            f'rx="{radius}" ry="{radius}" />'
        )
    text = f'<text class="label" x="{cx:.2f}" y="{cy:.2f}">{label}</text>'
    return f"  {outline}\n  {text}"


def _connection_svg(schematic: Schematic, connection) -> str:
    source = schematic.component_by_id(connection.source)
    target = schematic.component_by_id(connection.target)
    x1, y1 = source.center
    x2, y2 = target.center
    parts = [f'  <line class="wire" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" />']
    if connection.label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        parts.append(
            f'  <text class="wire-label" x="{mx:.2f}" y="{my - 1:.2f}">'
            f"{escape(connection.label)}</text>"
        )
    return "\n".join(parts)


def schematic_to_svg(schematic: Schematic) -> str:
    """Return the SVG document for ``schematic`` as a string."""
    min_x, min_y, max_x, max_y = schematic.bounds()
    width = max_x - min_x
    height = max_y - min_y + 20  # extra room for title and notes

    body: list[str] = [
        f'<text class="title" x="{min_x + 2:.2f}" y="{min_y + 8:.2f}">'
        f"{escape(schematic.title)}</text>"
    ]
    for connection in schematic.connections:
        body.append(_connection_svg(schematic, connection))
    for component in schematic.components:
        body.append(_component_svg(component))
    for index, note in enumerate(schematic.notes):
        note_y = max_y + 6 + index * 5
        body.append(f'  <text class="note" x="{min_x + 2:.2f}" y="{note_y:.2f}">'
                    f"\u2022 {escape(note)}</text>")

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x:.2f} {min_y:.2f} {width:.2f} {height:.2f}" '
        f'width="{width:.2f}mm" height="{height:.2f}mm">\n'
        f"<style>{_STYLE}</style>\n"
        + "\n".join(body)
        + "\n</svg>\n"
    )


def render_svg(schematic: Schematic, path: str | Path) -> Path:
    """Write ``schematic`` to ``path`` as SVG and return the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(schematic_to_svg(schematic), encoding="utf-8")
    return out
