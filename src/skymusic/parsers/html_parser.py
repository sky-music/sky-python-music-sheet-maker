import os, re, html.parser
#from skymusic.song import Song

class HtmlSongParser(html.parser.HTMLParser):
    
    def __init__(self):
        self.recording = False
        self.ascii = ''
        self.finished = False
        self.is_html = False
        super().__init__()

    def add_line_feed(self):
        if self.recording:
            self.ascii += os.linesep
      
    def handle_starttag(self, tag, attrs):
        if self.recording:
            self.ascii += f"<{tag}>"
        else:
            if tag == 'html':
                self.is_html = True
            elif tag == 'div' and attrs:
                if attrs[0] == ('id', 'ascii'):
                    self.recording = True

    def handle_endtag(self, tag):
        if self.recording:
            if tag == 'div':
                self.recording = False
                self.finished = True
            else:
                self.ascii += f"</{tag}>"

    def handle_data(self, data):
        if self.recording:
            data = data.strip()
            if data:
                self.ascii += data       

    def detect_html(self, splitted_lines):

        i = 0
        for line in splitted_lines:
            if i > 10:
                break
            line = line.strip()
            if line:
                self.feed(line)
                i += 1
                
        return self.is_html
                    

    def parse_html(self, splitted_lines):
        
        for line in splitted_lines:
            line = line.strip()
            if line:
                self.add_line_feed()
                self.feed(line)
            if self.finished:
                break
        
        self.ascii = self.ascii.strip()
        if not self.ascii:
            return []
        else:
            song_lines = self.ascii.split(os.linesep)     
            return song_lines
            #headers_skip = len(Song().get_meta())
            #return song_lines[headers_skip:]

    def handle_decl(self, decl):
        
        if re.search('html', decl, re.IGNORECASE):
            self.is_html = True
                    
    def close(self):
    
        self.init()
        super().close()
