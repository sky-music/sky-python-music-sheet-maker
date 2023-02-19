This directory contains the original SVG files used to generate PNG elements via a python script based on Pillow.
They are not standalone and require a theme-specific file called svg2png.css to be placed in the same directory (manualy or bu a scropt whenever necessary). The sheet content is imported via an @import url command.

These files are also used to generate the SVG symbols for the SVG template used by the svg renderer, as well as the background-images symbols included in the HTML files. In this case the class attributes are programmaticaly replaced by inline CSS styling.

A __init__.py file is not necessary here as the folders are *not* imported by the main program. They are used only in the development phase to generate PNGs. The script doing the conversion is in ../../skymusic/tools/svg_to_png.py

Note:
The 'root-highlighted-n.svg' file is a bit special since it does not correspond as such to any note. It is used by 'svg_to_png.py'
to create several files in a batch: 'root-highlighted-1.svg', ''root-highlighted-2.svg', etc, that will be used for rendering quavers.
