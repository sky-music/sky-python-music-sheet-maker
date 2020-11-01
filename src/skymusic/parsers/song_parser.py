import os, re
from skymusic import instruments, Lang
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
        self.lyric_delimiter = Resources.LYRIC_DELIMITER
        self.metadata_delimiter = Resources.METADATA_DELIMITER
        self.repeat_indicator = Resources.REPEAT_INDICATOR
        self.default_key = Resources.DEFAULT_KEY
        self.allowed_regex = ['\s', '\t', '\w', '\d', '\n', '\r', '\a', '\e', '\f', '\v', '\R']
        
        self.music_theory = music_theory.MusicTheory(self)
        try:
            self.locale = self.maker.get_locale()
        except AttributeError:  # Should never happen
            self.locale = Lang.guess_locale()
            print(f"**ERROR: SongParser self.maker has no locale. Reverting to {self.locale}")
    
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
        except AttributeError as err:
            return False
        except UnicodeDecodeError:
            return True

    def check_delimiters(self):

        if self.input_mode == InputMode.JIANPU or isinstance(self.note_parser, skymusic.parsers.noteparsers.jianpu.Jianpu):
            if self.pause != Resources.JIANPU_PAUSE:
                
                if not self.silent_warnings:
                    print('\n'+Lang.get_string("warnings/jianpu_pause", self.locale).format(pause=self.pause))
                self.pause = Resources.JIANPU_PAUSE
            if self.quaver_delimiter == '-':
                
                if not self.silent_warnings:
                    print('\n'+Lang.get_string("warnings/jianpu_quaver_delimiter", self.locale).format(jianpu_quaver_delimiter=Resources.JIANPU_QUAVER_DELIMITER, quaver_delimiter=self.quaver_delimiter))
                self.quaver_delimiter = Resources.JIANPU_QUAVER_DELIMITER

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
        
    def get_instrument_type(self):
        
        return self.instrument_type

    def find_key(self, song_lines=None):
        
        return self.music_theory.find_key(song_lines)

    def get_note_parser(self, input_mode=None):

        if self.note_parser is not None:
            return self.note_parser

        if input_mode is None:
            input_mode = self.input_mode
        
        (rows, columns) = self.get_instrument_type().get_instrument().get_dimensions()
        note_parser = input_mode.get_note_parser(locale=self.locale)
        note_parser.set_dimensions((rows, columns))

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

    def parse_chords(self, chords, song_key=Resources.DEFAULT_KEY, note_shift=0):
        """
        Creates a skygrid from the harp's chord notes
        # For each chord, sets the highlighted state of each note accordingly (True or False)
        """

        # A isolated note is a single-element list: chords=['A5']
        # An isolated chord is a single element list: chords=['B1A1A3']
        # Triplets and quavers have been decomposed into a list of notes or chords: chords=['B2', 'B3B1', 'B4', 'B5', 'C1', 'C2']
        harp_broken = True
        skygrid = {}

        if len(chords) > 1:
            idx0 = 1  # Chords in quavers and triplets have a frame index>1
        else:
            idx0 = 0  # An isolated chord or note has a frame index==0

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
                note_broken = False
                try:
                    if note == self.pause:
                        highlighted_note_position = (-1, -1)
                    else:
                        highlighted_note_position = self.note_parser.calculate_coordinate_for_note(note, song_key,
                                                                                                   note_shift, False)
                except (KeyError, SyntaxError) as err:
                    note_broken = True
                    harp_broken = True
                    if not self.silent_warnings:
                        print(err)
                finally:
                    
                    if not note_broken:
                        skygrid[highlighted_note_position] = {}
                        skygrid[highlighted_note_position][idx0 + chord_idx] = True
                        harp_silent = False
                        if highlighted_note_position[0] < 0 and highlighted_note_position[1] < 0:  # Note is a silence
                            skygrid[highlighted_note_position][idx0 + chord_idx] = False
                            harp_silent = True

        results = [skygrid, harp_broken, harp_silent, repeat]
        return results

    def convert_bracket_chords(self, line):
        
        bracket_chord = re.compile('((\(|\[)(?:\w|\s)+(\)|\]))')
        brackets_blanks = re.compile('\[|\]|\(|\)|\s')
        chord_matches = bracket_chord.finditer(line)
        for match in chord_matches:
            notes = brackets_blanks.sub('',match.group(0))
            line = line.replace(match.group(0), notes)
        return line

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
                if line[0] == self.lyric_delimiter:
                    delimiter = self.lyric_delimiter
                else:
                    delimiter = self.icon_delimiter
                
            if delimiter in self.allowed_regex:
                return re.compile(delimiter).split(line)
            else:
                return line.split(delimiter)


    def parse_line(self, line, song_key=Resources.DEFAULT_KEY, note_shift=0):
        """
        Returns instrument_line: a list of  'skygrid' objects (1 skygrid = 1 dict)
        """
        instrument_line = []
        line = self.sanitize_line(line)

        if len(line) > 0 and not re.match(re.escape(Resources.METADATA_DELIMITER),line):
            if line[0] == self.lyric_delimiter:
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
            
            (changed, meta_data) = parser.parse_metadata(input_lines[0], song)
        
        else:
            
            dict_iter = iter(song.get_meta())
            regexp = re.escape(Resources.METADATA_DELIMITER) + '([^:]+):*(.*)'
            
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
                    meta_data[next_key] = g2.strip() if g2.strip() else g1.strip()
                    changed = True
            
        return (changed, meta_data)


    def parse_song(self, song_lines, song_key, octave_shift):
        """
        Create a Song object from the textual song in 'song_lines'
        Requires knowledge of the input mode and the song key.
        """
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
            song_lines = song_lines.split(os.linesep)
            
        if self.input_mode == InputMode.SKYHTML:
            song_lines = HtmlSongParser().parse_html(song_lines)
        elif self.input_mode == InputMode.MIDI:
            song_lines = MidiSongParser().parse_midi(song_lines)

        english_song_key = self.english_note_name(song_key)

        note_shift = self.get_note_parser().get_base_of_western_major_scale() * octave_shift

        # Parses song line by line
        song = Song(locale=self.locale, music_key=english_song_key)
        
        (changed, meta_data) = self.parse_metadata(song_lines, song)
        if changed:
            song.set_meta(**meta_data)
            song.set_meta_changed(True)
                
        for song_line in song_lines:
            instrument_line = self.parse_line(song_line, song_key,
                                              note_shift)  # The song key must be in the original format
            song.add_line(instrument_line)

        return song
