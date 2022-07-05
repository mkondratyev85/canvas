"""Module for CanvasCairo."""
from typing import Tuple, Optional, List, Union
from math import pi, radians

import cairo

from .backend import Backend, LineType, Color, Font, TextAligment
from .logger import logger

COLORS = {
    Color.BLUE: (0, 0, 1),
    Color.RED: (1, 0, 0),
    Color.BLACK: (0, 0, 0),
    Color.GRAY: (0.7, 0.7, 0.7),
    Color.WHITE: (1, 1, 1),
    Color.ORANGE: (1, 0.5, 0),
    Color.GREEN: (0, 1, 0),
}

FONTS = {
    Font.SERIAL: "OpenSans",
}


def transform_rgb(red, green, blue):
    """Scale down rgb colors from 0-255 to 0-1."""

    return red / 255, green / 255, blue / 255


def wrap_text(func):
    def wrapper(
        self,
        origin: Tuple[float, float],
        text: str,
        wrap_width: Optional[float] = None,
        size: float = 10,
        font: Font = Font.SERIAL,
        **kwargs,
    ):
        self.ctx.select_font_face(FONTS[font])
        self.ctx.set_font_size(size * 1.5)

        x, y = origin

        for line in iterate_over_new_line_string(text):
            for segment, height in iterate_over_segments_width(
                text=line, wrap_width=wrap_width, context=self.ctx
            ):
                func(self, origin=(x, y), text=segment, **kwargs)
                y -= height

    return wrapper


def iterate_over_segments_width(text, wrap_width, context):
    if not wrap_width:
        (_, _, _, height, _, _) = context.text_extents(text)
        yield text, height
        return
    words = text.split(" ")
    sentence = ""
    while words:
        word = words.pop(0)
        (_, _, width, height, _, _) = context.text_extents(str(sentence + " " + word))
        if width < wrap_width:
            sentence = sentence + " " + word
            continue
        yield sentence, height
        sentence = word
    yield sentence, height


def iterate_over_new_line_string(text):
    for line in text.split("\n"):
        yield line


class CanvasCairo(Backend):
    """Class to produce pdf files via Cairo."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments

    def __init__(self, image_file, width_in_mm=500, height_in_mm=420):
        if not image_file.endswith(".pdf"):
            image_file += ".pdf"
        self.imagefile = image_file
        self.width_in_mm, self.height_in_mm = width_in_mm, height_in_mm

    def get_surface(self):
        return cairo.PDFSurface(self.imagefile, self.width, self.height)

    def __pre_draw__(self):
        # pylint: disable=attribute-defined-outside-init
        # pylint: disable=no-member

        width_in_inches, height_in_inches = self.width_in_mm / 25.4, self.height_in_mm / 25.4
        width_in_points, height_in_points = width_in_inches * 72, height_in_inches * 72
        self.width, self.height = width_in_points, height_in_points

        self.surface = self.get_surface()
        self.ctx = cairo.Context(self.surface)
        self._transform_to_mm()

        # self.load_patterns()

    def _transform_to_mm(self):
        self.ctx.scale(self.width, self.height)  # Normalizing the canvas
        self.ctx.scale(1 / self.width_in_mm, 1 / self.height_in_mm)
        # matrix_mm = cairo.Matrix(y0=self.height_in_mm, yy=-1)
        # self.ctx.transform(matrix_mm)

    def _transform_coordinates(self, x, y):
        y = self.height_in_mm - y
        return x, y

    def _transform_coordinates_back(self, x, y):
        y = self.height_in_mm - y
        return x, y

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

        x0, y0 = self._transform_coordinates(*origin)

        # cairo_color = COLORS[fill_color] if fill_color else transform_rgb(*fill_rgb)
        cairo_color = transform_rgb(*fill_rgb) if fill_rgb else COLORS[fill_color]
        self.ctx.set_source_rgb(*cairo_color)

        self.ctx.rectangle(x0, y0, size[0], -1 * size[1])
        self.ctx.fill_preserve()

        if edge_color:
            self.ctx.set_line_width(width)
            self.ctx.set_source_rgb(*COLORS[edge_color])
        self.ctx.stroke()

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
        if line_type == LineType.DOT:
            self.ctx.set_dash([width * 4])
        elif line_type == LineType.THAWED:
            self.ctx.set_dash([width * 5])
        elif line_type == LineType.DASH:
            self.ctx.set_dash([width * 6])
        else:
            self.ctx.set_dash([])
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)  # pylint: disable=no-member

        point0 = self._transform_coordinates(*points[0])
        self.ctx.move_to(*point0)

        for point in points[1:]:
            point = self._transform_coordinates(*point)
            self.ctx.line_to(*point)

        if pattern:
            fill = Color.GRAY

        if fill or fill_rgb:
            self.ctx.close_path()
            cairo_color = COLORS[fill] if fill else transform_rgb(*fill_rgb)

            if transparency:
                self.ctx.set_source_rgba(*cairo_color, transparency)
            else:
                self.ctx.set_source_rgb(*cairo_color)
            self.ctx.fill()

        if color:
            self.ctx.set_source_rgb(*COLORS[color])
            self.ctx.set_line_width(width)
            self.ctx.stroke()

    @wrap_text
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
        # pylint: disable=too-many-locals
        color = COLORS[color]
        self.ctx.set_source_rgb(*color)

        # x, y = self._transform_coordinates(*origin)
        x_original, y_original = self._transform_coordinates(*origin)
        self.ctx.translate(x_original, y_original)
        self.ctx.rotate(radians(-angle))

        x, y = 0, 0

        (_, _, width, height, _, _) = self.ctx.text_extents(str(text))
        if aligment == TextAligment.LEFT:
            pass
        elif aligment in [TextAligment.CENTER, TextAligment.BOTTOM_CENTER, TextAligment.TOP_CENTER]:
            x -= 0.5 * width
        elif aligment in [TextAligment.RIGHT, TextAligment.BOTTOM_RIGHT, TextAligment.TOP_RIGHT]:
            x -= width
        if aligment in [
            TextAligment.BOTTOM_LEFT,
            TextAligment.BOTTOM_CENTER,
            TextAligment.BOTTOM_RIGHT,
        ]:
            y += 0.5 * height
        elif aligment in [TextAligment.TOP_LEFT, TextAligment.TOP_CENTER, TextAligment.TOP_RIGHT]:
            y += 1.0 * height

        if white_background:
            x_new, y_new = self._transform_coordinates_back(x, y)
            self.draw_rectangle((x_new, y_new), (width, height), fill_color=Color.WHITE)
            self.ctx.set_source_rgb(*color)

        # self.ctx.translate(x_original, y_original)
        # self.ctx.rotate(radians(-angle))
        # self.ctx.move_to(0, 0)
        self.ctx.move_to(x, y)
        self.ctx.show_text(text)

        self.ctx.rotate(radians(angle))
        self.ctx.translate(-x_original, -y_original)

    def add_layer(
        self,
        layer_name: str,
        line_type: LineType = LineType.SOLID,
        color: Optional[Color] = None,
        width: float = 0.3,
        transparency: Optional[float] = None,
    ):
        pass

    def draw_circle(
        self,
        center: Tuple[float, float],
        radius: float,
        line_type: LineType = LineType.SOLID,
        color: Color = Color.BLACK,
        layer_name: Optional[str] = None,
    ):
        x, y = self._transform_coordinates(*center)
        self.ctx.move_to(x, y)
        self.ctx.arc(x, y, radius, 0, 2 * pi)
        self.ctx.set_source_rgb(*COLORS[color])
        self.ctx.set_line_width(0.04)
        self.ctx.stroke()

    # flake8: noqa: D102
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
        x0, y0 = origin

        if heading:
            heading_row = values.pop(0)
            y_top = y0
            point_left = x0, y_top
            point_right = x0 + col_width * (len(heading_row)), y_top
            self.draw_lines((point_left, point_right), width=0.1)
            y0 -= heading_height
            for cell_number, cell in enumerate(heading_row):
                x_left = x0 + col_width * cell_number
                y_bottom = y_top - row_height
                y_bottom2 = y_top - heading_height
                point_bottom_left = x_left, y_bottom
                point_bottom_left2 = x_left, y_bottom2
                point_top_left = x_left, y_top
                self.draw_lines((point_bottom_left2, point_top_left), width=0.1)
                self.draw_text(point_bottom_left, str(cell), size=text_height)

            x_left = x0 + col_width * (cell_number + 1)
            point_bottom_left2 = x_left, y_bottom2
            point_top_left = x_left, y_top
            self.draw_lines((point_bottom_left2, point_top_left), width=0.1)

        for row_number, row in enumerate(values):
            y_top = y0 - row_height * row_number
            point_left = x0, y_top
            point_right = x0 + col_width * (len(row)), y_top
            self.draw_lines((point_left, point_right), width=0.1)
            for cell_number, cell in enumerate(row):
                x_left = x0 + col_width * cell_number
                y_bottom = y_top - row_height
                point_bottom_left = x_left, y_bottom
                point_top_left = x_left, y_top
                self.draw_lines((point_bottom_left, point_top_left), width=0.1)
                self.draw_text(point_bottom_left, str(cell), size=text_height)

            x_left = x0 + col_width * (cell_number + 1)
            point_bottom_left = x_left, y_bottom
            point_top_left = x_left, y_top
            self.draw_lines((point_bottom_left, point_top_left), width=0.1)

        y_top = y0 - row_height * (row_number + 1)
        point_left = x0, y_top
        point_right = x0 + col_width * (len(row)), y_top
        self.draw_lines((point_left, point_right), width=0.1)

    # flake8: noqa: D102
    def save_to_file(self):
        self.surface.finish()
