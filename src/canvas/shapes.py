"""Module for shapes used by gashura."""

from abc import ABC
from typing import Tuple, Generator, Iterable
import math
from itertools import cycle

from .canvas_units import CanvasUnitLinked

from .backend import Color

class Shape(ABC):
    """A class for Shape that is being drawed on the canvas."""

    points: Tuple[Tuple[float, float], ...]
    size: float = 1
    shadow_radius: float = 2
    dx_mm: int = 3
    dy_mm: int = 3
    line_width = 0.1

    def __init__(self):
        self.points = tuple(self.__resize__())

    def __resize__(self) -> Generator[Tuple[float, float], None, None]:
        """Resize points."""
        for x, y in self.points:
            yield x * self.size, y * self.size

    def __scale__(self, points, scale) -> Generator[Tuple[float, float], None, None]:
        """Resize points."""
        for x, y in points:
            yield x * scale, y * scale

    def __rotate__(
        self, points: Iterable, angle: float
    ) -> Generator[Tuple[float, float], None, None]:
        """Rotate each point in self.

        Args:
            points: points to rotate.
            angle: angle of rotation in degrees

        Yields:
            Tuple of coordinates for each point.
        """
        # pylint: disable=no-self-use
        angle = math.radians(angle)
        sin = math.sin(angle)
        cos = math.cos(angle)

        for x, y in points:
            new_x = x * cos - y * sin
            new_y = x * sin + y * cos
            yield new_x, new_y

    def __translate__(
        self, points: Iterable, position: Tuple[float, float]
    ) -> Generator[Tuple[float, float], None, None]:
        """Move shape.

        Args:
            position: new coordinates of the shape.
            points: set of points to translate.

        Yields:
            List of translated points.
        """
        # pylint: disable=no-self-use
        dx, dy = position

        for x, y in points:
            yield x + dx, y + dy

    def scale_back(
        self, points: Iterable, canvas_unit: CanvasUnitLinked
    ) -> Generator[Tuple[float, float], None, None]:
        """Scale points from scaled unit to floating canvas unit.

        Args:
            points: point to scale back.
            canvas_unit: canvas unit to use for scaling.

        Yields:
            List of translated points.
        """
        # pylint: disable=no-self-use
        for x, y in points:
            yield canvas_unit.scale(x, y)

    def draw(
        self,
        position: Tuple[float, float],
        angle: float,
        canvas_unit: CanvasUnitLinked,
        polygon=None,
        color=Color.BLACK,
        scale=1,
    ) -> None:
        """Draws shape at given position.

        Args:
            position: coordinates of the shape center
            angle: angle of rotation
            canvas_unit: Unit that draws the shape
            polygon: Polygon to draw shapes only inside.
        """
        if isinstance(canvas_unit, CanvasUnitLinked):
            position = tuple(self.scale_back([position], canvas_unit))[0]
            polygon = tuple(self.scale_back(polygon, canvas_unit))

        points = self.__rotate__(self.points, angle)
        points = self.__scale__(points, scale)
        points = self.__translate__(points, position)
        points = tuple(points)

        if polygon:
            canvas_unit.draw_lines_inside_polygon(polygon, points, width=self.line_width*scale, color=color)
        else:
            canvas_unit.draw_lines(points, width=self.line_width*scale, color=color)


class MultiShape(Shape):
    """As Shape but consists of repiting different shapes."""

    shapes = Tuple[Shape]

    def __init__(self):
        self.iterator = cycle(self.shapes)

    def draw(
        self,
        position: Tuple[float, float],
        angle: float,
        canvas_unit: CanvasUnitLinked,
        polygon=None,
        color=None,
        scale=1,
    ) -> None:
        """Draws shape at given position.

        Args:
            position: coordinates of the shape center
            angle: angle of rotation
            canvas_unit: Unit that draws the shape
            polygon: Polygon to draw shapes only inside.
        """
        shape = next(self.iterator)
        shape.draw(position, angle, canvas_unit, polygon, color=color, scale=scale)


class Glina(Shape):
    """Shape for il in gashura."""

    size = 2
    points = ((-0.5, 0), (0.5, 0))
    shadow_radius = size


class Torf(Shape):
    """Shape for il in gashura."""

    size = 1
    points = ((-0.5, 0), (0.5, 0))
    shadow_radius = size


class Il(Shape):
    """Shape for il in gashura."""

    size = 2
    shadow_radius = size
    points = (
        (-0.5, 0),
        (-0.25, 0.1),
        (0.25, -0.1),
        (0.5, 0),
    )


class Galechnik(Shape):
    """Shape for galechink."""

    points = (
        (1.0, 0.0),
        (0.8660254037844387, 0.24999999999999997),
        (0.5000000000000001, 0.4330127018922193),
        (6.123233995736766e-17, 0.5),
        (-0.4999999999999998, 0.43301270189221935),
        (-0.8660254037844387, 0.24999999999999997),
        (-1.0, 6.123233995736766e-17),
        (-0.8660254037844386, -0.25000000000000006),
        (-0.5000000000000004, -0.4330127018922192),
        (-1.8369701987210297e-16, -0.5),
        (0.5000000000000001, -0.4330127018922193),
        (0.8660254037844384, -0.2500000000000002),
        (1.0, -1.2246467991473532e-16),
    )


class Valunnik(Galechnik):
    """Shape for valunnik."""

    size = 2
    dx_mm = 5
    dy_mm = 5


class Gravyi(Galechnik):
    """Shape for graviy."""

    size = 0.5
    dx_mm = 2
    dy_mm = 2


class Sand(Shape):
    """Shape for sand."""

    size = 0.1
    dx_mm = 2
    dy_mm = 2
    points = (
        (1.0, 0.0),
        (0.0, 1.0),
        (-1.0, 0.0),
        (0.0, -1.0),
        (1.0, 0.0),
    )


class Dresva(Shape):
    """Shape for Dresva."""

    size = 0.5
    dx_mm = 2
    dy_mm = 2
    points = (
        (-1.0, 0.2),
        (0.1, 0.6),
        (-0.2, -0.8),
        (-1.0, 0.2),
    )


class Sheben(Dresva):
    """Shape for galechink."""

    size = 1
    dx_mm = 3
    dy_mm = 3


class Spai(MultiShape):
    """Multishape for Spai."""

    shapes = (Sheben(), Gravyi())
    dx_mm = 2
    dy_mm = 2


class Andesit(Shape):
    """Shape for andesit in gashura."""

    size = 1
    points = ((-0.5, 1), (0, 0), (0.5, 1))
    shadow_radius = size

class Dacit(Shape):
    """Shape for andesit in gashura."""

    size = 1
    points = ((-0.5, 0), (0, 1), (0.5, 0))
    shadow_radius = size


class Basalt(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((-0.5, 1), (-0.5, 0), (0.5, 0))
    shadow_radius = size


class Riolite_left(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((-0.5, 1), (0, 0))
    shadow_radius = size


class Riolite_right(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((0, 0), (0.5, 1))
    shadow_radius = size

class Riolite_up(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((0, 0), (1, 0.5))
    shadow_radius = size

class Riolite_down(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((1, -0.5), (0, 0))
    shadow_radius = size


class Riolite(MultiShape):
    """Multishape for Andesibasalt."""

    shapes = (Riolite_left(), Riolite_up(), Riolite_right(), Riolite_down())
    dx_mm = 3
    dy_mm = 3


class Andesibasalt(MultiShape):
    """Multishape for Andesibasalt."""

    shapes = (Andesit(), Basalt())
    dx_mm = 3
    dy_mm = 3

class Andesidacit(MultiShape):
    """Multishape for Andesidacit."""

    shapes = (Andesit(), Dacit())
    dx_mm = 3
    dy_mm = 3


class AndesibasaltTuff(MultiShape):
    """Multishape for Andesibasalt."""

    shapes = (Andesit(), Sand(), Basalt(), Sand())
    dx_mm = 3
    dy_mm = 3


class Granite(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((-.5, 0), (0.5, 0), (0, 0), (0, .5), (0, -.5))
    shadow_radius = size


class Diorite(Shape):
    """Shape for Baslat in gashura."""

    size = 1
    points = ((-.4, -.4), (.4, .4), (0, 0), (-.4, .4), (.4, -.4))
    shadow_radius = size


class Granodiorite(MultiShape):
    """Multishape for Andesibasalt."""

    shapes = (Granite(), Diorite())
    dx_mm = 3
    dy_mm = 3
