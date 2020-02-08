#!/usr/bin/env python3
import re, os, math
from operator import truediv, itemgetter
from modes import InputMode
import instruments
import noteparsers


class SongParser:
    """
    For parsing a text format into a Song object
    """

    def __init__(self, responder):

        self.input_mode = None
        self.note_parser = None
        self.icon_delimiter = ' '
        self.pause = '.'
        self.quaver_delimiter = '-'
        self.comment_delimiter = '#'
        self.repeat_indicator = '*'
        self.responder = responder
        self.directory_base = self.responder.get_directory_base()

    def set_delimiters(self, icon_delimiter=' ', pause='.', quaver_delimiter='-', comment_delimiter='#',
                       repeat_indicator='*'):

        self.icon_delimiter = icon_delimiter
        self.pause = pause
        self.quaver_delimiter = quaver_delimiter
        self.comment_delimiter = comment_delimiter
        self.repeat_indicator = repeat_indicator

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

    def get_responder(self):

        return self.responder

    def check_delimiters(self):

        if self.input_mode == InputMode.JIANPU or isinstance(self.note_parser, noteparsers.jianpu.Jianpu):
            if self.pause != '0':
                print('Jianpu notation is used: setting 0 as the pause character instead of ' + self.pause)
                self.pause = '0'
            if self.quaver_delimiter == '-':
                print('Jianpu notation is used: setting ^ as the quaver delimiter instead of ' + self.quaver_delimiter)
                self.quaver_delimiter = '^'

        delims = [self.icon_delimiter, self.pause, self.quaver_delimiter, self.comment_delimiter, self.repeat_indicator]

        parser = self.get_note_parser()
        if parser is not None:
            for delim in delims:
                if (parser.not_note_name_regex.match(delim) is None or parser.not_octave_regex.match(
                        delim) is None) and delim != self.comment_delimiter:
                    print('You chose an invalid delimiter for notation ' + self.input_mode.value[1] + ': ' + delim)
                if delims.count(delim) > 1:
                    print('You chose twice the same delimiter for notation ' + self.input_mode.value[1] + ': ' + delim)

    def get_possible_modes(self, song_lines=None):

        if self.input_mode is not None:
            return [self.input_mode]
        else:
            return self.detect_input_mode(song_lines)

    def set_input_mode(self, input_mode):

        if isinstance(input_mode, InputMode):
            self.input_mode = input_mode
            self.set_note_parser(self.input_mode)
            self.check_delimiters()

    def get_input_mode(self):

        return self.input_mode

    def get_note_parser(self, input_mode=None):

        if self.note_parser is not None:
            return self.note_parser

        if input_mode is None:
            input_mode = self.input_mode

        note_parser = None

        if input_mode == InputMode.SKYKEYBOARD:
            note_parser = noteparsers.skykeyboard.SkyKeyboard()
        elif input_mode == InputMode.SKY:
            note_parser = noteparsers.sky.Sky()
        elif input_mode == InputMode.ENGLISH:
            note_parser = noteparsers.english.English()
        elif input_mode == InputMode.DOREMI:
            note_parser = noteparsers.doremi.Doremi()
        elif input_mode == InputMode.JIANPU:
            note_parser = noteparsers.jianpu.Jianpu()
        elif input_mode == InputMode.ENGLISHCHORDS:
            note_parser = noteparsers.englishchords.EnglishChords()

        return note_parser

    def set_note_parser(self, input_mode=None):

        if input_mode is None:
            input_mode = self.input_mode
        self.note_parser = self.get_note_parser(input_mode)

    def english_note_name(self, note_name, reverse=False):
        if self.note_parser is None:
            print('Warning: no note parser defined.')
            return ''
        else:
            return self.note_parser.english_note_name(note_name, reverse)

    def split_icon(self, icon, delimiter=None):

        """
        An icon is a collection of chords assembled with '-': ['A1C2-F3D4', 'C#4B4-Gb3A2']
        This method splits an icon into alist of chords:  ['A1C2', 'F3D4', 'C#4B4', 'Gb3A2']
        """

        if delimiter is None:
            delimiter = self.quaver_delimiter
        return icon.split(delimiter)

    def split_chord(self, chord, note_parser=None):
        """
        A chord is a collection of notes glued together:  ['A1C2', 'F3D4', 'C#4B4', 'Gb3A2']
        This method splits each chord into a list of notes: [['A1',C2'], ['F3','D4'],...]
        """
        try:
            repeat = int(re.split(re.escape(self.repeat_indicator), chord)[1])
            chord = re.split(re.escape(self.repeat_indicator), chord)[0]
        except:
            repeat = 1

        if note_parser is None:
            note_parser = self.note_parser

        try:
            chord = note_parser.note_name_regex.sub(' \\1', chord).split()
        except AttributeError as err:
            print(err)

        return repeat, chord

    def parse_chords(self, chords, song_key='C', note_shift=0):
        # Individual note is a single-element list: chords=['A5']
        # Real chord is a single element list: chords=['B1A1A3']
        # Triplets and quavers are a list of notes or chords: chords=['B2', 'B3B1', 'B4', 'B5', 'C1', 'C2']
        harp_broken = True
        chord_skygrid = {}

        # print(chord)
        if len(chords) > 1:
            idx0 = 1  # Notes in quavers and triplets have a frame index >1
        else:
            idx0 = 0  # Single note or note in chord has a frame index ==0

        if self.note_parser is None:
            self.set_note_parser()

        for chord_idx, chord in enumerate(chords):
            '''
            Creates a skygrid from the harp's chord notes
            # For each chord, sets the highlighted state of each note accordingly (True or False)
            '''
            # TODO: this line is useless since we don't use position maps anymore.
            # chord = re.sub(re.escape(self.pause), '.', chord) #Replaces the pause character by the default

            if isinstance(self.note_parser, noteparsers.englishchords.EnglishChords):
                chord = self.note_parser.decode_chord(chord)

            repeat, chord = self.split_chord(chord)
            # Now the real chord has been split in notes (1 note = 1 list slot)

            harp_broken = False
            harp_silent = False
            for note in chord:  # Chord is a list of notes
                # Except InvalidLetterException
                try:
                    if note == self.pause:
                        highlighted_note_position = (-1, -1)
                    else:
                        highlighted_note_position = self.note_parser.calculate_coordinate_for_note(note, song_key,
                                                                                                   note_shift, False)
                except (KeyError, SyntaxError) as err:
                    print(err)
                    harp_broken = True
                else:
                    chord_skygrid[highlighted_note_position] = {}
                    chord_skygrid[highlighted_note_position][idx0 + chord_idx] = True
                    harp_silent = False
                    if highlighted_note_position[0] < 0 and highlighted_note_position[1] < 0:  # Note is a silence
                        chord_skygrid[highlighted_note_position][idx0 + chord_idx] = False
                        harp_silent = True

        results = [chord_skygrid, harp_broken, harp_silent, repeat]
        return results

    def parse_line(self, line, song_key='C', note_shift=0):
        """
        Returns instrument_line: a list of chord 'skygrid' (1 chord = 1 dict)
        """
        instrument_line = []
        line = line.strip()
        line = re.sub(re.escape(self.icon_delimiter) + '{2,' + str(max(2, len(line))) + '}', self.icon_delimiter,
                      line)  # removes surnumerous spaces
        if len(line) > 0:
            if line[0] == self.comment_delimiter:
                lyrics = line.split(self.comment_delimiter)
                for lyric in lyrics:
                    if len(lyric) > 0:
                        voice = instruments.Voice(self.get_responder())
                        voice.set_lyric(lyric.strip())
                        instrument_line.append(voice)
            else:
                icons = line.split(self.icon_delimiter)
                for icon in icons:
                    chords = self.split_icon(icon)
                    # From here, real chords are still glued, quavers have been split in different list slots
                    chord_skygrid, harp_broken, harp_silent, repeat = self.parse_chords(chords, song_key, note_shift)
                    harp = instruments.Harp(self.get_responder())
                    harp.set_repeat(repeat)
                    harp.set_is_silent(harp_silent)
                    harp.set_is_broken(harp_broken)
                    harp.set_chord_skygrid(chord_skygrid)

                    instrument_line.append(harp)

        return instrument_line

    def find_key(self, song_lines):

        if self.note_parser is None:
            self.set_note_parser()
        # print('note parser is:')
        # print(self.note_parser)

        try:
            possible_keys = [k for k in self.note_parser.CHROMATIC_SCALE_DICT.keys()]
            is_note_regex = self.note_parser.note_name_regex
            not_note_regex = self.note_parser.not_note_name_regex
            # print(possible_keys)
        except AttributeError:
            # Parsers not having a chromatic scale keys should return None, eg Sky and Skykeyboard
            return None
        # print(possible_keys)
        scores = [0] * len(possible_keys)
        num_notes = [0] * len(possible_keys)
        for line in song_lines:
            if len(line) > 0:
                if line[0] != self.comment_delimiter:
                    notes = is_note_regex.sub(' \\1',
                                              not_note_regex.sub('', line)).split()  # Clean-up, adds space and split
                    for i, k in enumerate(possible_keys):
                        for note in notes:
                            num_notes[i] += 1
                            try:
                                # TODO: Support for Jianpu which uses a different octave indexing system
                                self.note_parser.calculate_coordinate_for_note(note, k, note_shift=0,
                                                                               is_finding_key=True)
                            except KeyError:
                                scores[i] += 1
                            except SyntaxError:  # Wrongly formatted notes are ignored
                                num_notes[i] -= 1

        num_notes = [1 if x == 0 else x for x in num_notes]
        # Removes zeros to avoid division by zero
        scores = list(map(truediv, scores, num_notes))
        scores = [(1 - score) for score in scores]

        # duplicates_dict = self.CHROMATIC_SCALE_DICT
        return self.most_likely(scores, possible_keys, 0.9, self.note_parser.CHROMATIC_SCALE_DICT)

    def detect_input_mode(self, song_lines):
        """
        Attempts to detect input musical notation
        """
        possible_modes = [mode for mode in InputMode]
        possible_parsers = [self.get_note_parser(mode) for mode in possible_modes]
        # position_maps = [self.get_note_parser(mode).position_map for mode in possible_modes]
        possible_regex = [parser.single_note_name_regex for parser in possible_parsers]

        good_notes = [0] * len(possible_modes)
        num_notes = [0] * len(possible_modes)
        defg_notes = 0
        qwrt_notes = 0
        octave_span = 0

        for line in song_lines:
            line = line.strip()
            line = re.sub(re.escape(self.icon_delimiter) + '{2,' + str(max(2, len(line))) + '}', self.icon_delimiter,
                          line)  # removes surnumerous spaces
            if len(line) > 0:
                if line[0] != self.comment_delimiter:
                    icons = line.split(self.icon_delimiter)
                    for icon in icons:
                        chords = self.split_icon(icon)
                        for chord in chords:
                            for idx, possible_mode in enumerate(possible_modes):

                                if possible_mode == InputMode.ENGLISHCHORDS:
                                    notes = [chord]  # Because abbreviated chord names are not composed of note names
                                    good_notes[idx] += sum(
                                        [int(note in possible_parsers[idx].english_chords.keys()) for note in notes])
                                else:
                                    repeat, notes = self.split_chord(chord, possible_parsers[idx])
                                    good_notes[idx] += sum(
                                        [int(possible_regex[idx].match(note) is not None) for note in notes if
                                         note != self.pause])
                                # TODO: use self.map_note_to_position?

                                num_notes[idx] += sum([1 for note in notes if note != self.pause])

                                if possible_mode == InputMode.ENGLISH:
                                    defg_notes += sum([int(re.search('[D-Gd-g]', note) is not None) for note in notes])
                                    qwrt_notes += sum(
                                        [int(re.search('[QWRTSZXVqwrtszxv]', note) is not None) for note in notes])
                                    octaves = [re.search('\d', note) for note in notes]

                                    octaves = sorted([int(octave.group(0)) for octave in octaves if octave is not None])
                                    if len(octaves) > 0:
                                        octave_span = max(octave_span, octaves[-1] - octaves[0] + 1)

        num_notes = [1 if x == 0 else x for x in num_notes]  # Removes zeros to avoid division by zero

        scores = list(map(truediv, good_notes, num_notes))
        defg_notes /= num_notes[possible_modes.index(InputMode.ENGLISH)]
        qwrt_notes /= num_notes[possible_modes.index(InputMode.SKYKEYBOARD)]

        if ((defg_notes == 0) or (defg_notes < 0.01 and octave_span > 2)) and (
                num_notes[possible_modes.index(InputMode.ENGLISH)] > 10):
            scores[possible_modes.index(InputMode.ENGLISH)] *= 0.5

        if ((qwrt_notes == 0) or (qwrt_notes < 0.01 and octave_span <= 1)) and (
                num_notes[possible_modes.index(InputMode.SKYKEYBOARD)] > 5):
            scores[possible_modes.index(InputMode.SKYKEYBOARD)] *= 0.5
        # print(scores)

        return self.most_likely(scores, possible_modes, 0.9)

    def most_likely(self, scores, items, threshold=0.9, duplicates_dict=None):

        if len(scores) == 0:
            return None
        if len(scores) == 1:
            return [items[0]]

        sorted_idx, sorted_scores = zip(
            *sorted([(i, e) for i, e in enumerate(scores)], key=itemgetter(1), reverse=True))

        sorted_items = [items[i] for i in sorted_idx]
        # print(sorted_scores)
        # print(sorted_items)

        if sorted_scores[0] == 1 and sorted_scores[1] < 1:
            return [sorted_items[0]]

        if sorted_scores[0] == 1 and sorted_scores[1] == 1:
            if duplicates_dict is not None:
                try:
                    if sorted_scores[2] < 1 and duplicates_dict[sorted_items[0]] == duplicates_dict[sorted_items[1]]:
                        return [sorted_items[0]]
                except (IndexError, KeyError):
                    pass
            return [k for i, k in enumerate(sorted_items) if sorted_scores[i] == 1]

        if sorted_scores[0] < threshold:
            # contrasts = [(score-min(sorted_scores))/(score+min(sorted_scores)) if score!=0 else 0 for score in
            # sorted_scores ]
            sorted_items = [k for i, k in enumerate(sorted_items) if sorted_scores[i] > threshold / 2]
        else:
            sorted_scores = list(map(truediv, sorted_scores, [max(sorted_scores)] * len(sorted_scores)))
            over_items = [k for i, k in enumerate(sorted_items) if sorted_scores[i] > threshold]
            if len(over_items) != 0:
                sorted_items = over_items

        if duplicates_dict is not None:
            # Remove synonyms
            for i in range(1, len(sorted_items), 2):
                if duplicates_dict[sorted_items[i]] == duplicates_dict[sorted_items[i - 1]]:
                    sorted_items[i] = None
            sorted_items = [item for item in sorted_items if item is not None]

        if len(sorted_items) == 0:
            return items
        else:
            return sorted_items
