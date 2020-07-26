Cascading Style Sheets are essential to the Music Sheet Maker program, for:
* HTML output
* SVG output
* building the PNG elements

This folder should NOT be tempered with or moved.

The CSS folder contains a subfolder for each color theme used in the program.
Each theme folder contains all the necessary CSS files for this theme. Currently, they are:
* html.css
* svg.css
* common.css

Each folder must contain a __init__.py file because they are imported as modules.

The only reason for which an advanced user may want to modify these CSS is to change colors, font size, or the note size in html or svg output.
For the latter they have 2 options:

1) Change the 'font-size' value of the 'body' element. This will resize *all* the elements in the page.
2) Change the 'font-size' value of the 'td' element. This will resize notes without affecting text.
