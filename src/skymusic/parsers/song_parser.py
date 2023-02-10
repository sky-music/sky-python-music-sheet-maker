import os, re
from skymusic import instruments, sheetlayout, Lang
from skymusic.modes import InputMode, InstrumentType
from skymusic.song import Song
import skymusic.parsers.noteparsers
from skymusic.resources import Resources
from skymusic.parsers.html_parser import HtmlSongParser
from skymusic.parsers.midi_parser import MidiSongParser
from skymusic.parsers import music_theory

class SongParserError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation
    def __str__(self):
        return str(self.explanation)
    pass

class SongParser:
    """
    For parsing a text format into a Song object
    """
    _num_errors = 0
    _max_errors = 30
    
    def __init__(self, maker, silent_warnings=True):

        self.maker = maker
        self.instrument_type = InstrumentType.NORMAL
        self.silent_warnings = silent_warnings
        self.input_mode = None
        self.note_parser = None
        self.icon_delimiter = Resources.DELIMITERS['icon']
        self.pause = Resources.DELIMITERS['pause']
        self.quaver_delimiter = Resources.DELIMITERS['quaver']
        self.lyric_delimiter = Resources.DELIMITERS['lyric']
        self.metadata_delimiter = Resources.DELIMITERS['metadata']
        self.repeat_indicator = Resources.DELIMITERS['repeat']
        self.layer_delimiter = Resources.DELIMITERS['layer']
        self.default_key = Resources.DEFAULT_KEY
        #Delimiters must be character or strings
        #The backslash character is forbidden
        #Only regex with the following format are supported: \x, where x is s, t, w, d, n, r, a, r, f, v, or R
        self.allowed_regex = ['\s', '\t', '\w', '\d', '\n', '\r', '\a', '\e', '\f', '\v', '\R']
        self.ruler_regex = Resources.DELIMITERS['lyric'] + r'{0,1}\s*(?P<code>' + r'|'.join(Resources.MARKDOWN_CODES['rulers']) + r')+\s*(?P<text>.*)'
        self.layer_regex = Resources.DELIMITERS['lyric'] + r'{0,1}\s*(?P<code>' + Resources.DELIMITERS['layer'] + r')+\s*(?P<text>.*)'
        self.music_theory = music_theory.MusicTheory(self)
        try:
            self.locale = self.maker.get_locale()
        except AttributeError:  # Should never happen
            self.locale = Lang.guess_locale()
            print(f"**ERROR: SongParser self.maker has no locale. Reverting to {self.locale}")

    def __print_error__(self,err):
        if not self.silent_warnings:
            print(err)
            self._num_errors += 1
            if self._num_errors > self._max_errors:
                self.silent_warnings = True
                print("Suppressing error logging after %d errors." % self._max_errors)

    def get_input_mode(self):
        return self.input_mode
        
    def set_instrument_type(self, instrument_type):
        self.instrument_type = instrument_type
        
    def get_instrument_type(self):
        return self.instrument_type    
            
    def get_icon_delimiter(self):
        return self.icon_delimiter

    def get_pause(self):
        return self.pause

    def get_quaver_delimiter(self):
        return self.quaver_delimiter

    def get_lyric_delimiter(self):
        return self.lyric_delimiter

    def get_repeat_indicator(self):
        return self.repeat_indicator

    def get_default_key(self):
        key = self.english_note_name(note_name=self.default_key, reverse=True)
        if not key:
            key = self.default_key
        return key

    def get_maker(self):
        return self.maker

    def check_is_bytes(self, song_line):
        if isinstance(song_line, (list,tuple)):
            line = song_line[0]
        else:
            line = song_line
        try:
            line.decode()
            return True
        except AttributeError:
            return False
        except UnicodeDecodeError:
            return True

    def check_delimiters(self):

        if self.input_mode == InputMode.JIANPU or isinstance(self.note_parser, skymusic.parsers.noteparsers.jianpu.Jianpu):
            if self.pause != Resources.DELIMITERS['jianpu_pause']:
                
                if not self.silent_warnings:
                    print('\n'+Lang.get_string("warnings/jianpu_pause", self.locale).format(pause=self.pause))
                self.pause = Resources.DELIMITERS['jianpu_pause']
            if self.quaver_delimiter == '-':
                
                if not self.silent_warnings:
                    print('\n'+Lang.get_string("warnings/jianpu_quaver_delimiter", self.locale).format(jianpu_quaver_delimiter=Resources.DELIMITERS['jianpu_quaver'], quaver_delimiter=self.quaver_delimiter))
                self.quaver_delimiter = Resources.DELIMITERS['jianpu_quaver']

        delims = [self.icon_delimiter, self.pause, self.quaver_delimiter, self.lyric_delimiter, self.repeat_indicator, self.metadata_delimiter]

        if self.quaver_delimiter == '\s' or re.match('\s', self.quaver_delimiter):
            print("\n***ERROR: You cannot use a blank delimiter to separate notes in a quaver")
        if self.pause == '\s' or re.match('\s', self.pause):
            print("\n***ERROR: You cannot use a blank delimiter to indicate a pause")
        if self.lyric_delimiter == '\s' or re.match('\s', self.lyric_delimiter):
            print("\n***ERROR: You cannot use a blank delimiter to indicate lyrics")
        if self.metadata_delimiter == '\s' or re.match('\s', self.metadata_delimiter):
            print("\n***ERROR: You cannot use a blank delimiter to indicate metadata")
        if self.lyric_delimiter == '\s' or re.match('\s', self.repeat_indicator):
            print("\n***ERROR: You cannot use a blank delimiter to indicate repetition")

        parser = self.get_note_parser()
        if parser is not None:
            for delim in delims:
                if (parser.not_note_name_regex.match(delim) is None or parser.not_octave_regex.match(delim) is None) and delim not in [self.lyric_delimiter, self.metadata_delimiter]:
                    print(f"\n***ERROR: You chose an invalid delimiter for notation {self.input_mode.get_short_desc(self.locale)}: {delim}")
                if delims.count(delim) > 1:
                    print("\n***ERROR: You used the same delimiter for different purposes.")

    def get_possible_modes(self, song_lines=None):
        """
        Returns all the possible InputMode for the textual song 'song_lines'
        """
        if self.input_mode is not None:
            return [self.input_mode]
        else:
            if not song_lines: return []
            if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
                song_lines = song_lines.strip().split(os.linesep)
                
            return self.music_theory.detect_input_mode(song_lines)
            

    def set_input_mode(self, input_mode):
        if isinstance(input_mode, InputMode):
            self.input_mode = input_mode
            self.set_note_parser(self.input_mode)
            self.check_delimiters()
        else:
            raise SongParserError(f"Cannot set input_mode: invalid input_mode: {input_mode}")

    def find_key(self, song_lines=None):
        return self.music_theory.find_key(song_lines)

    def get_note_parser(self, input_mode=None):

        if self.note_parser is not None: return self.note_parser
        if input_mode is None: input_mode = self.input_mode
        
        shape = self.get_instrument_type().get_shape()
        note_parser = input_mode.get_note_parser(locale=self.locale, shape=shape)
        #note_parser.set_shape(shape)

        return note_parser

    def set_note_parser(self, input_mode=None):

        if input_mode is None: input_mode = self.input_mode

        if input_mode is None:
            raise SongParserError("cannot set NoteParser: Invalid input_mode {input_mode}")
        else:
            self.note_parser = self.get_note_parser(input_mode)

    def english_note_name(self, note_name, reverse=False):
        if self.note_parser is None:
            return ''
        else:
            return self.note_parser.english_note_name(note_name, reverse)

    def split_icon(self, icon, delimiter=None):
        """
        A song is a list of icons
        An icon is a bundle of chords assembled with '-': ['A1C2-F3D4', 'C#4B4-Gb3A2']
        This method splits an icon into a list of chords:  ['A1C2', 'F3D4', 'C#4B4', 'Gb3A2']
        """
        if delimiter is None:
            delimiter = self.quaver_delimiter
            if delimiter in self.allowed_regex:
                return re.compile(delimiter).split(icon)
            else:
                return icon.split(delimiter)

    def split_repeat(self, chord):
        """
        Separates the chords from its repeat indicator
        """
        try:
            repeat = int(re.split(re.escape(self.repeat_indicator), chord)[1])
        except (IndexError, ValueError):
            repeat = 1
        else:
            chord = re.split(re.escape(self.repeat_indicator), chord)[0]

        return repeat, chord

    def split_chord(self, chord, note_parser=None):
        """
        A chord is a collection of notes glued together:  ['A1C2', 'F3D4', 'C#4B4', 'Gb3A2']
        This method splits each chord into a list of notes: [['A1',C2'], ['F3','D4'],...]
        """
        if note_parser is None: note_parser = self.note_parser

        try:
            chord = note_parser.note_name_regex.sub(' \\1', chord).split()
        except AttributeError as err:
            self.__print_error__(err)

        return chord

    def parse_chords(self, chords, song_key=Resources.DEFAULT_KEY, note_shift=0):
        """
        Creates a skygrid from the harp's chord notes
        # For each chord, sets the highlighted state of each note accordingly (True or False)
        """

        # A isolated note is a single-element list: chords=['A5']
        # An isolated chord is a single element list: chords=['B1A1A3']
        # Triplets and quavers have been decomposed into a list of notes or chords: chords=['B2', 'B3B1', 'B4', 'B5', 'C1', 'C2']
        harp_broken = True

        # Notes/chords in quavers and triplets have a frame index >= 1
        # A black/white note or chord has a frame index == 0
        start_frame = 1 if len(chords) > 1 else 0     

        if self.note_parser is None: self.set_note_parser()
        is_chord_parser = hasattr(self.note_parser, 'decode_chord')
        skygrid = instruments.Skygrid(shape=self.note_parser.get_shape())

        for chord_idx, chord in enumerate(chords):

            repeat, chord = self.split_repeat(chord)
            if is_chord_parser: chord = self.note_parser.decode_chord(chord) #Cmaj7': f"C{x}E{x}G{x}B{x}" 
            notes = self.split_chord(chord)
            # Now the real chord has been split in notes (1 note = 1 list slot)

            harp_broken = False # No probllem detected yet, so the Harp is a priori OK
            harp_silent = True  # No note detected yet, so the Harp is a priori silent
            for note in notes:  # Chord is a list of notes
                note_broken = False
                try:
                    if note == self.pause:
                        highlighted_coords = (-1, -1)
                    else:
                        highlighted_coords = self.note_parser.calculate_coordinate_for_note(note, song_key,
                                                                             note_shift, False)
                except (KeyError, SyntaxError) as err:
                    note_broken = True
                    harp_broken = True
                    harp_silent = False # Harp is broken, so it's not silent
                    if not self.silent_warnings: self.__print_error__(err)
                
                if not note_broken:
                    highlighted = (highlighted_coords[0] >= 0 and highlighted_coords[1] >= 0)
                    skygrid.set_note(highlighted_coords, start_frame + chord_idx, highlighted)
                    if highlighted: harp_silent = False

        results = [skygrid, harp_broken, harp_silent, repeat]
        return results

    def convert_bracket_chords(self, line):
        
        bracket_chord = re.compile(r'(?:\(|\[)((?:\w+\s*)+)(?:\)|\])')
        line = bracket_chord.sub(lambda mo:re.sub(r'\s','',mo.group(1)), line)
        return line
    
    def remove_script_tags(self,line):
        '''Remove HTML script tags in song text to prevent hacking'''
        script_tags = re.compile('<\s*/*\s*script[^>]*>', re.I)
        return script_tags.sub('',line)
    
    def sanitize_line(self, line):
        """
        Strip leading spaces and replace surnumerous spaces
        :param line:
        :return:
        """
        if self.input_mode is not InputMode.SKYJSON:
            line = self.convert_bracket_chords(line)
        
        line = re.sub('(\s){2,}', '\\1', line)  # removes surnumerous blank characters
        line = line.strip()
        
        line = self.remove_script_tags(line)
        
        if self.icon_delimiter in self.allowed_regex:
            delimiter = self.icon_delimiter
        elif self.icon_delimiter==' ':
            delimiter = '\s'
        else:
            delimiter = re.escape(self.icon_delimiter)       

        line = re.sub('(' + delimiter + ')' + '{2,}', '\\1', line)  # removes surnumerous delimiters
        line = re.sub('^'+delimiter+'|'+delimiter+'$','', line) #strip delimiters on edges
        
        return line

    
    def split_line(self, line, delimiter=None):
        """
        Splits a song line into icons
        An icon is a made of 1 note, several notes (chord), or several chords played rapidly (triplet, quaver)
        Icons will be visually split in SkyGrid renders (aka Harps), possibly with pauses between them
        """
        if delimiter is None:
            if line[0] == self.lyric_delimiter:
                delimiter = self.lyric_delimiter
            else:
                delimiter = self.icon_delimiter
            
        if delimiter in self.allowed_regex:
            return re.compile(delimiter).split(line)
        elif delimiter=="#":# to allow HTML/CSS hex color codes
            return re.compile(r'(?<!"|\'|:|#)#').split(line)
        elif delimiter=="%":# to allow percentages in HTML/CSS size attributes
            return re.compile(r'%(?!"|\')').split(line)
        else:
            return line.split(delimiter)


    def parse_line(self, line, song_key=Resources.DEFAULT_KEY, note_shift=0):
        """
        Takes a single string
        Returns instrument_line: a list of  'skygrid' objects (1 skygrid = 1 dict)
        """
        instrument_line = []
        line = self.sanitize_line(line)

        if len(line) > 0 and not re.match(re.escape(Resources.DELIMITERS['metadata']),line):
                       
            hr_match = re.match(self.ruler_regex, line)
            lay_match = re.match(self.layer_regex, line)
            
            if hr_match:
                hr = sheetlayout.Ruler()
                hr.set_code(hr_match.group('code')) # Markdown code
                hr.set_text(hr_match.group('text')) # possible text
                instrument_line.append(hr)
            
            elif lay_match:
                lay = sheetlayout.Layer()
                lay.set_code(lay_match.group('code')) # Code
                lay.set_text(lay_match.group('text')) # possible layer name
                instrument_line.append(lay)   
                                                                        
            elif line[0] == self.lyric_delimiter:
                lyrics = self.split_line(line)
                for lyric in lyrics:
                    if len(lyric) > 0:
                        voice = instruments.Voice()
                        voice.set_lyric(lyric.strip())
                        instrument_line.append(voice)
            else:
                icons = self.split_line(line)
                
                for icon in icons:
                    chords = self.split_icon(icon)
                    # From here, real chords are still glued, quavers have been split in different list slots
                    skygrid, harp_broken, harp_silent, repeat = self.parse_chords(chords, song_key, note_shift)
                    
                    harp = self.instrument_type.get_instrument()
                    harp.set_repeat(repeat)
                    harp.set_is_silent(harp_silent)
                    harp.set_is_broken(harp_broken)
                    harp.set_skygrid(skygrid)

                    instrument_line.append(harp)
        
        return instrument_line


    def parse_metadata(self, input_lines, song):
        changed = False        
        
        if self.input_mode == InputMode.SKYJSON and len(input_lines) > 0:
            from . import json_parser
            parser = json_parser.JsonSongParser(self.maker, self.silent_warnings)
            parser.set_input_mode(self.input_mode)
            
            (changed, meta_data) = parser.parse_metadata(input_lines, song)
        
        else:
            
            dict_iter = iter(song.get_meta())
            regexp = re.escape(Resources.DELIMITERS['metadata']) + '([^:]+):*(.*)'
            
            meta_data = {}
            i = 0
            for line in input_lines:
                line = self.sanitize_line(line)
                g = re.match(regexp,line)
                if line and not g:
                    break
                if g:
                    try:
                        next_key = next(dict_iter)
                    except StopIteration:
                        next_key = f"meta{i}"
                        i += 1
                    (g1, g2) = g.groups()
                    #meta_data[next_key] = g2.strip() if g2.strip() else g1.strip()
                    meta_data[next_key] = g2.strip()
                    changed = True
            
        return (changed, meta_data)


    def parse_song(self, song_lines, song_key, octave_shift):
        """
        Create a Song object from the textual song in 'song_lines'
        Requires knowledge of the input mode and the song key.
        """
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
            song_lines = song_lines.strip().split(os.linesep)
            
        if self.input_mode == InputMode.SKYHTML:
            song_lines = HtmlSongParser().parse_html(song_lines)
        elif self.input_mode == InputMode.MIDI:
            song_lines = MidiSongParser(self.maker, self.silent_warnings).parse_midi(song_lines)
        elif self.input_mode == InputMode.SKYJSON:
            from . import json_parser
            parser = json_parser.JsonSongParser(self.maker, self.silent_warnings)
            song_lines = parser.sanitize_lines(song_lines,join=True)
            
        english_song_key = self.english_note_name(song_key)

        note_shift = self.get_note_parser().get_base_of_western_major_scale() * octave_shift

        # Parses song line by line
        song = Song(locale=self.locale, music_key=english_song_key)
        
        # Metadata first, indicates by a special character such as #$
        (changed, meta_data) = self.parse_metadata(song_lines, song)
        if changed:
            song.set_meta(**meta_data)
            song.set_meta_changed(True)
         
        if self.input_mode == InputMode.SKYJSON:
            from . import json_parser
            parser = json_parser.JsonSongParser(self.maker, self.silent_warnings)
            parser.set_input_mode(self.input_mode)
            song_lines = parser.parse_layers(song_lines[0])                                          
        
        # IMPORTANT: at this point song_lines is a list of strings                                                                                                                                                                                                                                                                                                                                                                  
        for song_line in song_lines:
            instrument_line = self.parse_line(song_line, song_key,
                                              note_shift)  # The song key must be in the original format
            song.add_line(instrument_line)

        return song
        
