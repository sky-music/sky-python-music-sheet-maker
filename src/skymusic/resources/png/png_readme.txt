This folder contains files for PNG output:

* the original SVG files, in the 'svg' sub-directory, that use the style sheets placed in ../css/{theme}/, via an @import command, namely svg.css and common.css.
* the converted PNG files, for each theme, using the script in ../python/tools/svg_to_png.py.

The 'root-highlighted-n.svg' file is a bit special since it does not correspond as such to any note. It is used by 'svg_to_png.py'
to create several files in a batch: 'root-highlighted-1.svg', ''root-highlighted-2.svg', etc, that will be used for rendering quavers.
