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
CLEAN_TEMP_FILES = True

EMBED_CSS = False #To circumvent the stricter behavior of tinycss2 not supporting @import url('svg.css') with single quotes directives
CONVERT_HSL = True

transparency = True  # If yes, then PNG have an alpha channel
max_num_notes = 7  # mobile only: Maximum number of note images in triplets and quavers, starting from 1
quavers_overwrite = True # mobile only: Force creation of circle-highlighted-1.svg type files

platform_css = {'mobile': ['svg2png.css'], # A dictionary of used css, sorted by platform
               'playstation': ['svg2png.css'],
               'switch': ['svg2png.css']
               } #css files to copy inside the svg directory before converting to PNG
css_dir = "../resources/css" #css files are inside theme folders, e.g. resources/png/dark/common.css
svg_dir = "../resources/original"
png_dir = "../resources/png"
generic_quaver_names = ['circle-highlighted-n', 'diamond-highlighted-n', 'root-highlighted-n']  #mobile only: According to the CSS definitions
generic_quaver_class = 'ON-n' #According to the CSS definitions
exclude_platforms = [] #mobile, playstation, switch

def full_split(path):
    
    (dir, filename) = os.path.split(path)
    (basename, ext) = os.path.splitext(filename)
    return (dir, basename, ext)


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


def get_theme_css_paths(css_dir, platform_css={}):
    """
    Returns a dictionary of themes where the values are lists of full patjs to the css files of this theme
    css_dir: root directory to search
    platform_css: dictionary of css file names {platform: [css1, css2,...]}
    """
    css_paths = {}
    for (dirpath, dirnames, filenames) in os.walk(css_dir):

        for filename in filenames:
            if os.path.splitext(filename)[1] == '.css':
                for platform in platform_css:
                    if filename.lower() in platform_css[platform] or (not platform_css): #platform uses this css file
                        
                        (theme, css_path) = (os.path.split(dirpath)[-1], os.path.join(dirpath, filename))
                        
                        if theme not in css_paths: css_paths[theme] = dict()
                        if platform not in css_paths[theme]: css_paths[theme][platform] = list()
                        css_paths[theme][platform] += [css_path]

    return css_paths

def create_quavers_svgs(svg_paths, exclude_platforms=[], max_num_notes=7, quavers_overwrite=False):
    '''
    Creates SVG file for quavers
    '''    
    wrote_svg = 0
    skipped_svg = 0
    
    for platform in [plat for plat in svg_paths if plat not in exclude_platforms]:
        for svg_path in svg_paths[platform]:
            (basepath, basefilename, ext) = full_split(svg_path)
            
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
                            
                            if wrote_svg < 3:
                                print(f"Simulating writing quaver:\n'{svg_path}' to '{new_path}'\n with substitution {generic_quaver_class}->{new_quaver_class}")
                            else:
                                print('', end=f"\r+{wrote_svg-2} other files")
                        wrote_svg += 1
                    else:
                        skipped_svg += 1
                    
    return wrote_svg, skipped_svg    
    

def remove_comments(text):
    
    #Remove comments
    text = re.sub(r'<!--(.(?!-->))*.-->', '', text, flags=re.DOTALL)
    text = re.sub(r'/\*[^*]*\*/', '', text, flags=re.DOTALL)
    return text


def hsl_to_rgb(text):
    
    # Replaces hsl by RGB because tinycss2 does not support HSL yet
    hslreg = re.compile(r"hsl\(\s*(\d+)\s*%*,*\s*(\d+)\s*%*,*\s*(\d+)\s*%*,*\)")

    import colorsys
    def hsl2rgb(mo):
        h, s, l = (float(g) for g in mo.groups())
        r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
        return f"rgb({r*255:.0f},{g*255:.0f},{b*255:.0f})"

    mo = hslreg.search(text)
    if mo: text = hslreg.sub(hsl2rgb, text)

    return text
        

def correct_css_styles(svg_path, css_paths, remote_css_file=False, convert_hsl=True):

    if not EMBED_CSS and not CONVERT_HSL: return svg_path, css_paths

    if CONVERT_HSL:
        suffix = '_rgb'
    elif EMBED_CSS:
        suffix = '_embed'
    else:
        suffix = ''

    (svg_dir, svg_basename, svg_ext) = full_split(svg_path)
    out_svg_filename = svg_basename + suffix + svg_ext
    out_svg_path = os.path.join(svg_dir, out_svg_filename)
    
    out_css_paths = []

    num_embedded = 0
    num_fixed = 0
    
    with open(svg_path, 'r+') as svg_fp:
        
        svg_content = svg_fp.read()
        
        for css_path in css_paths:
            
            (css_dir, css_uri_basename, css_uri_ext) = full_split(css_path)
            if remote_css_file:
                css_uri = css_path
            else:
                css_uri = css_uri_basename + css_uri_ext
            
            #Regular expression for @import(...);
            importRegex = re.compile(r"@import\s*(?:url)*\(*\s*['\"]*%s['\"]*\s*\)*\s*;*" % re.escape(css_uri))     
                
            with open(css_path, 'r+') as css_fp:
                css_content = css_fp.read()
                css_content = remove_comments(css_content)
                if CONVERT_HSL: css_content = hsl_to_rgb(css_content)
            
            # ==========================
            # Replace @import command by css content
            if EMBED_CSS:
                (svg_content, numrepl) = importRegex.subn("\n" + css_content + "\n", svg_content)
                num_embedded += numrepl
    
                if re.search('CDATA', svg_content) is None and numrepl > 0:
                    # add CDATA tags for more safety
                    svg_content = re.sub(r'(<\s*style[^>]*>)', '\g<1>'+'<![CDATA[', svg_content, flags=re.IGNORECASE)
                    svg_content = re.sub(r'(<\s*/\s*style[^>]*>)', ']]>' + '\g<1>', svg_content, flags=re.IGNORECASE)
            # ========================
            
            # ======================
            # Creates a modified css file
            elif CONVERT_HSL:
          
                rgb_css_uri = css_uri_basename + '_rgb' + css_uri_ext
                if remote_css_file:
                    out_css_path = os.path.join(css_dir, rgb_css_uri)
                else:
                    out_css_path = os.path.join(svg_dir, rgb_css_uri)
                
                #replace css uri by new one in SVG file
                svg_content = importRegex.sub("@import url(" + rgb_css_uri + ");", svg_content)
            
                # Writes RGB CSS file
                with open(out_css_path, 'w+') as fpout: fpout.write(css_content)
                out_css_paths.append(out_css_path)
                num_fixed += 1
            else:
                # Do nothing, keep original css file path
                out_css_paths.append(css_path)
            if SIMULATE:
                assert os.path.isdir(svg_dir)
                assert os.path.isdir(css_dir)
            # =====================
           
            
        if EMBED_CSS and (num_embedded == 0):
            if re.search(r'import', svg_content):
                css_uris = [os.path.split(css_path)[1] for css_path in css_paths]
                print("*** WARNING: 0 replacements of " + ', '.join([f"@import url({css_uri})" for css_uri in css_uris]) + f" in {svg_path} ***")
    
        # Writes new svg file
        with open(out_svg_path, 'w+') as fpout: fpout.write(svg_content)
    
    
    return out_svg_path, out_css_paths
    


def convert_svg_to_png(svg_paths, exclude_svg=[], exclude_platforms=[], platform_css={}, png_dir=png_dir):
    """
    For a fixed theme:
    - copies the css files pointed by css_paths in the directory of svg_paths[0]
    - converts all the SVG files in svg_paths to PNGs
    - saves the PNGs in png_dir
    - SVG files listed in exclude_svg are not converted
    """
    png_paths = {}
    included_platforms = [plat for plat in svg_paths if plat not in exclude_platforms]
    
    for platform in included_platforms:
        
        (svg_dir, _) = os.path.split(svg_paths[platform][0])
        
        if platform not in platform_css: platform_css[platform] = list()
        copied_platform_css = dict().fromkeys(platform_css.keys(),[])
        fixed_platform_css = copied_platform_css.copy()
        
        for css_path in platform_css[platform]:
            (css_dir, css_filename) = os.path.split(css_path)
            copy_path = os.path.join(svg_dir, css_filename)
            
            if not SIMULATE:
                copied_platform_css[platform].append(copy_path)
                shutil.copyfile(css_path, copy_path)
            else:
                assert os.path.isfile(css_path)
                copied_platform_css[platform].append(css_path)
    
        if SIMULATE:
            common_path = os.path.commonpath([css_path, copy_path])
            simulated_paths = [(pth.replace(css_dir,svg_dir)).replace(common_path,'') for pth in copied_platform_css[platform]]
            print(f"\nSimulated CSS copies: {[pth.replace(common_path,'') for pth in platform_css[platform]]}-> {simulated_paths}")
    
        if SIMULATE: print("\n==== Simulated SVG 2 PNG conversions: ====")
        num_converted = 0
        for svg_path in svg_paths[platform]:
            
            (svg_dir, svg_basename, svg_ext) = full_split(svg_path)
            num_converted += 1
    
            if svg_basename not in exclude_svg:
                png_path = os.path.join(png_dir, platform, svg_basename+'.png')
                if EMBED_CSS or CONVERT_HSL: svg_path, fixed_platform_css[platform] = correct_css_styles(svg_path=svg_path, css_paths=copied_platform_css[platform])
                if iscairo and not SIMULATE:
                    svg2png(url=svg_path, write_to=png_path) #This where the work is done!
                else:
                    assert os.path.isfile(svg_path)
                    common_path = os.path.commonpath([svg_path, png_path])
                    
                    if num_converted < 3:
                        
                        if EMBED_CSS:
                            print(f"Embedding: '{[pth.replace(common_path,'') for pth in fixed_platform_css[platform]]}'")
                        elif CONVERT_HSL:
                            print(f"Creating: '{[pth.replace(common_path,'') for pth in fixed_platform_css[platform]]}'")
                        print(f"Converting: '{svg_path.replace(common_path,'')}' -> '{png_path.replace(common_path,'')}'")
                    else:
                        print('',end=f"\r+{num_converted-2} other files for {platform}")
                if EMBED_CSS or CONVERT_HSL:
                    if CLEAN_TEMP_FILES: os.remove(svg_path)
                
                png_paths[platform] = png_paths.get(platform,[]) + [png_path]
                
        #Removed copied css files
        if SIMULATE: print('\n')
        for css_path in copied_platform_css[platform]:
            if css_path not in platform_css[platform]:#by safety
                if not SIMULATE:
                    if CLEAN_TEMP_FILES: os.remove(css_path)
                else:
                    print(f"Simulated CSS removal: '{css_path}'")
        for fixed_css_path in fixed_platform_css[platform]:
            if fixed_css_path not in platform_css[platform]:#by safety
                if not SIMULATE:
                    if CLEAN_TEMP_FILES: os.remove(fixed_css_path)
                else:
                    print(f"Simulated CSS removal: '{fixed_css_path}'")
                
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
    print(f"\n===> Wrote {wrote_svg} quavers svg files / {skipped_svg} already existed")
    
    # Gets the SVG files again after creating the quavers
    svg_paths = get_svg_paths(svg_dir=svg_dir, exclude_platforms=exclude_platforms, exclude_svg=generic_quaver_names)
    print("\n======= Found SVG files to convert: =======")
    for platform in svg_paths:
        print(f"-------- {platform}: {len(svg_paths[platform])} ---------")
        print([os.path.split(svg_path)[1] for svg_path in svg_paths[platform]])
    
    
    # Gets installed themes
    # Returns a dictionary of themes names with links to associated css files
    theme_css = get_theme_css_paths(css_dir, platform_css=platform_css)
    if SIMULATE: assert theme_css
    
    print("\n=== Found the following themes with valid CSS file(s): ===")
    print(theme_css)
    
    # Creates PNGs theme by theme
    png_theme_paths = {}
    for theme in theme_css:
        theme_png_dir = os.path.join(png_dir, theme)
        print(f"\n.... Processing theme '{theme}' in '{png_dir}' ....")
        png_theme_paths[theme] = convert_svg_to_png(svg_paths=svg_paths, exclude_platforms=exclude_platforms, exclude_svg=generic_quaver_names, platform_css=theme_css[theme], png_dir=theme_png_dir)
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
            files_set = 0
        print(f"Transparency set for {files_set} PNGs in theme '{theme}'{'(cairo is not installed)' if not iscairo else ''}.")

    if exclude_platforms:
        print("\n========= Excluded platforms: ========")
        print(str(exclude_platforms))
        
        
