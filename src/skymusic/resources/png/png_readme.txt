This folder contains files for PNG output:

* PNG elements that will be opened and merged by the PNG renderer. They are sorted in a separate directory according to each color theme (light, dark, etc,). The names of these files must not be changed as they are hard-coded in the PNG renderers classes in files png_ir.py, png_nr.py, png_sr.py

A .__init__.py file is necessary in the theme directories as well as in the platforms sub-directories as the folders will be imported as modules by the PNG renderer.

* the original SVG files that were used to generate the PNGs, in the 'svg' sub-directory. They use style sheets named svg.css and svg2png.css, via an @import command. For each color theme, these sheets must be temporarily placed in the same folder. The script doing the conversion is in ../../skymusic/tools/svg_to_png.py. Again, the names must not be changed as they are called by the script and also determine the name of the png file. The svg directory is not imported by the program and only used in the development phase.

Note:
The 'root-highlighted-n.svg' file is a bit special since it does not correspond as such to any note. It is used by 'svg_to_png.py'
to create several files in a batch: 'root-highlighted-1.svg', ''root-highlighted-2.svg', etc, that will be used for rendering quavers.
