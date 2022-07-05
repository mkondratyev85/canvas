"""Module for different types of CanvasUnits."""

from dataclasses import dataclass
from typing import Optional, Type
from abc import ABC, abstractmethod

from .canvas import Canvas, Color, clip_lines_with_polygon


class CanvasUnitFloating(ABC):
    """Canvas Unit with floating property.

    I.e. it could be automatically placed on a canvas
    """

    name: str = "Элемент разреза без имени"
    height_mm = 10
    width_mm = 10
    layer = "New"
    origin = None, None
    canvas: Optional[Canvas] = None

    def __post_add__(self):
        """Called by canvas after unit is added to it."""

    def __draw__(self):
        """Called by canvas to trigger drawing of unit."""
        self.draw()

    @abstractmethod
    def draw(self):
        """Draws unit."""

    def __drop_shadow__(self):
        """Returns bounding box for Packer.

        Area enclosed by this bouding box is prohibit for other[:w CanvasUnits to be placed on.
        """

    def __place__(self, canvas):
        """Sets correct origin for self."""

    def draw_line(self, point0, point1, **kwargs):
        """Draws line on Subplot."""
        point0 = self.point_from_origin(*point0)
        point1 = self.point_from_origin(*point1)
        self.canvas.draw_line_canvas_mm(point0, point1, **kwargs)

    def draw_lines(self, points, **kwargs):
        """Draws line on subplot in coordinates given in mm."""
        points = [self.point_from_origin(*point) for point in points]
        self.canvas.draw_lines_canvas_mm(points, **kwargs)

    @clip_lines_with_polygon
    def draw_lines_inside_polygon(self, polygon, points, **kwargs):
        """Draw line inside given polygon."""
        # pylint: disable=unused-argument
        self.draw_lines(points, **kwargs)

    def draw_text(self, x, y, text, **kwargs):
        """Draws text on subplot with coordinates given in mm."""
        x, y = self.point_from_origin(x, y)
        self.canvas.draw_text_canvas_mm(x, y, text, **kwargs)

    def draw_rectangle(self, point0, size, **kwargs):
        """Draws rectangle on subplot with coordinates given in mm."""
        point0 = self.point_from_origin(*point0)
        self.canvas.draw_rectangle_canvas_mm(point0, size, **kwargs)

    def draw_circle(self, center, radius, **kwargs):
        """Draws a circle on subplot with coordinates given in mm."""
        center = self.point_from_origin(*center)
        self.canvas.draw_circle_canvas_mm(center, radius, **kwargs)

    def draw_table(self, origin, table, **kwargs):
        """Draws table on subplot in mm."""
        x, y = self.point_from_origin(*origin)
        self.canvas.draw_table_canvas_mm((x, y), table, **kwargs)

    def draw_border(self):
        """Draws border around canvas unit."""
        canvas = self.canvas
        canvas.draw_lines_canvas_mm(
            (
                (self.left, self.bottom),
                (self.left, self.top),
                (self.right, self.top),
                (self.right, self.bottom),
                (self.left, self.bottom),
            ),
            color=Color.RED,
        )

    def point_from_origin(self, x, y):
        """Returns point offsetted from origin."""
        x0, y0 = self.origin
        return x0 + x, y0 + y

    def relative_point(self, x_fraction, y_fraction):
        """Returns x, y coordinates based on x_fraction, y_fraction."""
        return self.width_mm * x_fraction, self.height_mm * y_fraction

    def draw_background(self, color=Color.WHITE):
        """Draws white background using origin and width of the unit."""
        if color == Color.WHITE:
            self.draw_rectangle((0, 0), (self.width_mm, self.height_mm), fill_rgb=(255, 255, 255))
        else:
            self.draw_rectangle((0, 0), (self.width_mm, self.height_mm), fill_color=color)

    @property
    def area(self):
        """Area of bounding box of floating unit."""
        return self.height_mm * self.width_mm

    @property
    def left(self):
        """Left level of floating point."""
        x0, _ = self.origin
        return x0

    @property
    def bottom(self):
        """Bottom level of floating point."""
        _, y0 = self.origin
        return y0

    @property
    def right(self):
        """Right level of floating unit."""
        x0, _ = self.origin
        return x0 + self.width_mm

    @property
    def top(self):
        """Top level of floating unit."""
        _, y0 = self.origin
        return y0 + self.height_mm

    def check_overlaps(self, other):
        """Check if self overlaps with rectangular bounding box of the other unit."""
        return not (
            self.right < other.left
            or self.left > other.right
            or self.top < other.bottom
            or self.bottom > other.top
        )


class CanvasUnitScaled(CanvasUnitFloating):
    """Floating Unit with scales.

    Used to plot things given in m on canvas respecting vertical scale, horizontal scale and offsets
    from the orgign
    """

    scale_horizontal: int = 1000
    scale_vertical: int = 100
    x_offset_m: float = 0
    y_offset_m: float = 0

    def __post_init__(self):
        """Update scales."""
        self.scale_horizontal_mm = 1000 / self.scale_horizontal
        self.scale_vertical_mm = 1000 / self.scale_vertical

    def scale(self, x, y):
        """Returns x and y scaled respecting horizontal and vertical scales."""
        x = self.scale_horizontal_mm * (x + self.x_offset_m)
        y = self.scale_vertical_mm * (y + self.y_offset_m)
        return x, y

    def mm_to_m_horizontal(self, mm):
        """Converts mm to m based on horizontal scale."""
        return mm / self.scale_horizontal_mm

    def mm_to_m_vertical(self, mm):
        """Converts mm to m based on horizontal scale."""
        return mm / self.scale_vertical_mm

    def m_to_mm_horizontal(self, m):
        """Converts m to mm based on horizontal scale."""
        return m * self.scale_horizontal_mm

    def m_to_mm_vertical(self, m):
        """Converts m to mm based on horizontal scale."""
        return m * self.scale_vertical_mm

    def draw_line_m(self, point0, point1, **kwargs):
        """Draws line on Subplot."""
        point0 = self.scale(*point0)
        point1 = self.scale(*point1)
        self.draw_line(point0, point1, **kwargs)

    def draw_lines_m(self, points, **kwargs):
        """Draws line on subplot in coordinates given in mm."""
        points = [self.scale(*point) for point in points]
        self.draw_lines(points, **kwargs)

    @clip_lines_with_polygon
    def draw_lines_m_inside_polygon(self, polygon, points, **kwargs):
        """Draw line inside given polygon."""
        # pylint: disable=unused-argument
        self.draw_lines_m(points, **kwargs)

    def draw_text_m(self, x, y, text, **kwargs):
        """Draws text on subplot with coordinates given in mm."""
        x, y = self.scale(x, y)
        self.draw_text(x, y, text, **kwargs)

    def draw_rectangle_m(self, point0, size, **kwargs):
        """Draws rectangle on subplot with coordinates given in mm."""
        point0 = self.scale(*point0)
        self.draw_rectangle(point0, size, **kwargs)

    def draw_circle_m(self, center, radius, **kwargs):
        """Draws a circle on subplot with coordinates given in mm."""
        center = self.scale(*center)
        self.draw_circle(center, radius, **kwargs)

    def draw_table_m(self, origin, table, **kwargs):
        """Draws table on subplot in mm."""
        x, y = self.scale(*origin)
        self.draw_table((x, y), table, **kwargs)


@dataclass
class CanvasUnitLinked(CanvasUnitScaled):
    """Scaled Canvas Unit that is linked to the another one.

    It will take parameters for scaling and origin from another it.
    """

    # pylint: disable=too-many-instance-attributes

    linked_cu: Type[CanvasUnitScaled]

    def __post_init__(self):
        """Sets scales, offsets and origin from linked_cu to self."""
        self.scale_horizontal = self.linked_cu.scale_horizontal
        self.scale_vertical = self.linked_cu.scale_horizontal
        self.scale_horizontal_mm = self.linked_cu.scale_horizontal_mm
        self.scale_vertical_mm = self.linked_cu.scale_vertical_mm
        self.x_offset_m = self.linked_cu.x_offset_m
        self.y_offset_m = self.linked_cu.y_offset_m
        self.origin = self.linked_cu.origin
