"""Module to save canvas drawings as dxf file."""

from typing import Optional, Tuple, List, Union

import ezdxf
from ezdxf.addons import Table

from .dxf_hatch_patterns import PATTERNS
from .backend import Backend, LineType, Color, Font, TextAligment

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint:disable=duplicate-code


LINE_TYPES = {
    LineType.SOLID: "CONTINUOUS",
    LineType.DOT: "DASHED3",
    LineType.THAWED: "THAWED_ZONE2",  # custom type defined in add_linetypes()
    LineType.DASH: "DASHED3",
}

COLORS = {
    Color.BLUE: ezdxf.rgb2int((0, 0, 255)),
    Color.RED: ezdxf.rgb2int((255, 0, 0)),
    Color.BLACK: ezdxf.rgb2int((0, 0, 0)),
    Color.GRAY: ezdxf.rgb2int((125, 125, 125)),
    Color.WHITE: ezdxf.rgb2int((255, 255, 255)),
}

COLOR_INDEXES = {
    Color.BLUE: 5,
    Color.RED: 1,
    Color.BLACK: 0,
    Color.WHITE: 255,
    Color.GRAY: 9,
    Color.ORANGE: 30,
}

MTEXT_ALIGMENTS = {
    TextAligment.TOP_LEFT: 1,  # 'MTEXT_TOP_LEFT',
    TextAligment.TOP_CENTER: 2,  # 'MTEXT_TOP_CENTER',
    TextAligment.TOP_RIGHT: 3,  # 'MTEXT_TOP_RIGHT',
    TextAligment.LEFT: 4,  # 'MTEXT_MIDDLE_LEFT',
    TextAligment.CENTER: 5,  # 'MTEXT_MIDDLE_CENTER',
    TextAligment.RIGHT: 6,  # 'MTEXT_MIDDLE_RIGHT',
    TextAligment.BOTTOM_LEFT: 7,  # 'MTEXT_BOTTOM_LEFT',
    TextAligment.BOTTOM_CENTER: 8,  # 'MTEXT_BOTTOM_CENTER',
    TextAligment.BOTTOM_RIGHT: 9,  # 'MTEXT_BOTTOM_RIGHT',
}

TEXT_ALIGMENTS = {
    TextAligment.LEFT: "LEFT",
    TextAligment.RIGHT: "RIGHT",
    TextAligment.CENTER: "CENTER",
    TextAligment.TOP_LEFT: "TOP_LEFT",
    TextAligment.TOP_RIGHT: "TOP_RIGHT",
    TextAligment.TOP_CENTER: "TOP_CENTER",
    TextAligment.BOTTOM_CENTER: "BOTTOM_CENTER",
    TextAligment.BOTTOM_LEFT: "BOTTOM_LEFT",
    TextAligment.BOTTOM_RIGHT: "BOTTOM_RIGHT",
}

FONTS = {
    Font.SERIAL: "OpenSans",
}


class CanvasDxf(Backend):
    """Canvas functions to save to dxf."""

    # pylint: disable=too-many-instance-attributes

    imagefile = None
    width_in_mm = 500
    height_in_mm = 420

    def __init__(self, image_file, patterns=None):

        self.patterns = patterns or PATTERNS
        self.image_file = image_file
        self.doc = ezdxf.new(dxfversion="R2010", setup=True)
        self.msp = self.doc.modelspace()
        self.psp = self.doc.layout("Layout1")

    def create_psp(self):
        """Creates paper space."""
        width_in_mm = self.width_in_mm
        height_in_mm = self.height_in_mm

        self.psp.page_setup(
            size=(width_in_mm, height_in_mm), margins=(0, 0, 0, 0), units="mm"
        )  # , scale=(1000, 1000))
        (x1, y1), (x2, y2) = self.psp.get_paper_limits()
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        self.psp.add_viewport(
            # center=(center_x, center_y),  # center of viewport in paper_space units
            center=(
                width_in_mm / 2,
                height_in_mm / 2,
            ),  # center of viewport in paper_space units
            size=(width_in_mm, height_in_mm),  # viewport size in paper_space units
            view_center_point=(
                center_x,
                center_y,
            ),  # model space point to show in center of viewport in WCS
            view_height=height_in_mm,  # how much model space area to show
            # in viewport in drawing units
        )

        # allow drawing of dashed line types as an uninterrupted pattern
        # through the vertices of the polyline
        self.doc.header["$PLINEGEN"] = 1

        self.add_linetypes()

    def add_linetypes(self):
        """Adds aditional linetypes to self.doc."""
        # # setup predefined linetypes
        self.doc.linetypes.new(
            name="DASHED3",
            dxfattribs={"description": "Dashed (x3 2)", "pattern": [4, 2, -2]},
        )

        self.doc.linetypes.new(
            "THAWED_ZONE2",
            dxfattribs={
                "description": " Thawed zone border",
                "length": 3.0,
                "pattern": 'A,2.0,["T",STANDARD,s=1.0,x=-1.5,y=-1.0],-1.0',
            },
        )

    def add_layer(
        self,
        layer_name: str,
        line_type: LineType = LineType.SOLID,
        color: Optional[Color] = None,
        width: float = 0.3,
        transparency: Optional[float] = None,
    ):
        # pylint:disable=duplicate-code

        layer_attribs = {
            "linetype": LINE_TYPES[line_type],
            "true_color": color,
            "lineweight": width * 100,
        }
        if color:
            layer_attribs["true_color"] = COLORS[color]

        try:
            layer = self.doc.layers.new(
                name=layer_name,
                dxfattribs=layer_attribs,
            )
        except ezdxf.lldxf.const.DXFTableEntryError:
            # skip the error if the layer already exists
            pass

        if transparency:
            layer.transparency = transparency

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
        # pylint:disable=duplicate-code

        if edge_color:
            edge_color = COLORS[edge_color]
        if fill_rgb:
            fill_color = None
        x0, y0 = origin[0], origin[1]
        x1, y1 = x0 + size[0], y0 + size[1]
        points = ((x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0))
        self.draw_lines(
            points,
            fill=fill_color,
            fill_rgb=fill_rgb,
            color=edge_color,
            layer_name=layer_name,
            width=width,
        )

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
        # pylint:disable=duplicate-code
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-locals

        attribs = {
            "ltscale": 1.5,
        }

        if layer_name:
            attribs["layer"] = layer_name
            attribs["color"] = 256
            if pattern:
                attribs["linetype"] = "BYLAYER"
        else:
            if color:
                attribs["color"] = COLOR_INDEXES[color]
            attribs["linetype"] = LINE_TYPES[line_type]
            attribs["lineweight"] = width * 100

        # special flag to make rendering of polyline line pattern continuous
        # along the whole line (instead of each segment of the polyline on it's own)
        attribs["flags"] = 128

        if not pattern:
            polyline = self.msp.add_lwpolyline(
                points,
                dxfattribs=attribs,
            )
        if fill or fill_rgb:
            polyline.close(True)
            if fill_rgb:
                color = ezdxf.rgb2int(fill_rgb)
            else:
                color = COLOR_INDEXES[fill]
            if layer_name:
                color = 256
            hatch = self.msp.add_hatch(color=color, dxfattribs={"true_color": color})
            if layer_name:
                hatch = self.msp.add_hatch(
                    color=color,
                    dxfattribs={
                        "layer": layer_name,
                        "color": 256,
                    },
                )
            if transparency:
                hatch.transparency = 1 - transparency
            hatch.paths.add_polyline_path(points, is_closed=1)
        elif pattern:
            hatch = self.msp.add_hatch()
            if layer_name:
                hatch = self.msp.add_hatch(dxfattribs={"layer": layer_name})
            pattern_name = pattern
            pattern_ = self.patterns[pattern_name]
            if "name" not in pattern_:
                pattern_["name"] = pattern_name
            hatch.set_pattern_fill(**pattern_)
            hatch.paths.add_polyline_path(points, is_closed=1)

    def draw_circle(
        self,
        center: Tuple[float, float],
        radius: float,
        line_type: LineType = LineType.SOLID,
        color: Color = Color.BLACK,
        layer_name: Optional[str] = None,
    ):
        # pylint:disable=duplicate-code
        attribs = {}
        if layer_name:
            attribs["layer"] = layer_name
            attribs["color"] = COLOR_INDEXES[color]
            attribs["linetype"] = LINE_TYPES[line_type]
        self.msp.add_circle(center=center, radius=radius, dxfattribs=attribs)

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
        # pylint:disable=duplicate-code
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-locals

        attribs = {
            "style": FONTS[font],
            "rotation": angle,
            "color": COLOR_INDEXES[color],
        }
        if layer_name:
            attribs["layer"] = layer_name
        if wrap_width:
            attribs["char_height"] = size
            attribs["insert"] = origin
            attribs["attachment_point"] = MTEXT_ALIGMENTS[aligment]
            attribs["width"] = wrap_width
            self.msp.add_mtext(text, dxfattribs=attribs)
        else:
            attribs["height"] = size
            self.msp.add_text(
                text,
                dxfattribs=attribs,
            ).set_pos((origin), align=TEXT_ALIGMENTS[aligment])

    def save_to_file(self):
        """Save drawing to dxf file and to png file if plot_to_png set to True."""
        self.create_psp()
        self.doc.saveas(self.image_file)

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
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-locals
        # pylint: disable=duplicate-code

        nrows, ncols = dimensions
        table = Table(insert=origin, nrows=nrows, ncols=ncols)
        ctext = table.new_cell_style(
            name="ctext",
            textcolor=7,
            textheight=text_height,
            align="MIDDLE_CENTER",
        )

        border = table.new_border_style(color=0, priority=51)
        ctext.set_border_style(border)  # , right=False)

        for i in range(len(values)):
            table.set_row_height(i, row_height)
        for i in range(len(values[0])):
            table.set_col_width(i, col_width)
        if heading:
            table.set_row_height(0, heading_height)

        for i, row in enumerate(values):
            for j, value in enumerate(row):
                table.text_cell(i, j, str(value), style="ctext")
        table.render(self.msp, insert=origin)
