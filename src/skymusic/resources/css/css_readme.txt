Cascading Style Sheets are essential to the Music Sheet Maker program, for:
* HTMl output
* SVG output
* building the PNG elements

It should NOT be tempered with or moved.

The only reason for which an advanced user may want to modify these CSS is to change colors, font size, or the note size in html or svg output.
For the latter they have 2 options:

1) Change the 'font-size' value of the 'body' element. This will resize *all* the elements in the page.
2) Change the 'font-size' value of the 'td' element. This will resize notes without affecting text.
