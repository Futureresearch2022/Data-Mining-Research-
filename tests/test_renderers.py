import re

import ezdxf

from schematics_ai.drawing import render_dxf, render_svg
from schematics_ai.drawing.svg_renderer import schematic_to_svg
from schematics_ai.schema import Component, Connection, Schematic, Shape


def _sample() -> Schematic:
    return Schematic(
        title="RC filter",
        components=[
            Component(id="src", label="Source", x=0, y=0, shape=Shape.ELLIPSE),
            Component(id="r", label="R1", x=80, y=0, shape=Shape.ROUNDED),
            Component(id="c", label="C1", x=160, y=0),
        ],
        connections=[
            Connection(source="src", target="r", label="in"),
            Connection(source="r", target="c"),
        ],
        notes=["fc = 1 kHz"],
    )


def test_schematic_to_svg_contains_labels():
    svg = schematic_to_svg(_sample())
    assert svg.startswith("<?xml")
    assert "<svg" in svg
    assert "RC filter" in svg
    assert "Source" in svg
    assert "<ellipse" in svg
    assert "<line" in svg


def test_render_svg_writes_file(tmp_path):
    out = render_svg(_sample(), tmp_path / "sub" / "out.svg")
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("<?xml")


def test_svg_viewbox_covers_all_notes():
    schematic = Schematic(
        title="many notes",
        components=[Component(id="a", label="A", x=0, y=0)],
        notes=[f"note {i}" for i in range(6)],
    )
    svg = schematic_to_svg(schematic)
    viewbox = re.search(r'viewBox="([\d.\- ]+)"', svg).group(1).split()
    min_y, vb_height = float(viewbox[1]), float(viewbox[3])
    bottom = min_y + vb_height
    note_ys = [float(y) for y in re.findall(r'class="note"[^>]*y="([\d.]+)"', svg)]
    assert note_ys, "expected note elements in SVG"
    assert max(note_ys) <= bottom


def test_render_dxf_writes_readable_file(tmp_path):
    out = render_dxf(_sample(), tmp_path / "out.dxf")
    assert out.exists()
    doc = ezdxf.readfile(out)
    msp = doc.modelspace()
    entity_types = {e.dxftype() for e in msp}
    assert "LWPOLYLINE" in entity_types
    assert "ELLIPSE" in entity_types
    assert "LINE" in entity_types
    assert "TEXT" in entity_types
