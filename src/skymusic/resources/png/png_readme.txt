This folder contains:

* PNG elements that will be opened and merged by the PNG renderer. They are sorted in a separate directory according to each color theme (light, dark, etc,) and each gaming platform (mobile, playstation, etc). The names of these files must not be changed as they are hard-coded in the PNG renderers classes in png_ir.py, png_nr.py, and png_sr.py

A .__init__.py file is necessary in the theme directories as well as in the platforms sub-directories as the folders will be imported as modules by the PNG renderer.



