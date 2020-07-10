#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A script used to convert notes in SVG to PNG, with out without an alpha channel.
It needs the Cairo Library and the CairoSVG python binding to run the first part.
It needs pillow to run the second part.
@author: jmmelko
"""
import os, re, shutil

try:
    from cairosvg import svg2png
    iscairo = True
except:
    iscairo = False
from PIL import Image

transparency = True  # If yes, then PNG have an alpha channel
max_num_notes = 7  # Maximum number of note images in triplets and quavers, starting from 1
quavers_overwrite = False # Force creation of xxx-highlighted-1 files

base_css_name = 'base.css'
theme_css_name = 'theme.css'
themes_dir = "../resources/elements"
main_css_path = '../resources/css/svg.css'
svg_dir = "../resources/elements/svgs"
generic_quaver_names = ['circle-highlighted-n', 'diamond-highlighted-n', 'root-highlighted-n']
generic_quaver_class = 'highlighted-n'

def get_svg_paths(svg_dir, exclude=[]):
    '''
    Get SVG file paths to convert
    '''
    svg_paths = []
    for (dirpath, dirnames, filenames) in os.walk(svg_dir):
        for filename in filenames:
            (basename, ext) = os.path.splitext(filename)
            if ext.lower() == '.svg' and basename not in exclude:
                svg_paths.append(os.path.join(dirpath, filename))

    return svg_paths


def get_theme_css(themes_dir):
    '''
    Get themes directories
    A theme directory must contain at least one .css file
    '''
    css_paths = []
    for (dirpath, dirnames, filenames) in os.walk(themes_dir):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() == '.css':
                css_paths.append(os.path.join(dirpath, filename))
                break
    return css_paths

def create_quavers_svgs(svg_paths, max_num_notes=7, quavers_overwrite=False):
    '''
    Creates SVG file for quavers
    '''
    
    wrote_svg = 0
    
    for svg_path in svg_paths:
        (basepath, filename) = os.path.split(svg_path)
        (basename, ext) = os.path.split(filename)
        
        if basename in generic_quaver_names:
            for i in range(1, max_num_notes + 1):
            
                new_basename = re.sub('-n', f'-{i}', basename)
                new_path = os.path.join(basepath, new_basename + ext)
                new_quaver_class = re.sub('-n', f'-{i}', generic_quaver_class)
                
                if not os.path.isfile(new_path) or quavers_overwrite:
                    new_file = open(new_path, 'w+', encoding='utf-8', errors='ignore')
                    for line in open(svg_path, 'r', encoding='utf-8', errors='ignore'):
                        new_file.write(re.sub(generic_quaver_class, new_quaver_class, line))
                    new_file.close()
                    wrote_svg += 1
                    
    return wrote_svg    

def convert_svg_to_png(svg_paths, css_path, main_css_path=None, exclude=[]):
    
    global base_css_name, theme_css_name
    
    (css_dir, css_filename) = os.path.split(css_path)
    (css_basename, css_ext) = os.path.splitext(css_filename)
    (svg_dir, _) = os.path.split(svg_paths[0])
    
    if main_css_path:
        shutil.copyfile(main_css_path, os.path.join(svg_dir, base_css_name))
    shutil.copyfile(css_path, os.path.join(svg_dir, theme_css_name))

    converted = 0
    for svg_path in svg_paths:

        (svg_dir, svg_filename) = os.path.split(svg_path)
        (svg_basename, svg_ext) = os.path.splitext(svg_filename)

        if svg_basename not in exclude:

            if iscairo:
                svg2png(url=svg_path, write_to=os.path.join(css_dir, svg_basename+'.png'))
            else:
                print(f'Simulating svg2png conversion to {svg_basename}.png')
            converted += 1
            
    #Removed copied css files       
    try:
        if main_css_path:
            os.remove(os.path.join(svg_dir, base_css_name))
        os.remove(os.path.join(svg_dir, the))
    except FileNotFoundError as err:
        print(err)
        
    return converted

'''
for file_path in filepaths:
    (name, ext) = os.path.splitext(file_path)
    if ext == '.png':
        im = Image.open(file_path)
        if transparency:
            im = im.convert('RGBA')
        else:
            im = im.convert('RGB')
        im.save(file_path, dpi=(96, 96), compress_level=0)
'''

if __name__ == '__main__':
    
    svg_paths = get_svg_paths(svg_dir)
    
    wrote_svg = create_quavers_svgs(svg_paths, max_num_notes, quavers_overwrite)
    if wrote_svg:
        print(f"\n=== Created {wrote_svg} quavers svg files ===")
        
    svg_paths = get_svg_paths(svg_dir, exclude=generic_quaver_names)
    print(f"\n=== Found {str(len(svg_paths))} SVG files to convert: ===")
    print([os.path.split(svg_path)[1] for svg_path in svg_paths])
    
    css_paths = get_theme_css(themes_dir)
    themes_names = [os.path.split(os.path.split(css_path)[0])[-1] for css_path in css_paths]
    print(f"\n=== Found the following themes directories with a CSS file: ===")
    print(themes_names)
    print('\n')
    
    for theme_name, css_path in zip(themes_names, css_paths):
        converted = convert_svg_to_png(svg_paths, css_path, main_css_path, generic_quaver_names)
        print(f"\n==> Converted {converted} PNGs for theme '{theme_name}'\n")
