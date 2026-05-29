import json

import pytest

from schematics_ai.clients.base import extract_json
from schematics_ai.generator import SchematicGenerator

SAMPLE = {
    "title": "Test rig",
    "components": [
        {"id": "a", "label": "A", "x": 0, "y": 0},
        {"id": "b", "label": "B", "x": 80, "y": 0},
    ],
    "connections": [{"from": "a", "to": "b"}],
    "notes": [],
}


class FakeClient:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def generate_json(self, description: str) -> str:
        return self.payload


def test_generate_plain_json():
    gen = SchematicGenerator(FakeClient(json.dumps(SAMPLE)))
    schematic = gen.generate("anything")
    assert schematic.title == "Test rig"
    assert len(schematic.components) == 2


def test_generate_and_render_writes_files(tmp_path):
    gen = SchematicGenerator(FakeClient(json.dumps(SAMPLE)))
    schematic, files = gen.generate_and_render("anything", tmp_path, basename="rig")
    assert schematic.title == "Test rig"
    assert files["svg"].exists()
    assert files["dxf"].exists()


def test_extract_json_strips_markdown_fence():
    fenced = "```json\n" + json.dumps(SAMPLE) + "\n```"
    assert extract_json(fenced)["title"] == "Test rig"


def test_extract_json_handles_surrounding_prose():
    noisy = "Here is your schematic:\n" + json.dumps(SAMPLE) + "\nHope that helps!"
    assert extract_json(noisy)["title"] == "Test rig"


def test_extract_json_empty_raises():
    with pytest.raises(ValueError):
        extract_json("   ")


def test_extract_json_no_object_raises():
    with pytest.raises(ValueError):
        extract_json("no json here")
