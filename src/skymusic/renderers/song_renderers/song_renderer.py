import re, os, io
from src.skymusic import Lang

class SongRendererError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)

    pass


class SongRenderer():
    
    def __init__(self, locale=None):
        
        if locale is None:
            self.locale = Lang.guess_locale()
            print(f"**WARNING: Song self.maker has no locale. Reverting to: {self.locale}")
        else:
            self.locale = locale


    def write_buffers(self, song, **kwargs):
        
        return
        
    
    def write_buffers_to_files(self, song, render_mode, buffers, dir_out):
        """
        Writes the content of an IOString or IOBytes buffer list to one or several files.
        Command line only
        """
        try:
            numfiles = len(buffers)
        except (TypeError, AttributeError):
            buffers = [buffers]
            numfiles = 1

        file_paths = self.build_file_paths(song, render_mode, numfiles, dir_out)
        
        # Creates output directory if did not exist
        for file_path in file_paths:
            song_dir_out = os.path.dirname(file_path)
        
            if not os.path.isdir(song_dir_out):
                os.mkdir(song_dir_out)
                                          
        written_paths = []
        for (file_path, buffer) in zip(file_paths, buffers):

            if isinstance(buffer, io.StringIO):
                output_file = open(file_path, 'w+', encoding='utf-8', errors='ignore')
            elif isinstance(buffer, io.BytesIO):
                output_file = open(file_path, 'bw+')
            elif buffer is None:
                pass
            else:
                raise SongRendererError(f"Unknown buffer type in {self}")
      
            if buffer is not None:
                output_file.write(buffer.getvalue())
                written_paths.append(file_path)

        return written_paths


    def build_file_paths(self, song, render_mode, numfiles, dir_out):
        """
        Command line only : generates a list of file paths for a given input mode.
        """
        if numfiles == 0:
            return []
        
        sanitized_title = re.sub(r'[\\/:"*?<>|]', '', re.escape(song.get_title())).strip()
        sanitized_title = re.sub('(\s)+', '_', sanitized_title)  # replaces spaces by underscore
        sanitized_title = sanitized_title[:31]
        if len(sanitized_title) == 0 or sanitized_title == '_':
            sanitized_title = Lang.get_string("song_meta/untitled", self.locale)
        
        file_base = os.path.join(dir_out, sanitized_title)
        file_ext = render_mode.extension

        file_paths = []
        if numfiles > 1:
            for i in range(numfiles):
                file_paths += [file_base + str(i) + file_ext]
        else:
            file_paths = [file_base + file_ext]

        return file_paths
        
        
