"""Render a schematic to a DXF drawing using ``ezdxf``.

DXF uses a Y-up coordinate system whereas the schema places the origin at the
top-left with Y growing downward, so Y coordinates are flipped on the way out to
keep drawings the right way up in CAD viewers. Units are millimetres.
"""

from __future__ import annotations

from pathlib import Path

import ezdxf

from schematics_ai.schema import Schematic, Shape

_LAYER_BLOCK = "COMPONENTS"
_LAYER_WIRE = "CONNECTIONS"
_LAYER_TEXT = "TEXT"
_LAYER_NOTES = "NOTES"


def build_dxf(schematic: Schematic):
    """Return an ``ezdxf`` document for ``schematic``."""
    doc = ezdxf.new(dxfversion="R2010")
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()

    doc.layers.add(_LAYER_BLOCK, color=7)
    doc.layers.add(_LAYER_WIRE, color=5)
    doc.layers.add(_LAYER_TEXT, color=7)
    doc.layers.add(_LAYER_NOTES, color=8)

    _min_x, _min_y, _max_x, max_y = schematic.bounds()

    def fy(value: float) -> float:
        """Flip Y so the drawing is upright in CAD viewers."""
        return max_y - value

    for component in schematic.components:
        cx, cy = component.center
        if component.shape == Shape.ELLIPSE:
            msp.add_ellipse(
                center=(cx, fy(cy)),
                major_axis=(component.width / 2, 0),
                ratio=component.height / component.width,
                dxfattribs={"layer": _LAYER_BLOCK},
            )
        else:
            x0, y0 = component.x, component.y
            x1, y1 = component.x + component.width, component.y + component.height
            points = [
                (x0, fy(y0)),
                (x1, fy(y0)),
                (x1, fy(y1)),
                (x0, fy(y1)),
            ]
            msp.add_lwpolyline(points, close=True, dxfattribs={"layer": _LAYER_BLOCK})

        text = msp.add_text(
            component.label,
            height=3.0,
            dxfattribs={"layer": _LAYER_TEXT},
        )
        text.set_placement((cx, fy(cy)), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    for connection in schematic.connections:
        source = schematic.component_by_id(connection.source)
        target = schematic.component_by_id(connection.target)
        x1, y1 = source.center
        x2, y2 = target.center
        msp.add_line((x1, fy(y1)), (x2, fy(y2)), dxfattribs={"layer": _LAYER_WIRE})
        if connection.label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            label = msp.add_text(
                connection.label,
                height=2.4,
                dxfattribs={"layer": _LAYER_WIRE},
            )
            label.set_placement((mx, fy(my)), align=ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)

    title = msp.add_text(
        schematic.title,
        height=5.0,
        dxfattribs={"layer": _LAYER_TEXT},
    )
    title.set_placement((_min_x, fy(_min_y)), align=ezdxf.enums.TextEntityAlignment.BOTTOM_LEFT)

    for index, note in enumerate(schematic.notes):
        note_text = msp.add_text(
            f"- {note}",
            height=2.6,
            dxfattribs={"layer": _LAYER_NOTES},
        )
        note_text.set_placement(
            (_min_x, fy(max_y + 6 + index * 5)),
            align=ezdxf.enums.TextEntityAlignment.BOTTOM_LEFT,
        )

    return doc


def render_dxf(schematic: Schematic, path: str | Path) -> Path:
    """Write ``schematic`` to ``path`` as DXF and return the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = build_dxf(schematic)
    doc.saveas(out)
    return out
