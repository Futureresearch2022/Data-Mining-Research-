"""Data model describing a technical schematic.

A schematic is a block diagram: a set of labelled components positioned on a
canvas plus connections (wires/shafts/pipes) between them. Both the DeepSeek and
Gemini clients are instructed to emit JSON matching this model, which keeps the
rendering pipeline independent of the model that produced it.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class Shape(str, Enum):
    """Supported component outlines."""

    RECT = "rect"
    ROUNDED = "rounded"
    ELLIPSE = "ellipse"


class Component(BaseModel):
    """A single labelled block on the schematic canvas.

    Coordinates are in millimetres with the origin at the top-left of the
    drawing. ``x``/``y`` denote the top-left corner of the component's bounding
    box.
    """

    id: str = Field(..., description="Unique identifier referenced by connections.")
    label: str = Field(..., description="Human-readable text drawn inside the block.")
    x: float = Field(..., description="Left edge of the block, in mm.")
    y: float = Field(..., description="Top edge of the block, in mm.")
    width: float = Field(40.0, gt=0, description="Block width, in mm.")
    height: float = Field(25.0, gt=0, description="Block height, in mm.")
    shape: Shape = Field(Shape.RECT, description="Outline style of the block.")

    @property
    def center(self) -> tuple[float, float]:
        """Return the ``(x, y)`` centre of the component."""
        return (self.x + self.width / 2, self.y + self.height / 2)


class Connection(BaseModel):
    """A directed link between two components."""

    source: str = Field(..., alias="from", description="``id`` of the originating component.")
    target: str = Field(..., alias="to", description="``id`` of the destination component.")
    label: str | None = Field(None, description="Optional text drawn along the link.")

    model_config = {"populate_by_name": True}


class Schematic(BaseModel):
    """A complete schematic ready to be rendered."""

    title: str = Field(..., description="Title shown on the drawing.")
    components: list[Component] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list, description="Free-form annotations.")

    @model_validator(mode="after")
    def _validate_connection_endpoints(self) -> Schematic:
        ids = {component.id for component in self.components}
        for connection in self.connections:
            missing = {connection.source, connection.target} - ids
            if missing:
                raise ValueError(
                    f"connection references unknown component id(s): {sorted(missing)}"
                )
        return self

    def component_by_id(self, component_id: str) -> Component:
        """Return the component with ``component_id`` or raise ``KeyError``."""
        for component in self.components:
            if component.id == component_id:
                return component
        raise KeyError(component_id)

    def bounds(self, margin: float = 10.0) -> tuple[float, float, float, float]:
        """Return ``(min_x, min_y, max_x, max_y)`` padded by ``margin`` mm."""
        if not self.components:
            return (0.0, 0.0, 100.0, 100.0)
        min_x = min(component.x for component in self.components) - margin
        min_y = min(component.y for component in self.components) - margin
        max_x = max(component.x + component.width for component in self.components) + margin
        max_y = max(component.y + component.height for component in self.components) + margin
        return (min_x, min_y, max_x, max_y)
