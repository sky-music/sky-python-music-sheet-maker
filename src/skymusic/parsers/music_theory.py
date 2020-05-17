#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re
from operator import truediv, itemgetter
import json
from src.skymusic.modes import InputMode 


class MusicTheory():
    """
     This class is actually just an extension of SongParser,
     so any change made to song parser may break this one.   
        
    """
    
    def __init__(self, song_parser):
        
        self.song_parser = song_parser # Vital, essential! 


    def detect_input_mode(self, song_lines):
        """
        Attempts to detect input musical notation for the textual song in 'song_lines'.
        Returns a list with the probable input modes (eliminating the least likely)
        """

        try:
            json_dict = json.loads(song_lines[0])
            json_dict[0]['songNotes']
            return [InputMode.SKYJSON]
        except (json.JSONDecodeError, NameError, TypeError):
            pass        
        
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
            song_lines = song_lines.split(os.linesep)

        song_parser = self.song_parser

        possible_modes = [mode for mode in InputMode if mode is not InputMode.SKYJSON]
        possible_parsers = [song_parser.get_note_parser(mode) for mode in possible_modes]
        possible_regex = [parser.single_note_name_regex for parser in possible_parsers]

        good_notes = [0] * len(possible_modes)
        num_notes = [0] * len(possible_modes)
        defg_notes = 0
        qwrt_notes = 0
        octave_span = 0

        for line in song_lines:
            line = song_parser.sanitize_line(line)
            if len(line) > 0:
                if line[0] != song_parser.comment_delimiter:
                    icons = song_parser.split_line(line)
                    for icon in icons:
                        chords = song_parser.split_icon(icon)
                        for chord in chords:
                            for idx, possible_mode in enumerate(possible_modes):

                                if 'chords' in possible_parsers[idx].__dict__.keys():
                                    notes = [chord]  # Because abbreviated chord names are not composed of note names
                                    good_notes[idx] += sum(
                                        [int(note in possible_parsers[idx].chords.keys()) for note in notes])
                                else:
                                    _, notes = song_parser.split_chord(chord, possible_parsers[idx])
                                    good_notes[idx] += sum(
                                        [int(possible_regex[idx].match(note) is not None) for note in notes if
                                         note != song_parser.pause])
                                # TODO: use self.map_note_to_position?

                                num_notes[idx] += sum([1 for note in notes if note != song_parser.pause])

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
        
        return self.most_likely(scores, possible_modes, 0.9)


    def find_key(self, song_lines):
        """
        Attempts to find the musical key for the textual song in 'input_lines'.
        Requires knoledge of the musical notation (input_mode) first.
        """
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
            song_lines = song_lines.split(os.linesep)

        song_parser = self.song_parser
        note_parser = song_parser.get_note_parser()

        try:
            possible_keys = [k for k in note_parser.CHROMATIC_SCALE_DICT.keys()]
            if len(possible_keys) == 0:
                return None 
            is_note_regex = note_parser.note_name_regex
            not_note_regex = note_parser.not_note_name_regex
        except AttributeError:
            # Parsers not having a chromatic scale keys should return None, eg Sky and Skykeyboard
            return None
        
        scores = [0] * len(possible_keys)
        num_notes = [0] * len(possible_keys)
        for line in song_lines:
            if len(line) > 0:
                if line[0] != song_parser.comment_delimiter:
                    notes = is_note_regex.sub(' \\1',
                                              not_note_regex.sub('', line)).split()  # Clean-up, adds space and split
                    for i, k in enumerate(possible_keys):
                        for note in notes:
                            num_notes[i] += 1
                            try:
                                # TODO: Support for Jianpu which uses a different octave indexing system
                                note_parser.calculate_coordinate_for_note(note, k, note_shift=0,
                                                                               is_finding_key=True)
                            except KeyError:
                                scores[i] += 1
                            except SyntaxError:  # Wrongly formatted notes are ignored
                                num_notes[i] -= 1

        num_notes = [1 if x == 0 else x for x in num_notes]
        # Removes zeros to avoid division by zero
        scores = list(map(truediv, scores, num_notes))
        scores = [(1 - score) for score in scores]

        return self.most_likely(scores, possible_keys, 0.9, note_parser.CHROMATIC_SCALE_DICT)


    def most_likely(self, scores, items, threshold=0.9, duplicates_dict=None):
        """
        Returns the items with scores above threshold, removing duplicates defined in the dict       
        
        """
        if len(scores) == 0:
            return None
        if len(scores) == 1:
            return [items[0]]

        sorted_idx, sorted_scores = zip(
            *sorted([(i, e) for i, e in enumerate(scores)], key=itemgetter(1), reverse=True))

        sorted_items = [items[i] for i in sorted_idx]

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

