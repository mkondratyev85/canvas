"""Module for abstract class for backend used by Canvas to create output files."""

from typing import Optional, Tuple, List, Union
from abc import ABC, abstractmethod
from enum import Enum


class LineType(Enum):
    """Line types used by canvas."""

    SOLID = 0
    DOT = 1
    THAWED = 2
    DASH = 3


class Color(Enum):
    """Colors used by canvas."""

    BLACK = 0
    WHITE = 1
    RED = 2
    BLUE = 3
    ORANGE = 4
    GRAY = 5
    GREEN = 6


class Font(Enum):
    """Fonts used by canvas."""

    SERIAL = 0


class TextAligment(Enum):
    """Text Aligments used by canvas."""

    TOP_LEFT = 0
    TOP_CENTER = 1
    TOP_RIGHT = 3
    LEFT = 4
    CENTER = 5
    RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_CENTER = 8
    BOTTOM_RIGHT = 9


class Backend(ABC):
    """Abstract class for backend used by Canvas to create output files."""

    # pylint: disable=too-many-arguments

    def __pre_draw__(self):
        """Called before drawing elements to file."""

    @abstractmethod
    def add_layer(
        self,
        layer_name: str,
        line_type: LineType = LineType.SOLID,
        color: Optional[Color] = None,
        width: float = 0.3,
        transparency: Optional[float] = None,
    ):
        """Add a layer.

        Args:
            layer_name: The name of the layer.
            line_type: Type of the line used in the layer (Required for DXF).
            color: Color of the lines used in this layer.
            width: Thickness of the lines.
            transparency: Transparency of the layer.
        """

    @abstractmethod
    def draw_rectangle(
        self,
        origin: Tuple[float, float],
        size: Tuple[float, float],
        fill_color: Color = Color.BLACK,
        fill_rgb: Optional[Tuple[float, float, float]] = None,
        edge_color: Optional[Color] = None,
        width: float = 1,
        layer_name: Optional[str] = None,
    ):
        """Draw rectangle.

        Args:
            origin: Top left corner of the rectangle.
            size: width and height of the rectangle.
            fill_color: Color to use to fill rectangle.
            edge_color: Color for the edge lines.
            width: thicknes of the lines.
            layer_name: the name of the layer to draw rectangle in.
        """

    @abstractmethod
    def draw_lines(
        self,
        points: Tuple[Tuple[float, float]],
        color: Color = Color.BLACK,
        width: float = 0.3,
        line_type: LineType = LineType.SOLID,
        fill: Optional[Color] = None,
        fill_rgb: Optional[Tuple[float, float, float]] = None,
        transparency: Optional[float] = None,
        pattern=None,
        layer_name: Optional[str] = None,
    ):
        """Draw lines.

        Args:
            points: list of line nodes.
            color: the color of the line.
            width: thickness of the line.
            line_type: recieves `LineType` value.
            fill: `Color` value to fill with.
            fill_rgb: red, green, blue values used to fill polygon.
            pattern: Used in dxf mainly.
            layer_name: the name of the layer to draw rectangle in.
            transparency: Transparency of the layer.
        """

    @abstractmethod
    def draw_circle(
        self,
        center: Tuple[float, float],
        radius: float,
        line_type: LineType = LineType.SOLID,
        color: Color = Color.BLACK,
        layer_name: Optional[str] = None,
    ):
        """Draws circle.

        Args:
            center: center of the circle.
            radius: radius of the circle.
            color: receives `Color` value for the line.
            line_type: receives `LineType` value.
            layer_name: the name of the layer to draw rectangle in.
        """

    @abstractmethod
    def draw_text(
        self,
        origin: Tuple[float, float],
        text: str,
        size: float = 10,
        color: Color = Color.BLACK,
        white_background: bool = False,
        angle: float = 0,
        wrap_width: Optional[float] = None,
        font: Font = Font.SERIAL,
        aligment: TextAligment = TextAligment.LEFT,
        layer_name: Optional[str] = None,
    ):
        """Draws text.

        Args:
            origin: top left corner of the rectangle.
            text: strings used to draw text.
            size: text size.
            color: receives `Color` value for the line.
            white_background: draw white background behind text if set to True.
            angle: angle of rotation of text.
            wrap_width: if set - this value will be used to split text into several lines
                        one below another to make sure text width will not exceed this value.
            font: `Font` used to draw text.
            aligment: `TextAligment` used to place text.
            layer_name: the name of the layer to draw rectangle in.
        """

    @abstractmethod
    def draw_table(
        self,
        origin: Tuple[float, float],
        dimensions: Tuple[float, float],
        values: List[List[Union[float, str]]],
        row_height: float = 3,
        col_width: float = 18,
        text_height: float = 2.4,
        heading: bool = True,
        heading_height: float = 12,
    ):
        """Draw a table.

        Args:
            origin: top left corner of the table rectangle.
            dimensions: number of rows and number of cols.
            values: 2d list of values to draw on the table.
            row_height: height of the rows.
            col_width: width of the cols.
            text_height: text size.
            heading: draw heading row using `heading_height` parameter.
            heading_height: height of the heading row.
        """

    @abstractmethod
    def save_to_file(self):
        """Save drawing to dxf file and to png file if plot_to_png set to True."""
