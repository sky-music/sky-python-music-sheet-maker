import os, re
from src.skymusic import instruments, Lang
from src.skymusic.modes import InputMode, InstrumentType
from src.skymusic.song import Song
import src.skymusic.parsers.noteparsers
from src.skymusic.resources import Resources
from src.skymusic.parsers.html_parser import HtmlSongParser
from src.skymusic.parsers import music_theory


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

    def __init__(self, maker, silent_warnings=True):

        self.maker = maker
        self.instrument_type = InstrumentType.NORMAL
        self.silent_warnings = silent_warnings
        #Delimiters must be character or strings
        #The backslash character is forbidden
        #Only regex with the following format are supported: \x, where x is s, t, w, d, n, r, a, r, f, v, or R
        self.input_mode = None
        self.note_parser = None
        self.icon_delimiter = Resources.ICON_DELIMITER
        self.pause = Resources.PAUSE
        self.quaver_delimiter = Resources.QUAVER_DELIMITER
        self.comment_delimiter = Resources.COMMENT_DELIMITER
        self.repeat_indicator = Resources.REPEAT_INDICATOR
        self.default_key = Resources.DEFAULT_KEY
        self.allowed_regex = ['\s', '\t', '\w', '\d', '\n', '\r', '\a', '\e', '\f', '\v', '\R']
        
        self.music_theory = music_theory.MusicTheory(self)
        try:
            self.locale = self.maker.get_locale()
        except AttributeError:  # Should never happen
            self.locale = Lang.guess_locale()
            print(f"**ERROR: SongParser self.maker has no locale. Reverting to {self.locale}")

    """
    def set_delimiters(self, icon_delimiter=Resources.ICON_DELIMITER, pause=Resources.PAUSE, quaver_delimiter=Resources.QUAVER_DELIMITER, comment_delimiter=Resources.COMMENT_DELIMITER,
                       repeat_indicator=Resources.REPEAT_INDICATOR):

        self.icon_delimiter = icon_delimiter
        self.pause = pause
        self.quaver_delimiter = quaver_delimiter
        self.comment_delimiter = comment_delimiter
        self.repeat_indicator = repeat_indicator
    """
    
    def get_icon_delimiter(self):

        return self.icon_delimiter

    def get_pause(self):

        return self.pause

    def get_quaver_delimiter(self):

        return self.quaver_delimiter

    def get_comment_delimiter(self):

        return self.comment_delimiter

    def get_repeat_indicator(self):

        return self.repeat_indicator

    def get_default_key(self):
        
        key = self.english_note_name(note_name=self.default_key, reverse=True)
        if not key:
            key = self.default_key
        return key

    def get_maker(self):

        return self.maker

    def check_delimiters(self):

        if self.input_mode == InputMode.JIANPU or isinstance(self.note_parser, src.skymusic.parsers.noteparsers.jianpu.Jianpu):
            if self.pause != Resources.JIANPU_PAUSE:
                
                if not self.silent_warnings:
                    print('\n'+Lang.get_string("warnings/jianpu_pause", self.locale).format(pause=self.pause))
                self.pause = Resources.JIANPU_PAUSE
            if self.quaver_delimiter == '-':
                
                if not self.silent_warnings:
                    print('\n'+Lang.get_string("warnings/jianpu_quaver_delimiter", self.locale).format(jianpu_quaver_delimiter=Resources.JIANPU_QUAVER_DELIMITER, quaver_delimiter=self.quaver_delimiter))
                self.quaver_delimiter = Resources.JIANPU_QUAVER_DELIMITER

        delims = [self.icon_delimiter, self.pause, self.quaver_delimiter, self.comment_delimiter, self.repeat_indicator]


        if self.quaver_delimiter == '\s' or re.match('\s', self.quaver_delimiter):
            print("\n***ERROR: You cannot use a blank delimiter to separate notes in a quaver")
        if self.pause == '\s' or re.match('\s', self.pause):
            print("\n***ERROR: You cannot use a blank delimiter to indicate a pause")
        if self.comment_delimiter == '\s' or re.match('\s', self.comment_delimiter):
            print("\n***ERROR: You cannot use a blank delimiter to indicate comments")
        if self.comment_delimiter == '\s' or re.match('\s', self.repeat_indicator):
            print("\n***ERROR: You cannot use a blank delimiter to indicate repetition")

        parser = self.get_note_parser()
        if parser is not None:
            for delim in delims:
                if (parser.not_note_name_regex.match(delim) is None or parser.not_octave_regex.match(delim) is None) and delim != self.comment_delimiter:
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
            if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
                song_lines = song_lines.split(os.linesep)
                
            return self.music_theory.detect_input_mode(song_lines)

    def set_input_mode(self, input_mode):

        if isinstance(input_mode, InputMode):
            self.input_mode = input_mode
            self.set_note_parser(self.input_mode)
            self.check_delimiters()
        else:
            raise SongParserError(f"Cannot set input_mode: invalid input_mode: {input_mode}")

    def get_input_mode(self):

        return self.input_mode

    def set_instrument_type(self, instrument_type):
        
        self.instrument_type = instrument_type
        
    def get_instrument_type(self, instrument_type):
        
        return self.instrument_type

    def find_key(self, song_lines=None):
        
        return self.music_theory.find_key(song_lines)

    def get_note_parser(self, input_mode=None):

        if self.note_parser is not None:
            return self.note_parser

        if input_mode is None:
            input_mode = self.input_mode

        note_parser = input_mode.get_note_parser(locale=self.locale)

        return note_parser

    def set_note_parser(self, input_mode=None):

        if input_mode is None:
            input_mode = self.input_mode

        if input_mode is None:
            raise SongParserError("cannot set NoteParser: Invalid input_mode {input_mode}")
        else:
            self.note_parser = self.get_note_parser(input_mode)

    def english_note_name(self, note_name, reverse=False):
        if self.note_parser is None:
            #print("\n***WARNING: no note parser defined.")
            return ''
        else:
            return self.note_parser.english_note_name(note_name, reverse)

    def split_icon(self, icon, delimiter=None):
        """
        An icon is a collection of chords assembled with '-': ['A1C2-F3D4', 'C#4B4-Gb3A2']
        This method splits an icon into a list of chords:  ['A1C2', 'F3D4', 'C#4B4', 'Gb3A2']
        """
        if delimiter is None:
            delimiter = self.quaver_delimiter
            if delimiter in self.allowed_regex:
                return re.compile(delimiter).split(icon)
            else:
                return icon.split(delimiter)

    def split_chord(self, chord, note_parser=None):
        """
        A chord is a collection of notes glued together:  ['A1C2', 'F3D4', 'C#4B4', 'Gb3A2']
        This method splits each chord into a list of notes: [['A1',C2'], ['F3','D4'],...]
        """
        try:
            repeat = int(re.split(re.escape(self.repeat_indicator), chord)[1])
            chord = re.split(re.escape(self.repeat_indicator), chord)[0]
        except (IndexError, ValueError):
            repeat = 1

        if note_parser is None:
            note_parser = self.note_parser

        try:
            chord = note_parser.note_name_regex.sub(' \\1', chord).split()
        except AttributeError as err:
            if not self.silent_warnings:
                print(err)

        return repeat, chord

    def parse_chords(self, chords, song_key='C', note_shift=0):
        """
        Creates a skygrid from the harp's chord notes
        # For each chord, sets the highlighted state of each note accordingly (True or False)
        """

        # Individual note is a single-element list: chords=['A5']
        # Real chord is a single element list: chords=['B1A1A3']
        # Triplets and quavers are a list of notes or chords: chords=['B2', 'B3B1', 'B4', 'B5', 'C1', 'C2']
        harp_broken = True
        chord_skygrid = {}

        if len(chords) > 1:
            idx0 = 1  # Notes in quavers and triplets have a frame index >1
        else:
            idx0 = 0  # Single note or note in chord has a frame index ==0

        if self.note_parser is None:
            self.set_note_parser()

        try:
            self.note_parser.decode_chord
            is_chord_parser = True
        except AttributeError:
            is_chord_parser = False

        for chord_idx, chord in enumerate(chords):

            if is_chord_parser:
                chord = self.note_parser.decode_chord(chord)

            repeat, chord = self.split_chord(chord)
            # Now the real chord has been split in notes (1 note = 1 list slot)

            harp_broken = False
            harp_silent = False
            for note in chord:  # Chord is a list of notes
                try:
                    if note == self.pause:
                        highlighted_note_position = (-1, -1)
                    else:
                        highlighted_note_position = self.note_parser.calculate_coordinate_for_note(note, song_key,
                                                                                                   note_shift, False)
                except (KeyError, SyntaxError) as err:
                    harp_broken = True
                    if not self.silent_warnings:
                        print(err)
                else:
                    chord_skygrid[highlighted_note_position] = {}
                    chord_skygrid[highlighted_note_position][idx0 + chord_idx] = True
                    harp_silent = False
                    if highlighted_note_position[0] < 0 and highlighted_note_position[1] < 0:  # Note is a silence
                        chord_skygrid[highlighted_note_position][idx0 + chord_idx] = False
                        harp_silent = True

        results = [chord_skygrid, harp_broken, harp_silent, repeat]
        return results

    def sanitize_line(self, line):
        """
        Strip leading spaces and replace surnumerous spaces
        :param line:
        :return:
        """
        line = re.sub('(\s){2,}', '\\1', line)  # removes surnumerous blank characters
        line = line.strip()
        
        if self.icon_delimiter in self.allowed_regex:
            delimiter = self.icon_delimiter
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
        if self.input_mode == InputMode.SKYJSON:
            from . import json_parser
            parser = json_parser.JsonSongParser(self.maker, self.silent_warnings)
            parser.set_input_mode(self.input_mode)
            return parser.split_line(line)
            
        else:
            
            if delimiter is None:
                if line[0] == self.comment_delimiter:
                    delimiter = self.comment_delimiter
                else:
                    delimiter = self.icon_delimiter
                
            if delimiter in self.allowed_regex:
                return re.compile(delimiter).split(line)
            else:
                return line.split(delimiter)


    def parse_line(self, line, song_key='C', note_shift=0):
        """
        Returns instrument_line: a list of chord 'skygrid' (1 chord = 1 dict)
        """
        instrument_line = []
        line = self.sanitize_line(line)

        if len(line) > 0:
            if line[0] == self.comment_delimiter:
                #lyrics = line.split(self.comment_delimiter)
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
                    chord_skygrid, harp_broken, harp_silent, repeat = self.parse_chords(chords, song_key, note_shift)
                    
                    harp = self.instrument_type.get_instrument()
                    harp.set_repeat(repeat)
                    harp.set_is_silent(harp_silent)
                    harp.set_is_broken(harp_broken)
                    harp.set_chord_skygrid(chord_skygrid)

                    instrument_line.append(harp)

        return instrument_line

    def parse_song(self, song_lines, song_key, octave_shift):
        """
        Create a Song object from the textual song in 'song_lines'
        Requires knowledge of the input mode and the song key.
        """
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
            song_lines = song_lines.split(os.linesep)
            
        if self.input_mode == InputMode.SKYHTML:
            song_lines = HtmlSongParser().parse_html(song_lines)

        english_song_key = self.english_note_name(song_key)

        note_shift = self.get_note_parser().get_base_of_western_major_scale() * octave_shift

        # Parses song line by line
        song = Song(locale=self.locale, music_key=english_song_key)
        for song_line in song_lines:
            instrument_line = self.parse_line(song_line, song_key,
                                              note_shift)  # The song key must be in the original format
            song.add_line(instrument_line)

        return song
