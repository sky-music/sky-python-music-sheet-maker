#!/usr/bin/env python3
"""
A script to import SVG files and convert them to background-images for HTML files

"""
import os, re, html.parser

class SVGMerger(html.parser.HTMLParser):
    '''A XML tags parser to collect SVG elements and put them in image-background format'''
    
    recording_gate = ('svg',) #When to start and stop recording
    stop_tags = () #Tags that force-interrupt recording 
    suspend_gate = ('style',) #Tag and content to skip
    valid_attrs = {'svg': ('viewBox', 'xmlns')} #A dictionary of tags for which some attributes must be kept
    verbatim_tags = ('path','polygon','text', 'rect', 'circle', 'polyline', 'ellipse', 'line') #SVG elements to be recorded in extenso.   
    valid_attrs_lc = {k:tuple(vi.lower() for vi in v) for k,v in valid_attrs.items()} #same list in lower case because the HTML parser converts everything in lower case
    
    def __init__(self, float_precision=3):
        super().__init__()
        self.float_precision = float_precision # To round floating-point numbers in path elements
        self._reset_()

    def _reset_(self):
        self.recording = False
        self.ascii = ''
        self.finished = False
        self.is_xml = False # Not really used
        
    def roundoff(self, text):
    
        floating = r'\d+\.\d{2,}'
        fmt = "{:.%df}" % self.float_precision
        
        def replace_digits(mo): return fmt.format(float(mo.group(0)))
        
        return re.sub(floating, replace_digits, text)

    def add_line_feed(self):
        if self.recording: self.ascii += os.linesep
    
    def format_attrs(self, attrs):
        
        attr_strs = [(attr[0]+'="'+attr[1]+'"') for attr in attrs]
        return ' '.join(attr_strs)
    
    def handle_starttag(self, tag, attrs):
        
        if tag in self.stop_tags: # Stops parsing
            self.recording = False
            self.finished = True
            return
        
        if not self.recording and tag in self.recording_gate:
            self.recording = True # Entering recording gate
            self.add_line_feed()
            
        if tag in self.suspend_gate: self.recording = False # Pausing recording
        
        if self.recording:
            if tag in self.valid_attrs_lc: # tag has a limite set of valid tags
                valid_attrs_lc = self.valid_attrs_lc[tag]
                attrs_str = self.format_attrs([attr for attr in attrs if attr[0] in valid_attrs_lc])
                self.ascii += f"<{tag} {attrs_str}>"
            elif tag in self.verbatim_tags: # tag must be recorded in extenso
                self.ascii += self.roundoff(self.get_starttag_text().strip())
            else: # By default all attributes are ditched
                self.ascii += f"{tag}"
            self.add_line_feed()
                

    def handle_endtag(self, tag):
        
        if tag in self.suspend_gate:  self.recording = True #We passed the suspend gate, resuming recording
        if self.recording: self.ascii += f"</{tag}>"
        if self.recording and tag in self.recording_gate: self.recording = False #Pausing recording

    def handle_startendtag(self, tag, attrs):
        
        self.handle_starttag(tag, attrs) #Do not add an end tag, thank you

    def handle_data(self, data):
        '''What to do with non-tag text; should not be used with SVG'''
        if self.recording:
            data = data.strip()
            if data: self.ascii += data

    def parse(self, file):
        
        for line in file:
            line = line.strip()
            if line: self.feed(line) #send line to built-in html parser method
            if self.finished: break
        
        return self.format_result(self.ascii)

    def format_result(self, result):
        '''Special formatting of the result to produce a background-image'''
        result = re.sub(r'"','\'',result)
        result = re.sub(r'<','%3C',result)
        result = re.sub(r'>','%3E',result)
        #Correct letter case, especially for viewBox which is case-sensitive
        for tag in self.valid_attrs:
            for attr in self.valid_attrs[tag]:
                if attr.lower() != attr: result = result.replace(attr.lower(),attr)
        return result

    def handle_decl(self, decl):
        
        if re.search('xml', decl, re.IGNORECASE):  self.is_xml = True
                    
    def close(self):
    
        self._reset_()
        super().close()


if __name__ == '__main__':
    
    merger = SVGMerger(float_precision=2)
    
    svg_dir = '../resources/png/svg/switch/'
    
    template = 'sw{} {{ background-image: url("data:image/svg+xml, {}"); }}'


    # Parse SVG files one by one
    dirpath, _, filenames = next(os.walk(svg_dir), (None, None, []))
    for filename in filenames: # Remove non SVG files
        if os.path.splitext(filename)[1].lower().strip() != '.svg':  filenames.remove(filename)
    
    merged_file = ''
    for filename in filenames:
        svg_name = os.path.splitext(filename)[0]
        path = os.path.join(dirpath, filename)
        
        # Parse SVG file
        with open(path,'r+') as fp:
            merged_file += template.format(svg_name, merger.parse(fp)).replace(os.linesep,'')
            merger.close()
        merged_file += os.linesep
    
    #Write output file
    out = os.path.join(svg_dir,'svg_merged.txt')
    with open(out,'w+') as fp: fp.write(merged_file)
    
