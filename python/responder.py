#!/usr/bin/env python3
import io
import os
import re

from modes import InputMode, RenderMode, CSSMode, ResponseMode
from parsers import SongParser
from songs import Song


class Responder:
    """
    For managing text input and output from external sources to the Parser
    """

    def __init__(self, dir_in='test_songs', dir_out='songs_out', questions=None):

        self.song_dir_in = dir_in
        self.song_dir_out = dir_out
        self.css_path = "css/main.css"
        self.css_mode = CSSMode.EMBED
        self.render_modes_enabled = [mode for mode in RenderMode]
        # self.render_modes_disabled = [RenderMode.JIANPUASCII, RenderMode.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]
        # self.render_modes_enabled = [RenderMode.PNG, RenderMode.SKYASCII, RenderMode.WESTERNASCII]

        self.response_mode = ''

        self.song = None
        self.parser = None

        self.init_working_directory()
        self.directory_base = os.getcwd()

        self.questions = questions

    def init_working_directory(self):

        os.chdir('../')
        if not os.path.isdir(self.song_dir_out):
            os.mkdir(self.song_dir_out)

    def get_directory_base(self):

        return self.directory_base

    def get_song_dir_out(self):

        return os.path.join(self.get_directory_base(), self.song_dir_out)

    def get_song_dir_in(self):

        return os.path.join(self.get_directory_base(), self.song_dir_in)

    def get_css_mode(self):

        return self.css_mode

    def get_css_path(self):

        return self.css_path

    def get_render_modes_enabled(self):

        return self.render_modes_enabled

    def is_render_mode_enabled(self, mode):

        if mode in self.render_modes_enabled:
            return True
        else:
            return False

    def get_song(self):

        return self.song

    def set_song(self, song):

        self.song = song

    def get_parser(self):

        return self.parser

    def set_parser(self, parser):

        self.parser = parser

    def set_response_mode(self, response_mode):

        self.response_mode = response_mode

    def create_questions(self):

        pass

    def ask_to_select_mode(self, modes):

        modes_list = {}
        instructions = ""
        i = 0
        instructions += "Please choose your note format:\n"
        for mode in modes:
            i += 1
            instructions += str(i) + ') ' + mode.value[2] + "\n"
            modes_list[i] = mode
        self.output(instructions)
        try:
            notation = int(self.ask('Mode (1-' + str(i) + "): ").strip())
            mode = modes_list[notation]
        except (ValueError, KeyError):
            self.output('No valid notation selected. Using SKY by default.')
            mode = InputMode.SKY
        return mode

    def get_response_mode(self):

        return self.response_mode

    def ask(self, prompt):

        user_response = None

        if self.get_response_mode() == ResponseMode.BOT:

            # TODO: I don't know how to do this
            pass

        elif self.get_response_mode() == ResponseMode.COMMAND_LINE:

            user_response = input(prompt)

        return user_response

    def output(self, output):

        if self.get_response_mode() == ResponseMode.COMMAND_LINE:
            print(output)
        # TODO: refactor print and input to use ResponseMode.COMMAND_LINE and BOT

    def create_song_command_line(self):

        self.set_parser(SongParser(self))

        os.chdir(self.get_directory_base())

        self.output_instructions()

        first_line = self.ask_first_line()
        fp = self.load_file(self.get_song_dir_in(), first_line)  # loads file or asks for next line
        song_lines = self.read_lines(first_line, fp)

        # Parse song
        # TODO: refactor song_lines, song_keys, parse_song to be in Song class
        self.ask_input_mode(song_lines)
        song_key = self.ask_song_key(self.get_parser().get_input_mode(), song_lines)
        note_shift = self.ask_note_shift()
        self.set_song(self.parse_song(song_lines, song_key, note_shift))

        self.calculate_error_ratio()

        # Song information
        self.ask_song_title()
        self.ask_song_headers(song_key)

        # Output
        if self.get_response_mode() == ResponseMode.COMMAND_LINE:
            self.write_song_to_files()
        elif ResponseMode.BOT:
            # TODO: choose RenderMode according to player request
            self.send_song_to_channel(RenderMode.PNG)
        else:
            return

    def output_instructions(self):

        self.output('===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====')
        self.output('\nAccepted music notes formats:')
        for mode in InputMode:
            self.output('\n* ' + mode.value[2])
        self.output('\nNotes composing a chord must be glued together (e.g. A1B1C1).')
        self.output('Separate chords with \"' + self.get_parser().get_icon_delimiter() + '\".')
        self.output('Use \"' + self.get_parser().get_pause() + '\" for a silence (rest).')
        self.output(
            'Use \"' + self.get_parser().get_quaver_delimiter() + '\" to link notes within an icon, for triplets, '
                                                                  'quavers... (e.g. A1' + self.get_parser(

            ).get_quaver_delimiter() + 'B1' + self.get_parser().get_quaver_delimiter() + 'C1).')
        self.output('Add ' + self.get_parser().get_repeat_indicator() + '2 after a chord to indicate repetition.')
        self.output('Sharps # and flats b (semitones) are supported for Western and Jianpu notations.')
        self.output('===========================================')

    def ask_first_line(self):

        first_line = input(
            'Type or copy-paste notes, or enter file name (in ' + os.path.normpath(
                self.get_song_dir_in()) + '/): ').strip()

        return first_line

    def load_file(self, directory, filename):
        """
        if string is a file name, loads the file, else return None
        """
        file_path = os.path.join(directory, os.path.normpath(filename))
        isfile = os.path.isfile(file_path)

        # Assumes that user has forgotten extension
        if not isfile:
            file_path = os.path.join(filename, os.path.normpath(filename + '.txt'))
            isfile = os.path.isfile(file_path)

        if not isfile:
            file_path = None
            splitted = os.path.splitext(filename)
            if len(splitted[0]) > 0 and 2 < len(splitted[1]) <= 5 and re.search('\\.', splitted[0]) is None:
                # then probably a file name
                while file_path is None:
                    self.output('\nFile not found.')
                    file_path = self.load_file(directory,
                                               input('File name (in ' + os.path.normpath(directory) + '/): ').strip())
                    isfile = os.path.isfile(file_path)
        if isfile:
            return file_path
        else:
            return None

    def read_lines(self, first_line=None, filepath=None):
        """
         Read song lines in fp, or asks the user to type each line in the console
        """

        if self.get_response_mode() == ResponseMode.COMMAND_LINE:
            lines = []
            if filepath is not None:
                try:
                    for line in open(filepath, mode='r', encoding='utf-8', errors='ignore'):
                        lines.append(line)
                except (OSError, IOError) as err:
                    self.output('Error opening file.')
                    raise err
                self.output('(Song imported from ' + os.path.abspath(filepath) + ')')
            else:
                line = first_line
                while line:
                    line = line.split(os.linesep)
                    for line in line:
                        lines.append(line)
                    line = input('Type next line: ')
            return lines

    def ask_song_title(self):

        self.get_song().set_title(self.ask('Song title (also used for the file name): '))
        if self.get_song().get_title() == '':
            self.get_song().set_title('untitled')

    def ask_song_headers(self, song_key):
        self.output('\nPlease fill song info or press ENTER to skip:')
        original_artists = self.ask('Original artist(s): ')
        transcript_writer = self.ask('Transcribed by: ')
        self.get_song().set_headers(original_artists, transcript_writer, song_key)

    def ask_input_mode(self, song_lines):

        possible_modes = self.get_parser().get_possible_modes(song_lines)

        if len(possible_modes) > 1:
            self.output('\nSeveral possible notations detected.')
            input_mode = self.ask_to_select_mode(possible_modes)
        elif len(possible_modes) == 0:
            self.output('\nCould not detect your note format. Maybe your song contains typo errors?')
            input_mode = self.ask_to_select_mode(possible_modes)
        else:
            self.output('\nWe detected that you use the following notation: ' + possible_modes[0].value[1] + '.')
            input_mode = possible_modes[0]

        self.get_parser().set_input_mode(input_mode)

    def ask_song_key(self, input_mode, song_lines):

        """Attempts to detect key for input written in absolute musical scales (western, Jianpu)"""
        if input_mode in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU]:
            possible_keys = self.get_parser().find_key(song_lines)
            if len(possible_keys) == 0:
                self.output("\nYour song cannot be transposed exactly in Sky.")
                # trans = input('Enter a key or a number to transpose your song within the chromatic scale:')
                self.output("\nDefault key will be set to C.")
                song_key = 'C'
            elif len(possible_keys) == 1:
                song_key = str(possible_keys[0])
                self.output("\nYour song can be transposed in Sky with the following key: " + song_key)
            else:
                self.output("\nYour song can be transposed in Sky with the following keys: " + ', '.join(possible_keys))
                song_key = ''
                while song_key not in possible_keys:
                    song_key = str(input('Choose your key: '))
        else:
            song_key = str(input('Recommended key to play the visual pattern: '))

        return song_key

    def ask_note_shift(self):

        if self.get_parser().get_input_mode() in [InputMode.ENGLISH, InputMode.DOREMI, InputMode.JIANPU,
                                                  InputMode.ENGLISHCHORDS]:
            try:
                note_shift = int(7 * eval(input('Shift song by how many octaves? (-n ; +n): ').strip()))
            except (NameError, SyntaxError):
                note_shift = 0
        else:
            note_shift = 0

        return note_shift

    def parse_song(self, song_lines, song_key, note_shift):

        english_song_key = self.get_parser().english_note_name(song_key)

        # Parses song line by line
        song = Song(responder=self, music_key=english_song_key)  # The song key must be in English format
        for song_line in song_lines:
            instrument_line = self.get_parser().parse_line(song_line, song_key,
                                                           note_shift)  # The song key must be in the original format
            song.add_line(instrument_line)

        return song

    def calculate_error_ratio(self):
        self.output('===========================================')
        error_ratio = self.get_song().get_num_broken() / max(1, self.get_song().get_num_instruments())
        if error_ratio == 0:
            self.output('Song successfully read with no errors!')
        elif error_ratio < 0.05:
            self.output('Song successfully read with few errors!')
        else:
            self.output('**WARNING**: Your song contains many errors. Please check the following:'
                        '\n- All your notes are within octaves 4 and 6. If not, try again with an octave shift.'
                        '\n- Your song is free of typos. Please check this website for full instructions: '
                        'https://sky.bloomexperiment.com/t/summary-of-input-modes/403')

    def write_buffer_to_file(self, buffer_list, file_path0):
        """Writes the content of an IOString or IOBytes buffer list to one or several files
        """
        try:
            numfiles = len(buffer_list)
        except:
            buffer_list = [buffer_list]
            numfiles = 1

        (file_base, file_ext) = os.path.splitext(file_path0)

        for filenum, buffer in enumerate(buffer_list):
            if numfiles > 1:
                file_path = file_base + str(filenum) + file_ext
            else:
                file_path = file_path0

            if isinstance(buffer, io.StringIO):
                output_file = open(file_path, 'w+', encoding='utf-8', errors='ignore')
            elif isinstance(buffer, io.BytesIO):
                output_file = open(file_path, 'bw+')
            else:
                raise Exception('Unknown buffer type in ' + str(self))
            output_file.write(buffer.getvalue())
        return file_path

    def write_song_to_files(self):
        """
        Writes the song to files with different formats as defined in RenderMode
        """
        self.output('==========================================')
        for render_mode in self.get_render_modes_enabled():

            if render_mode == RenderMode.HTML:
                buffer_list = [self.get_song().write_html(self.get_css_mode(), self.get_css_path())]
            elif render_mode == RenderMode.SVG:
                buffer_list = self.get_song().write_svg(self.get_css_mode(), self.get_css_path())
            elif render_mode == RenderMode.PNG:
                buffer_list = self.get_song().write_png()
            elif render_mode == RenderMode.MIDI:
                buffer_list = [self.get_song().write_midi()]
            else:  # Ascii
                buffer_list = [self.get_song().write_ascii(render_mode)]

            numfiles = len(buffer_list)
            file_ext = render_mode.value[2]
            file_path0 = os.path.join(self.get_song_dir_out(), self.get_song().get_title() + file_ext)

            try:
                file_path = self.write_buffer_to_file(buffer_list, file_path0)

                if numfiles > 1:
                    self.output('Your song in ' + render_mode.value[1] + ' is located in: ' + self.get_song_dir_out())
                    self.output(
                        'Your song has been split into ' + str(numfiles) + ' between ' + os.path.split(file_path0)[
                            1] + ' and ' + os.path.split(file_path)[1])
                else:
                    self.output('Your song in ' + render_mode.value[1] + ' is located at:' + file_path)
            except (OSError, IOError):
                self.output('Could not write to ' + render_mode.value[1] + ' file.')
            self.output('------------------------------------------')

    def send_song_to_channel(self, render_mode):
        """Sends the song as a file to a Discord channel, with format according to render_mode"""
        if not self.is_render_mode_enabled(render_mode):
            self.output('Sorry, this song format is disabled.')
        else:
            if render_mode == RenderMode.HTML:
                buffer_list = [self.get_song().write_html(self.get_css_mode(), self.get_css_path())]
            elif render_mode == RenderMode.SVG:
                buffer_list = self.get_song().write_svg(self.get_css_mode(), self.get_css_path())
            elif render_mode == RenderMode.PNG:
                buffer_list = self.get_song().write_png()
            elif render_mode == RenderMode.MIDI:
                buffer_list = [self.get_song().write_midi()]
            else:  # Ascii
                buffer_list = [self.get_song().write_ascii(render_mode)]

            numfiles = len(buffer_list)

            if numfiles == 0:
                self.output('No ' + render_mode.value[1] + ' was generated.')
                return

            file_ext = render_mode.value[2]
            file_name0 = self.get_song().get_title() + file_ext

            (file_base, file_ext) = os.path.splitext(file_name0)

            for filenum, buffer in enumerate(buffer_list):
                if filenum > 0:
                    file_name = file_base + str(filenum) + file_ext
                else:
                    file_name = file_name0

                buffer.seek(0)  # reset the reader to the beginning
                self.output('Sending file to discord not implemented yet')
                # TODO: finish
                # await channel.send(file=discord.File(buffer, file_name))
