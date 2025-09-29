import math
from .canvas_units import CanvasUnitLinked
from .shapes import Il, Glina, Galechnik, Valunnik, Gravyi, Sand, Dresva, Sheben, Spai, Andesit, Basalt, Andesibasalt, AndesibasaltTuff, Riolite, Granodiorite, Andesidacit, Dacit, Diorite, Granite
from .shapes import create_shape_for_rock_and_aggregate
from .shapes import create_shape_for_rock_and_aggregates
from .canvas import LineType


rock_shapes = {
    "галечник": Galechnik(),
    "валунник": Valunnik(),
    "гравий": Gravyi(),
    "ил": Il(),
    "песок": Sand(),
    "глина": Glina(),
    "дресва": Dresva(),
    "щебень": Sheben(),
    "спай": Spai(),
    "андезит": Andesit(),
    "дацит": Dacit(),
    "базальт": Basalt(),
    "андезибазальт": Andesibasalt(),
    "андезидацит": Andesidacit(),
    "андезибазальт туф": AndesibasaltTuff(),
    "риолит": Riolite(),
    "гранодиорит": Granodiorite(),
    "диорит": Diorite(),
    "гранит": Granite(),
}


def fill_polygon_with_pattern(canvas_unit, rock, polygon, bounding_box, dip_function, aggregate=None, color=None, scale=1, offset_factor=1):
    """Draw hatches with new style."""
    if rock == "торф":
        fill_polygon_with_lines_vertical(canvas_unit, polygon=polygon, bounding_box=bounding_box)
    elif rock == "прс":
        fill_polygon_with_lines_vertical(canvas_unit, polygon=polygon, bounding_box=bounding_box, dx_mm=1.0)
    elif rock == "коренные породы":
        fill_polygon_with_lines_diagonal(
            canvas_unit, polygon=polygon, bounding_box=bounding_box, alter_linetype=True
        )
    elif rock in ("сланцы", "переходный слой (трещиноватый коренник)"):
        fill_polygon_with_lines_diagonal(
            canvas_unit, polygon=polygon, bounding_box=bounding_box, alter_linetype=False, d_mm=2
        )
    else:
        if rock in rock_shapes:
            shape = rock_shapes[rock]
        else:
            print(f"Can't find shape for {rock}")
            return
        shape = rock_shapes[rock]
        if aggregate:
            aggregate_shapes = []
            if isinstance(aggregate, str):
                aggregate = [aggregate]
            for r in aggregate:
                if r not in rock_shapes:
                    return
                # aggregate_shape = rock_shapes[aggregate]
                aggregate_shapes.append(rock_shapes[r])
            shape = create_shape_for_rock_and_aggregates(shape, aggregate_shapes)

        fill_polygon_with_shapes(
            canvas_unit,
            polygon=polygon,
            bounding_box=bounding_box,
            dip_function=dip_function,
            shape=shape,
            color=color,
            scale=scale,
            offset_factor=offset_factor,
        )


def fill_polygon_with_lines_vertical(canvas_unit, polygon, bounding_box, dx_mm=2.0) -> None:
    """Draw lines inside polygon."""
    x0, x1, y0, y1 = bounding_box

    if isinstance(canvas_unit, CanvasUnitLinked):
        dx_m = canvas_unit.mm_to_m_horizontal(dx_mm)
    else:
        dx_m = dx_mm

    x = x0 - x0 % dx_m
    while x < x1:
        x += dx_m
        line = ((x, y0), (x, y1))
        if isinstance(canvas_unit, CanvasUnitLinked):
            canvas_unit.draw_lines_m_inside_polygon(polygon=polygon, points=line, width=0.1)
        else:
            canvas_unit.draw_lines_inside_polygon(polygon=polygon, points=line, width=0.1)


def fill_polygon_with_lines_diagonal(
    canvas_unit, polygon, bounding_box, color=None, linetype=None, alter_linetype: bool = False, d_mm: float = 3.0
) -> None:
    """Draw lines inside polygon."""
    x0, x1, y0, y1 = bounding_box

    dx = x1 - x0
    dy = dx / 10

    dy_mm = d_mm
    dx_mm = 0.5 * d_mm
    if isinstance(canvas_unit, CanvasUnitLinked):
        dy_m = canvas_unit.mm_to_m_vertical(dy_mm)
        dx_m = canvas_unit.mm_to_m_horizontal(dx_mm)
    else:
        dy_m = dy_mm
        dx_m = dx_mm
        dy = dx

    y0_ = y0 - dy

    y = y0_ - y0_ % dy_m
    x = x0 - x0 % dx_m
    if (x // dx_m) % 2:
        x += dx_m

    # print (x % (2 * dx_m))
    line_type_flag = True
    if (x // dx_m) % 4:
        line_type_flag = False
    # print((x // dx_m) % 4)

    x_left, x_right = x - 50 * dx, x + 50 * dx
    while y - 50 * dy < y1:
        y_bottom, y_top = y - 50 * dy, y + 50 * dy

        line = ((x_left, y_bottom), (x_right, y_top))
        y += dy_m
        # print(f"{y=}, {dy_m=} {y%(2*dy_m)=}")

        if alter_linetype:
            line_type_flag = not line_type_flag
            line_type = LineType.DASH if line_type_flag else LineType.SOLID
        else:
            line_type = linetype or LineType.SOLID

        if isinstance(canvas_unit, CanvasUnitLinked):
            canvas_unit.draw_lines_m_inside_polygon(
                polygon=polygon, points=line, width=0.1, line_type=line_type, color=color
            )
        else:
            canvas_unit.draw_lines_inside_polygon(
                polygon=polygon, points=line, width=0.1, line_type=line_type, color=color
            )


def fill_polygon_with_shapes(canvas_unit, polygon, bounding_box, dip_function, shape, color=None, scale=1, offset_factor=1):
    """Draws shape withing layer polygon."""
    x0, x1, y0, y1 = bounding_box
    if isinstance(canvas_unit, CanvasUnitLinked):
        dx_m = canvas_unit.mm_to_m_horizontal(shape.dx_mm)
        dy_m = canvas_unit.mm_to_m_vertical(shape.dy_mm)
    else:
        dx_m = shape.dx_mm
        dy_m = shape.dy_mm

    dx_m *= scale * offset_factor
    dy_m *= scale * offset_factor

    y0 = y0 - y0 % (2 * dy_m)
    x0 = x0 - x0 % dx_m

    y = y0
    shift_x = False
    while y < y1 + dy_m:

        x = x0
        if shift_x:
            x += 0.5 * dx_m
        shift_x = not shift_x

        while x < x1 + dx_m:
            dip = dip_function((x, y)) or 0
            angle = math.degrees(math.atan(dip * 10))
            shape.draw((x, y), angle, canvas_unit, polygon, color, scale=scale)
            x += dx_m

        y += dy_m


def fill_polygon_with_curved_lines(self, layer):
    """Fills polygon with curved lines."""
    x0, _, y0, y1 = layer.bounding_box
    dx_m = self.mm_to_m_horizontal(3)
    dy_m = self.mm_to_m_vertical(3)
    y0 = y0 - y0 % (2 * dy_m)
    x0 = x0 - x0 % dx_m

    points = list(layer.bottom)
    y = y0
    while y < y1 + dy_m:
        self.draw_lines_m_inside_polygon(layer.polygon, points, width=0.1, line_type=LineType.DASH)
        y += dy_m
        points = [(x, y_ + dy_m) for x, y_ in points]
