This folder contains scripts for developers.

In particular it contains a script to build PNG icons from SVG files.
This will be useful in case the style of the music sheets is changed and the statics images of PNG and SVG need to be generates again.

transposition.py can be used by anybody to transpose notes (ie shift notes inside the chromatic music scale)

collect_classes lists the CSS classes actually used by the original elements

merge_svg generates symbols and url-encoded background images for the SVG and HTML renderers, respectively. The generates code has to be pasted inside the correspondingn .css files.

colormap_maker was used to generate the color suite of the quavers.
