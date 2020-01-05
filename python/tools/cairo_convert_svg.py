#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A script used to convert notes in SVG to PNG, with out without an alpha channel.
It needs the Cairo Library and the CairoSVG python binding to run the first part.
It needs pillow to run the second part.
@author: jmmelko
"""
import os
import re

try:
    from cairosvg import svg2png

    iscairo = True
except:
    iscairo = False
from PIL import Image

transparency = True  # If yes, then PNG have an alpha channel
max_num_notes = 7  # Maximum number of note images in triplets and quavers, starting from 1

os.chdir("../../elements")

if iscairo:
    for file_path in os.listdir():
        (name, ext) = os.path.splitext(file_path)
        if ext == '.svg':
            if name in ['circle-highlighted-n', 'diamond-highlighted-n', 'root-highlighted-n']:
                for i in range(1, max_num_notes + 1):
                    new_name = re.sub('-n', '-' + str(i), name)
                    new_file = open(new_name + ext, 'w+', encoding='utf-8', errors='ignore')
                    for line in open(file_path, 'r', encoding='utf-8', errors='ignore'):
                        new_file.write(re.sub('highlighted-n', 'highlighted-' + str(i), line))
                    new_file.close()
                    svg2png(url=(new_name + ext), write_to=(new_name + '.png'))
            else:
                svg2png(url=file_path, write_to=(name + '.png'))

for file_path in os.listdir():
    (name, ext) = os.path.splitext(file_path)
    if ext == '.png':
        im = Image.open(file_path)
        if transparency:
            im = im.convert('RGBA')
        else:
            im = im.convert('RGB')
        im.save(file_path, dpi=(96, 96), compress_level=0)
