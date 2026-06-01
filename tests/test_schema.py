import pytest
from pydantic import ValidationError

from schematics_ai.schema import Component, Connection, Schematic, Shape


def test_component_center():
    c = Component(id="a", label="A", x=10, y=20, width=40, height=20)
    assert c.center == (30, 30)


def test_connection_alias_from_to():
    conn = Connection.model_validate({"from": "a", "to": "b", "label": "x"})
    assert conn.source == "a"
    assert conn.target == "b"
    assert conn.label == "x"


def test_schematic_bounds_with_margin():
    s = Schematic(
        title="t",
        components=[Component(id="a", label="A", x=10, y=10, width=20, height=20)],
    )
    assert s.bounds(margin=5) == (5, 5, 35, 35)


def test_schematic_bounds_empty():
    s = Schematic(title="empty")
    assert s.bounds() == (0.0, 0.0, 100.0, 100.0)


def test_invalid_connection_endpoint_raises():
    with pytest.raises(ValidationError):
        Schematic(
            title="t",
            components=[Component(id="a", label="A", x=0, y=0)],
            connections=[Connection(source="a", target="missing")],
        )


def test_component_by_id():
    a = Component(id="a", label="A", x=0, y=0)
    s = Schematic(title="t", components=[a])
    assert s.component_by_id("a") is a
    with pytest.raises(KeyError):
        s.component_by_id("nope")


def test_shape_enum_default():
    c = Component(id="a", label="A", x=0, y=0)
    assert c.shape == Shape.RECT
