
The SVG folder contains all the necessary SVG symbols that will be imported by the SVG song renderer through the load_svg_template() method. 
The files are organised in subfolders corresponding to color themes.
Currently, there is only template.svg

Each theme folder must contain a __init__.py file because they are imported as modules.

The only reason for which an advanced user may want to modify these SVG templates is to change colors, font size, or the note size in html or svg output.

(This directory must not be confused with the original directory that also SVG elememts used to generate PNG files)
