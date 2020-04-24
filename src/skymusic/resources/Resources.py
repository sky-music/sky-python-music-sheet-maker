import io
from importlib import resources as importlib_resources
from src.skymusic.resources import fonts, elements, css


A_root_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-circle.png'))
A_diamond_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-diamond.png'))
A_circle_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-circle.png'))
B_root_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-root.png'))
B_diamond_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-diamond.png'))
B_circle_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-circle.png'))
C_root_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-root.png'))
C_diamond_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-diamond.png'))
C_circle_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-circle.png'))
dead_png = io.BytesIO(importlib_resources.read_binary(elements, 'dead-note.png'))
A_unhighlighted_png = io.BytesIO(importlib_resources.read_binary(elements, 'A-unhighlighted.png'))   
B_unhighlighted_png = io.BytesIO(importlib_resources.read_binary(elements, 'B-unhighlighted.png'))   
C_unhighlighted_png = io.BytesIO(importlib_resources.read_binary(elements, 'C-unhighlighted.png'))
root_highlighted_pngs = [io.BytesIO(importlib_resources.read_binary(elements, 'root-highlighted-' + str(i) + '.png')) for i in range(1, 8)]
diamond_highlighted_pngs = [io.BytesIO(importlib_resources.read_binary(elements, 'diamond-highlighted-' + str(i) + '.png')) for i in range(1, 8)]
circle_highlighted_pngs = [io.BytesIO(importlib_resources.read_binary(elements, 'circle-highlighted-' + str(i) + '.png')) for i in range(1, 8)]

empty_chord_png = io.BytesIO(importlib_resources.read_binary(elements, 'empty-chord.png'))  # blank harp
unhighlighted_chord_png = io.BytesIO(importlib_resources.read_binary(elements, 'unhighlighted-chord.png'))  # harp with unhighlighted notes
broken_png = io.BytesIO(importlib_resources.read_binary(elements, 'broken-symbol.png'))
silent_png = io.BytesIO(importlib_resources.read_binary(elements, 'silent-symbol.png'))

with importlib_resources.path(css, 'main.css') as fp:
    css_path = str(fp)

with importlib_resources.path(fonts, 'NotoSansCJKjp-Regular.otf') as fp:
    font_path = str(fp)