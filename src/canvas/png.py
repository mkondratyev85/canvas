"""Module for Canvas backend that plots png as a result."""

import os

import cairo

from .pdf_via_cairo import CanvasCairo

watermark_cmd = """ \( -size 250x -background none -fill gray -gravity center \
label:"talveg.ru" -trim -rotate -30 \
-bordercolor none -border 50 \
-write mpr:wm +delete \
+clone -fill mpr:wm  -draw 'color 0,0 reset' \) \
-compose over -composite \
"""


class CanvasPng(CanvasCairo):
    def get_surface(self):
        return cairo.ImageSurface(cairo.FORMAT_ARGB32, int(self.width), int(self.height))

    def save_to_file(self):
        self.surface.write_to_png(self.imagefile)
        super().save_to_file()

        pdf_file = self.imagefile
        png_file = f"{pdf_file[:-3]}png"
        output_file = f"{pdf_file[:-4]}"

        os.system(f"convert {pdf_file} -flatten -fuzz 1% -trim +repage {watermark_cmd} {png_file}")
        os.system(f"mv {png_file} {output_file}")
