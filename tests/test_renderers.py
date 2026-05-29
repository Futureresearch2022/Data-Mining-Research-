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
