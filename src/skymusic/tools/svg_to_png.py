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

SIMULATE = False

EMBED_CSS = True #To circumvent a bug of CairoSVG not supporting @import directives

transparency = True  # If yes, then PNG have an alpha channel
max_num_notes = 7  # Maximum number of note images in triplets and quavers, starting from 1
quavers_overwrite = False # Force creation of circle-highlighted-1.svg type files

include_css = ['svg2png.css', 'svg.css'] #css files to copy inside the svg directory before converting to PNG
css_dir = "../resources/css" #css files are inside theme folders, e.g. resources/png/dark/common.css
svg_dir = "../resources/png/svg"
png_dir = "../resources/png"
generic_quaver_names = ['circle-highlighted-n', 'diamond-highlighted-n', 'root-highlighted-n']  #According to the CSS definitions
generic_quaver_class = 'ON-n' #According to the CSS definitions
exclude_platforms = ['mobile']

def get_svg_paths(svg_dir, exclude_svg=[], exclude_platforms=[]):
    '''
    Get SVG file paths to convert
    Returns a dictionary with keys being the platform names
    Should be all the .svg files in svg_dir
    '''
    svg_paths = {}
    for (dirpath, dirnames, filenames) in os.walk(svg_dir):
        for filename in filenames:
            (basefilename, ext) = os.path.splitext(filename)
            if ext.lower() == '.svg' and basefilename not in exclude_svg: # Valid SVG file
                platform = os.path.basename(dirpath) #Sort by platform
                if platform not in exclude_platforms:
                    svg_paths[platform] = svg_paths.get(platform,[]) + [os.path.join(dirpath, filename)]

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

def create_quavers_svgs(svg_paths, exclude_platforms=[], max_num_notes=7, quavers_overwrite=False):
    '''
    Creates SVG file for quavers
    '''    
    wrote_svg = 0
    skipped_svg = 0
    
    for platform in [plat for plat in svg_paths if plat not in exclude_platforms]:
        for svg_path in svg_paths[platform]:
            (basepath, filename) = os.path.split(svg_path)
            (basefilename, ext) = os.path.splitext(filename)
            
            if basefilename in generic_quaver_names:
                for i in range(1, max_num_notes + 1):
                
                    new_basefilename = re.sub('-n', f'-{i}', basefilename)
                    new_path = os.path.join(basepath, new_basefilename + ext)
                    new_quaver_class = re.sub('-n', f'-{i}', generic_quaver_class)
                    
                    if not os.path.isfile(new_path) or quavers_overwrite:
                        if not SIMULATE:
                            with open(new_path, 'w+', encoding='utf-8', errors='ignore') as new_file:
                                for line in open(svg_path, 'r', encoding='utf-8', errors='ignore'):
                                    new_file.write(re.sub(generic_quaver_class, new_quaver_class, line))
                        else:
                            assert os.path.isfile(svg_path)
                            print(f"Simulating writing of:\n'{svg_path}' to '{new_path}'\n     with substitution {generic_quaver_class}->{new_quaver_class}")
                        wrote_svg += 1
                    else:
                        skipped_svg += 1
                    
    return wrote_svg, skipped_svg    


def force_embed_styles(svg_path, css_paths, strip_css_dir=True):

    (svg_dir, svg_filename) = os.path.split(svg_path)
    (svg_basename, svg_ext) = os.path.splitext(svg_filename)

    outfilename = svg_basename + '_embed' + svg_ext
    outpath = os.path.join(svg_dir, outfilename)
    
    with open(svg_path, 'r+') as svg_fp:
        
        svg_content = svg_fp.read()
        
        for css_path in css_paths:
            if strip_css_dir:
                (_, css_uri) = os.path.split(css_path)
            else:
                css_uri = css_path
        
            with open(css_path, 'r+') as css_fp:
                css_content = css_fp.read()
                css_content = "\n" + css_content + "\n"
        
            
            regexp = re.compile(r"@import\s*url\(*\s*['\"]{1}%s['\"]{1}\s*\)*\s*[;]*" % re.escape(css_uri))
            
            (svg_content, numrepl) = regexp.subn(css_content, svg_content)

            if re.search('CDATA', svg_content) is None and numrepl > 0:
                # add CDATA tags for more safety
                svg_content = re.sub(r'(<\s*style[^>]*>)', '\g<1>'+'<![CDATA[', svg_content, re.IGNORECASE)
                svg_content = re.sub(r'(<\s*/\s*style[^>]*>)', ']]>' + '\g<1>', svg_content, re.IGNORECASE)

    
        with open(outpath, 'w+') as fpout:
            fpout.write(svg_content)
    
    
    return outpath
    


def convert_svg_to_png(svg_paths, exclude_svg=[], exclude_platforms=[], css_paths=[], png_dir=png_dir):
    '''
    For a fixed theme:
    - copies the css files pointed by css_paths in the directory of svg_paths[0]
    - converts all the SVG files in svg_paths to PNGs
    - saves the PNGs in png_dir
    - SVG files listed in exclude_svg are not converted
    '''
    png_paths = {}
    
    for platform in [plat for plat in svg_paths if plat not in exclude_platforms]:
        
        (svg_dir, _) = os.path.split(svg_paths[platform][0])
        
        copied_css_files = []
        for css_path in css_paths:
            (css_dir, css_filename) = os.path.split(css_path)
            copy_path = os.path.join(svg_dir, css_filename)
            #(css_basename, css_ext) = os.path.splitext(css_filename)
            copied_css_files.append(copy_path)
            if not SIMULATE:
                pass
                shutil.copyfile(css_path, copy_path)
            else:
                assert os.path.isfile(css_path)
                common_path = os.path.commonpath([css_path, copy_path])
                print(f"Simulated CSS copy: '{css_path.replace(common_path,'')}' -> '{copy_path.replace(common_path,'')}'")
    
        for svg_path in svg_paths[platform]:
    
            (svg_dir, svg_filename) = os.path.split(svg_path)
            (svg_basename, svg_ext) = os.path.splitext(svg_filename)
    
            if svg_basename not in exclude_svg:
                png_path = os.path.join(png_dir, platform, svg_basename+'.png')
                if iscairo and not SIMULATE:
                    if EMBED_CSS: svg_path = force_embed_styles(svg_path=svg_path, css_paths=css_paths)
                    svg2png(url=svg_path, write_to=png_path)
                    if EMBED_CSS: os.remove(svg_path)
                else:
                    assert os.path.isfile(svg_path)
                    common_path = os.path.commonpath([svg_path, png_path])
                    print(f"Simulated conversion: '{svg_path.replace(common_path,'')}' -> '{png_path.replace(common_path,'')}'")
                
                png_paths[platform] = png_paths.get(platform,[]) + [png_path]
                
        #Removed copied css files       
        for copy_path in copied_css_files:
            if not SIMULATE:
                pass
                os.remove(copy_path)
            else:
                print(f"Simulated CSS removal: '{copy_path}'")
            
    return png_paths

def set_transparency(png_paths, transparency):
    '''
    Sets the transparency of the given PNGs
    '''
    files_set = 0
    for platform in png_paths:
        for png_path in png_paths[platform]:
            (basename, ext) = os.path.splitext(png_path)
            if ext == '.png':
                if not SIMULATE:
                    im = Image.open(png_path)
                    if transparency:
                        im = im.convert('RGBA')
                    else:
                        im = im.convert('RGB')
                    im.save(png_path, dpi=(96, 96), optimize=True)
            files_set += 1
            
    return files_set

if __name__ == '__main__':
    
    # Gets the SVGs files, as a dicitionary of file paths, sorted by platform
    svg_paths = get_svg_paths(svg_dir=svg_dir, exclude_platforms=exclude_platforms)
    if SIMULATE: assert svg_paths
    
    # Create SVGs for quavers based on generic SVG files
    wrote_svg, skipped_svg = create_quavers_svgs(svg_paths=svg_paths, exclude_platforms=exclude_platforms, max_num_notes=max_num_notes, quavers_overwrite=quavers_overwrite)
    print(f"\n=== Wrote {wrote_svg} quavers svg files / {skipped_svg} already existed ===")
    
    # Gets the SVG files again after creating the quavers
    svg_paths = get_svg_paths(svg_dir=svg_dir, exclude_platforms=exclude_platforms, exclude_svg=generic_quaver_names)
    print("\n======= Found SVG files to convert: =======")
    for platform in svg_paths:
        print(f"----- {platform}: {len(svg_paths[platform])} ------")
        print([os.path.split(svg_path)[1] for svg_path in svg_paths[platform]])
    
    
    # Gets installed themes
    # Returns a dictionary of themes names 0ith links to associated css files
    theme_css = get_theme_css(css_dir, include=include_css)
    if SIMULATE: assert theme_css
    
    print("\n=== Found the following themes with valid CSS file(s): ===")
    print(theme_css)
    print('\n')
    
    # Creates PNGs theme by theme
    png_theme_paths = {}
    for theme in theme_css:
        theme_png_dir = os.path.join(png_dir, theme)
        print(f"\n.... Processing theme '{theme}' in '{png_dir}' ....")
        png_theme_paths[theme] = convert_svg_to_png(svg_paths=svg_paths, exclude_platforms=exclude_platforms, exclude_svg=generic_quaver_names, css_paths=theme_css[theme], png_dir=theme_png_dir)
    print("\n=========== Converted PNGs:' =============")
    for theme in png_theme_paths:
        for platform in png_theme_paths[theme]:
            wrote_dir = os.path.dirname(png_theme_paths[theme][platform][0]) if png_theme_paths[theme][platform] else ''
            print(f"{theme+'/'+platform:20}: {len(png_theme_paths[theme][platform])} in {wrote_dir}")

    # Sets the transparency for all created PNGs
    print("")
    for theme in png_theme_paths:
        if iscairo:
            files_set = set_transparency(png_theme_paths[theme], transparency)
        else:
            files_set = []
        print(f"Transparency set for {files_set} PNGs in theme '{theme}'.")

