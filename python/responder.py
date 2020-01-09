#!/usr/bin/env python3
from modes import InputModes, RenderModes, CSSModes
from parsers import SongParser
from songs import Song
import os
import re


class Responder:

    def __init__(self):

        self.song_dir_in = "test_songs"
        self.song_dir_out = "songs_out"
        self.css_path = "css/main.css"
        self.css_mode = CSSModes.EMBED
        self.render_modes_enabled = [mode for mode in RenderModes]
        # self.render_modes_disabled = [RenderModes.JIANPUASCII, RenderModes.DOREMIASCII]
        self.render_modes_disabled = []
        self.render_modes_enabled = [mode for mode in self.render_modes_enabled if
                                     mode not in self.render_modes_disabled]
        # self.render_modes_enabled = [RenderModes.PNG, RenderModes.SKYASCII, RenderModes.WESTERNASCII]

        self.response_mode = ''

        self.cwd = os.getcwd()
        os.chdir("../..")
        if not os.path.isdir(self.song_dir_out):
            os.mkdir(self.song_dir_out)

    def get_render_modes_enabled(self):

        return self.render_modes_enabled

    def is_render_mode_enabled(self, mode):

        if mode in self.render_modes_enabled:
            return True
        else:
            return False

    def ask_for_mode(self, modes, ask, parser):

        modes_list = {}
        instructions = ""
        i = 0
        instructions += "Please choose your note format:\n'"
        for mode in modes:
            i += 1
            instructions += str(i) + ') ' + mode.value[2] + "\n"
            if mode == InputModes.SKYKEYBOARD:
                instructions += "   " + parser.get_keyboard_layout().replace(" ", "\n   ") + ":"
            modes_list[i] = mode
        self.output(instructions)
        try:
            notation = int(ask('Mode (1-' + str(i) + "): ").strip())
            mode = modes_list[notation]
        except (ValueError, KeyError):
            mode = InputModes.SKY
        return mode

    def set_response_mode(self, response_mode):

        # bot or commandline
        self.response_mode = response_mode

    def get_response_mode(self):

        return self.response_mode

    def ask(self):

        pass

    def output(self, output):

        pass

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
                    print('\nFile not found.')
                    file_path = self.load_file(directory,
                                               input('File name (in ' + os.path.normpath(directory) + '/): ').strip())
                    isfile = os.path.isfile(file_path)
        if isfile:
            return file_path
        else:
            return None

    def read_lines(self, filepath=None):
        """
         Read song lines in fp, or asks the user to type each line in the console
        """
        lines = []
        if filepath is not None:
            try:
                for line in open(filepath, mode='r', encoding='utf-8', errors='ignore'):
                    lines.append(line)
            except (OSError, IOError) as err:
                print('Error opening file.')
                raise err
            print('(Song imported from ' + os.path.abspath(filepath) + ')')
        else:
            line = first_line
            while line:
                line = line.split(os.linesep)
                for line in line:
                    lines.append(line)
                line = input('Type next line: ')
        return lines

    def ask_song_title(self, song):

        song.set_title(self.ask('Song title (also used for the file name): '))
        if song.get_title() == '':
            song.set_title('untitled')


    original_artists = input('Original artist(s): ')
    transcript_writer = input('Transcribed by: ')

    if RenderModes.HTML in ENABLED_MODES:
        html_path = os.path.join(SONG_DIR_OUT, song_title + '.html')
        html_path = song.write_html(html_path, CSS_MODE, CSS_PATH)

        if html_path != '':
            print('============================================================')
            print('Your song in HTML is located at:', html_path)

    if RenderModes.SVG in ENABLED_MODES:
        svg_path0 = os.path.join(SONG_DIR_OUT, song_title + '.svg')
        filenum, svg_path = song.write_svg(svg_path0, CSS_MODE, CSS_PATH)

        if svg_path != '':
            print('--------------------------------------------------')
            print('Your song in SVG is located in:', SONG_DIR_OUT)
            print('Your song has been split into ' + str(filenum + 1) + ' files '
                                                                        'between ' + os.path.split(svg_path0)[
                      1] + ' and ' + os.path.split(svg_path)[1])

    if RenderModes.PNG in ENABLED_MODES:
        png_path0 = os.path.join(SONG_DIR_OUT, song_title + '.png')
        filenum, png_path = song.write_png(png_path0)

        if png_path != '':
            print('--------------------------------------------------')
            print('Your song in PNG is located in:', SONG_DIR_OUT)
            print('Your song has been split into ' + str(filenum + 1) + ' files '
                                                                        'between ' + os.path.split(png_path0)[
                      1] + ' and ' + os.path.split(png_path)[1])

    if RenderModes.MIDI in ENABLED_MODES:
        midi_path = os.path.join(SONG_DIR_OUT, song_title + '.mid')
        midi_ascii_path = song.write_midi(midi_path)
        if midi_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in MIDI is located at:', midi_ascii_path)

    if RenderModes.SKYASCII in ENABLED_MODES and myparser.get_input_mode() not in [InputModes.SKY, InputModes.SKYKEYBOARD]:
        sky_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_sky.txt')
        res = song.write_ascii(sky_ascii_path, RenderModes.SKYASCII)
        if sky_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to Sky notation is located at:', sky_ascii_path)

    if RenderModes.ENGLISHASCII in ENABLED_MODES and myparser.get_input_mode() not in [InputModes.ENGLISH,
                                                                           InputModes.ENGLISHCHORDS]:
        english_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_english.txt')
        english_ascii_path = song.write_ascii(english_ascii_path, RenderModes.ENGLISHASCII)
        if english_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to English notation with C key is located at:', english_ascii_path)

    if RenderModes.JIANPUASCII in ENABLED_MODES and myparser.get_input_mode() != InputModes.JIANPU:
        jianpu_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_jianpu.txt')
        jianpu_ascii_path = song.write_ascii(jianpu_ascii_path, RenderModes.JIANPUASCII)
        if jianpu_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to Jianpu notation with 1 key is located at:', jianpu_ascii_path)

    if RenderModes.DOREMIASCII in ENABLED_MODES and myparser.get_input_mode() != InputModes.DOREMI:
        doremi_ascii_path = os.path.join(SONG_DIR_OUT, song_title + '_doremi.txt')
        doremi_ascii_path = song.write_ascii(doremi_ascii_path, RenderModes.DOREMIASCII)
        if doremi_ascii_path != '':
            print('--------------------------------------------------')
            print('Your song in TXT converted to doremi notation with do key is located at:', doremi_ascii_path)
