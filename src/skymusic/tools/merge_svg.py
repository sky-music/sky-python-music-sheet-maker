#!/usr/bin/env python3
"""
A script to import SVG files and convert them to background-images for HTML files

"""
if __name__ == '__main__':
    #To find skymusic
    import os, sys
    project_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../'))
    if project_path not in sys.path:
        sys.path.append(project_path)

from skymusic.modes import GamePlatform
import os, re, html.parser

class SVGMerger(html.parser.HTMLParser):
    '''A XML tags parser to collect SVG elements and put them in image-background format'''
    
    recording_gate = ('svg',) #When to start and stop recording
    stop_tags = () #Tags that force-interrupt recording 
    suspend_gate = ('defs',) #Tag and content to skip
    valid_attrs = {'svg': ('viewBox', 'xmlns', 'preserveAspectRatio')} #A dictionary of tags for which some attributes must be kept
    drawing_tags = ('path','polygon','text', 'rect', 'circle', 'polyline', 'ellipse', 'line') #SVG elements to be recorded in extenso.   
    valid_attrs_lc = {k:tuple(vi.lower() for vi in v) for k,v in valid_attrs.items()} #same list in lower case because the HTML parser converts everything in lower case
    
    mode_templates = {'html': '{} {{ background-image: url("data:image/svg+xml, {}"); }}',
                      'svg' : '<symbol id="{}" viewBox="{}">{}</symbol>'}
    
    def __init__(self, float_precision=3, mode='html', css_paths=None):
        super().__init__()
        self.float_precision = float_precision # To round floating-point numbers in path elements
        self.mode = mode
        if mode not in self.mode_templates: raise KeyError(mode)
        self.css = dict()
        if css_paths: self.load_css(css_paths)
        self._reset_()

    def _reset_(self):
        self.recording = False
        self.ascii = ''
        self.finished = False
        self.is_xml = False # Not really used
        self.svg_viewBox = "0 0 100 100"

    def _remove_comments_(self, text):
        
        #Remove comments
        text = re.sub(r'<!--(.(?!-->))*.-->', '', text, flags=re.DOTALL)
        text = re.sub(r'/\*[^*]*\*/', '', text, flags=re.DOTALL)
        return text

    def load_css(self, css_paths):
        for css_path in css_paths:
            with open(css_path,'r+') as fp:
                basename = os.path.splitext(os.path.basename(css_path))[0]
                content = self._remove_comments_(fp.read())
                self.css.update({basename: content})
        
    def _roundoff_(self, text):
    
        floating = r'\d+\.\d{2,}'
        fmt = "{:.%df}" % self.float_precision
        
        def replace_digits(mo): return fmt.format(float(mo.group(0)))
        
        return re.sub(floating, replace_digits, text)

    def add_line_feed(self):
        self.ascii += os.linesep
    
    def format_attrs(self, attrs):
        
        attr_strs = [(attr[0]+'="'+attr[1]+'"') for attr in attrs]
        return ' '.join(attr_strs)


    def _handle_starttags_(self, tag, attrs, startend=False):

         if tag in self.stop_tags: # Stops parsing
             self.recording = False
             self.finished = True
             return
         
         if not self.recording and tag in self.recording_gate:
             self.recording = True # Entering recording gate
             self.add_line_feed()
        
         if tag in self.suspend_gate:
             self.recording = False # Pausing recording
         
         if self.recording:
                  
             if tag in self.drawing_tags: # tag must be recorded in extenso
                 if not self.css:            
                     self.ascii += self._roundoff_(self.get_starttag_text().strip())
                 else:
                     if self.css: attrs = self._class_to_inline_(attrs)
                     attrs_str = self.format_attrs(attrs)
                     self.ascii += f"<{tag} {attrs_str}{' /' if startend else ''}>"
             
             else:
                 if tag in self.valid_attrs_lc: # tag has a limit set of valid tags
                     valid_attrs_lc = self.valid_attrs_lc[tag]
                     attrs_str = " " + self.format_attrs([attr for attr in attrs if attr[0] in valid_attrs_lc])
                 else:
                     attrs_str = "" # By default all attributes are ditched
                 
                 if tag == 'svg' and self.mode == "svg":
                     for attr in attrs:
                         if attr[0].lower() == 'viewbox': self.svg_viewBox = attr[1]
                 else:
                    self.ascii += f"<{tag} {attrs_str}{' /' if startend else ''}>"
        
             
             self.add_line_feed()
    
    def handle_starttag(self, tag, attrs):
        
        return self._handle_starttags_(tag, attrs, False)
       
    def handle_startendtag(self, tag, attrs):
        
        if tag in self.suspend_gate:
            self.recording = False
        else:
            return self._handle_starttags_(tag, attrs, True) #Do not add an end tag, thank you


    def _search_css_(self, css_classes):
        
        css_style = ''
        for css_class in css_classes:
            for css in self.css.values():
                mo = re.search(r'\.' + css_class.strip() + r'\s*(?:\s*,[^{]*)*{([^}]*)}', css, re.DOTALL)
                if mo:
                    styles = mo.group(1).split(';')
                    css_style += ';'.join([style.strip() for style in styles])
        
        return css_style


    def _class_to_inline_(self, attrs):
        
        
        attrs_new = {attr:value for (attr, value) in attrs}
         
        css_class = attrs_new.pop('class', '').strip()
        
        css_classes = css_class.split(' ') if css_class else []
        
        css_style = self._search_css_(css_classes).replace(';;',';')
              
        attrs_new['style'] = (attrs_new.get('style', '') + css_style)
        
        return list(attrs_new.items())
                

    def handle_endtag(self, tag):
            
        if self.recording:
            if not (tag == 'svg' and self.mode == 'svg'): self.ascii += f"</{tag}>"
        if self.recording and tag in self.recording_gate: self.recording = False #Pausing recording
        if tag in self.suspend_gate:  self.recording = True #We passed the suspend gate, resuming recording

            

    def handle_data(self, data):
        '''What to do with non-tag text; should not be used with SVG'''
        if self.recording:
            data = data.strip()
            if data: self.ascii += data

    def parse(self, file, svg_name):
        
        for line in file:
            line = line.strip()
            if line: self.feed(line) #send line to built-in html parser method
            if self.finished: break
        
        return self._format_result_(self.ascii, svg_name)

    def _format_result_(self, result, svg_name):
        '''Special formatting of the result to produce a background-image'''
        if self.mode == 'html':
            result = re.sub(r'"','\'',result)
            result = re.sub(r'<','%3C',result)
            result = re.sub(r'>','%3E',result)
        #Correct letter case, especially for viewBox which is case-sensitive
        for tag in self.valid_attrs:
            for attr in self.valid_attrs[tag]:
                if attr.lower() != attr: result = result.replace(attr.lower(),attr)
                
        if mode == 'html':
            result = self.mode_templates['html'].format(svg_name, result.replace('\n',''))
        elif mode == 'svg':
            result = self.mode_templates['svg'].format(svg_name, self.svg_viewBox, result.replace('\n',''))
            
        return result

    def handle_decl(self, decl):
        
        if re.search('xml', decl, re.IGNORECASE):  self.is_xml = True
    
     
    def close(self):
    
        self._reset_()
        super().close()


if __name__ == '__main__':
    
    #%% User parameters
    float_precision = 2
    
    platforms = [GamePlatform.SWITCH, GamePlatform.PLAYSTATION]
    themes = ['light','dark']
    modes = ['html','svg'] #'html, svg'
    css_files = ['svg2png.css'] # for html only
    excluded_svgs = ['unhighlighted-drum', 'unhighlighted-harp', 'empty-drum', 'empty-harp', 'blank']
    strip_text = ['-symbol']
    
    for platform in platforms:
        for theme in themes:
            for mode in modes:
                svg_dir = os.path.join('../resources/original', platform.get_name())
                css_dir = os.path.join('../resources/css', theme)
            
            
                #%% MAIN
                if mode == 'html':
                    escape_html = True
                    css_paths = [os.path.join(css_dir, css_file) for css_file in css_files]
                    for css_path in css_paths:
                        if not os.path.isfile(css_path):
                            print("*** WARNING: {css_path} not found.")
                else:
                    escape_html = False
                    css_paths = []
                    
                # Parse SVG files one by one
                dirpath, _, filenames = next(os.walk(svg_dir), (None, None, []))
                for filename in filenames.copy(): # Remove non SVG files
                    if os.path.splitext(filename)[1].lower().strip() != '.svg':  filenames.remove(filename)
                
                #Collecting and merging
                merger = SVGMerger(float_precision=float_precision, mode=mode, css_paths=css_paths)
                
                merged_file = ''
                for filename in filenames:
                    svg_name = os.path.splitext(filename)[0]
                    path = os.path.join(dirpath, filename)
                    
                    if svg_name not in excluded_svgs:
                        for txt in strip_text:
                            svg_name = svg_name.replace(txt,'')
                        
                        # Parse SVG file
                        with open(path,'r+') as fp:
                            merged_file += merger.parse(fp, platform.get_nickname() + svg_name) #eg psX, psLL
                            
                            merger.close()
                        merged_file += os.linesep
                
                #Write output file
                out_name = platform.get_name() + '_' + theme + '_' + mode + '.txt'
                out = os.path.normpath(os.path.join(svg_dir,out_name))
                with open(out,'w+') as fp: fp.write(merged_file)
            
