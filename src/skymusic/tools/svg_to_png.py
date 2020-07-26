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
quavers_overwrite = False # Force creation of circle-highlighted-1.svg type files

include_css = ['common.css', 'svg.css'] #css files to copy inside the svg directory before converting to PNG
css_dir = "../resources/css"
svg_dir = "../resources/png/svg"
png_dir = "../resources/png"
generic_quaver_names = ['circle-highlighted-n', 'diamond-highlighted-n', 'root-highlighted-n']
generic_quaver_class = 'ON-n'

def get_svg_paths(svg_dir, exclude_svg=[]):
    '''
    Get SVG file paths to convert
    Should be all the .svg files in svg_dir
    '''
    svg_paths = []
    for (dirpath, dirnames, filenames) in os.walk(svg_dir):
        for filename in filenames:
            (basename, ext) = os.path.splitext(filename)
            if ext.lower() == '.svg' and basename not in exclude_svg:
                svg_paths.append(os.path.join(dirpath, filename))

    return svg_paths


def get_theme_css(css_dir, include=[]):
    '''
    Returns a dictionary of themes where the values are links to the css files of this theme
    A theme directory must contain at least one .css file
    '''
    css_paths = {}
    for (dirpath, dirnames, filenames) in os.walk(css_dir):

        for filename in filenames:
            if filename.lower() in include or include == []:
                
                (k, path) = (os.path.split(dirpath)[-1], os.path.join(dirpath, filename))
                try:
                    css_paths[k] += [path]
                except KeyError:
                    css_paths[k] = [path]
                
    return css_paths

def create_quavers_svgs(svg_paths, max_num_notes=7, quavers_overwrite=False):
    '''
    Creates SVG file for quavers
    '''    
    wrote_svg = 0
    
    for svg_path in svg_paths:
        (basepath, filename) = os.path.split(svg_path)
        (basename, ext) = os.path.splitext(filename)
        
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

def convert_svg_to_png(svg_paths, exclude_svg=[], css_paths=[], png_dir=png_dir):
    '''
    For a fixed theme:
    - copies the css files pointed by css_paths in the directory of svg_paths[0]
    - converts all the SVG files in svg_paths to PNGs
    - saves the PNGs in png_dir
    - SVG files listed in exclude_svg are not converted
    '''
    (svg_dir, _) = os.path.split(svg_paths[0])
    
    copied_css_files = []
    for css_path in css_paths:
        (css_dir, css_filename) = os.path.split(css_path)
        copy_path = os.path.join(svg_dir, css_filename)
        #(css_basename, css_ext) = os.path.splitext(css_filename)
        copied_css_files.append(copy_path)
        shutil.copyfile(css_path, copy_path)

    png_paths = []
    for svg_path in svg_paths:

        (svg_dir, svg_filename) = os.path.split(svg_path)
        (svg_basename, svg_ext) = os.path.splitext(svg_filename)

        if svg_basename not in exclude_svg:
            png_path = os.path.join(png_dir, svg_basename+'.png')
            if iscairo:
                svg2png(url=svg_path, write_to=png_path)
            else:
                print(f"Simulating conversion to '{svg_basename}.png'")
            png_paths.append(png_path)
            
    #Removed copied css files       
    for copy_path in copied_css_files:
        os.remove(copy_path)
        
    return png_paths

def set_transparency(png_paths, transparency):
    '''
    Sets the transparency of the given PNGs
    '''
    for png_path in png_paths:
        (basename, ext) = os.path.splitext(png_path)
        if ext == '.png':
            im = Image.open(png_path)
            if transparency:
                im = im.convert('RGBA')
            else:
                im = im.convert('RGB')
            im.save(png_path, dpi=(96, 96), compress_level=0)


if __name__ == '__main__':
    
    # Gets the SVGs files
    svg_paths = get_svg_paths(svg_dir)
    
    # Create SVGs for quavers based on generic SVG files
    wrote_svg = create_quavers_svgs(svg_paths, max_num_notes, quavers_overwrite)
    print(f"\n=== Created {wrote_svg} quavers svg files ===")
    
    # Gets the SVG files again after creating the quavers
    svg_paths = get_svg_paths(svg_dir, exclude_svg=generic_quaver_names)
    print(f"\n=== Found {str(len(svg_paths))} SVG files to convert: ===")
    print([os.path.split(svg_path)[1] for svg_path in svg_paths])
    
    # Gets installed themes
    # Returns a dictionary of themes names with links to associated css files
    theme_css = get_theme_css(css_dir, include=include_css)
    
    print(f"\n=== Found the following themes  with a valid CSS file: ===")
    print(theme_css)
    print('\n')
    
    # Creates PNGs theme by theme
    theme_png = {}
    for theme in theme_css:
        theme_png_dir = os.path.join(png_dir, theme)
        theme_png[theme] = convert_svg_to_png(svg_paths=svg_paths, exclude_svg=generic_quaver_names, css_paths=theme_css[theme], png_dir=theme_png_dir)
        print(f"\n==> Converted {len(theme_png[theme])} PNGs for theme '{theme}'\n")

    # Sets the transparency for all created PNGs
    for theme in theme_png:
        if iscairo:
            set_transparency(theme_png[theme], transparency)
        print(f"Transparency set for {len(theme_png[theme])} PNGs in theme '{theme}'.")

