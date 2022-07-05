"""Модуль отвечающий непосредственно за холст на котором рисуется разрез."""

import os
from enum import Enum

import pyclipper

from .logger import logger

from .exceptions import CanvasException
from .dxf import CanvasDxf
from .pdf_via_cairo import CanvasCairo
from .png import CanvasPng

# flake8: noqa
from .backend import Backend, LineType, Color, TextAligment  # pylint: disable=unused-import
from .paper_sizes import SIZES


class OutputType(str, Enum):
    dxf = "dxf"
    pdf = "pdf"
    png = "png"


BACKENDS = {
    OutputType.dxf: CanvasDxf,
    OutputType.pdf: CanvasCairo,
    OutputType.png: CanvasPng,
}


def clip_lines_with_polygon(func):
    """Function wrapper for draw lines.

    Clips all lines inside given polygon and draws only those lines that are inside this polygon.
    """

    def wrapper(canvas, polygon, points, **kwargs):
        # scale_up points from float to int that is needed for coorect work of pyclipper
        points = pyclipper.scale_to_clipper(points)
        polygon = pyclipper.scale_to_clipper(polygon)

        # clip line given by points
        clipper = pyclipper.Pyclipper()
        clipper.AddPath(polygon, pyclipper.PT_CLIP)
        clipper.AddPath(points, pyclipper.PT_SUBJECT, False)

        solution = clipper.Execute2(pyclipper.CT_INTERSECTION)
        solution = pyclipper.PolyTreeToPaths(solution)
        solution = pyclipper.scale_from_clipper(solution)

        for line in solution:
            func(canvas, polygon, line, **kwargs)

    return wrapper


class Canvas:
    """Canvas for simple drawings without subplot and so on."""

    _width_in_mm = None
    _height_in_mm = None

    def __init__(self, page, output_file, output_type: OutputType = OutputType.png):
        self.page = page
        self.units = dict()
        self.backend = BACKENDS[output_type](output_file)

    @property
    def width_in_mm(self):
        """Width of the page in mm."""
        if self._width_in_mm:
            return self._width_in_mm
        return SIZES[self.page][0]

    @property
    def height_in_mm(self):
        """Height of the page in mm."""
        if self._height_in_mm:
            return self._height_in_mm
        return SIZES[self.page][1]

    @clip_lines_with_polygon
    def draw_lines_inside_polygon(self, polygon, points, **kwargs):
        """Draw line inside given polygon."""
        # pylint: disable=unused-argument
        self.draw_lines_canvas_mm(points, **kwargs)

    def add(self, unit, name=None):
        """Добавляет на разрез элемент разреза (CanvasUnit)."""

        unit_name = name or unit.name
        while True:
            if unit_name not in self.units:
                break
            unit_name = unit_name + "+"

        self.units[unit_name] = unit
        unit.canvas = self
        unit.__post_add__()

    def add_layer(self, layer_name, **kwargs):
        """Adds a new layer."""
        self.backend.add_layer(layer_name=layer_name, **kwargs)

    def draw_line_canvas_mm(self, point0, point1, **kwargs):
        """Draws line on canvas in coordinates given in mm.

        Coordinates starts from bottom left part of the canvas.
        """
        self.backend.draw_lines([point0, point1], **kwargs)

    def draw_lines_canvas_mm(self, points, **kwargs):
        """Draws line on canvas in coordinates given in mm.

        Coordinates starts from bottom left part of the canvas.
        """
        self.backend.draw_lines(points, **kwargs)

    def draw_text_canvas_mm(self, x, y, text, **kwargs):
        """Draws text on canvas with coordinates given in mm."""
        self.backend.draw_text((x, y), text, **kwargs)

    def draw_rectangle_canvas_mm(self, point0, size, **kwargs):
        """Draws rectangle on canvas with coordinates given in mm."""
        self.backend.draw_rectangle(point0, size, **kwargs)

    def draw_circle_canvas_mm(self, center, radius, **kwargs):
        """Draws a circle on canvas with coordinates given in mm."""
        self.backend.draw_circle(center=center, radius=radius, **kwargs)

    def draw_table_canvas_mm(self, origin, table, **kwargs):
        """Draws table on canvas with coordinates given in mm."""
        dimention = len(table), len(table[0])
        self.backend.draw_table(origin=origin, dimensions=dimention, values=table, **kwargs)

    def draw_units(self):
        """Draws all units in self using self backend."""

        # pylint: disable=bare-except
        # pylint: disable=W0703

        self.backend.widht_in_mm = self.width_in_mm
        self.backend.width_in_mm = self.width_in_mm
        self.backend.height_in_mm = self.height_in_mm
        self.backend.__pre_draw__()

        for _, unit in self.units.items():
            try:
                logger.info(f'Обработка элемента разреза "{unit.name}"')
                unit.__draw__()
            except CanvasException as exception:
                logger.exception(exception)
                logger.info(exception)
            except BaseException as e:
                print(e)
                raise
                # logger.exception(f"Ошибка при построении разреза {unit.name}")
                # logger.info(f"Ошибка при построении элемента разреза {unit.name}")
                # logger.info("Элемент не будет построен на разрезе")

    def place_units(self):
        """Call __place__ for each unit."""

        for _, unit in self.units.items():
            unit.__place__(self)
            # print(unit)

    def draw(self):
        """Draw everything and saves to file."""

        self.place_units()
        self.draw_units()
        self.save_to_file()

    def save_to_file(self):
        """Saves drawing to a file."""

        self.backend.save_to_file()
