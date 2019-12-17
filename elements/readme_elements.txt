This folder contains files for PNG output:

* the original SVG files, using the style sheet in ../css/main.css (via an import command)
* the converted PNG files, using the script in ../python/tools/cairo_convert_svg.py

The 'root-highlighted-n.svg' file is a bit special since it does not correspond as such to any note. It is used by 'cairo_convert_svg.py'
to create several files in a batch: 'root-highlighted-1.svg', ''root-highlighted-2.svg', etc, that will be used for rendering quavers.
