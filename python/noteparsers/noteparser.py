import re
import math


class NoteParser:
    """
    A generic NoteParser for parsing notes of a major scale, and turning them into the corresponding coordinate on
    Sky's 3*5 piano.
    """

    def __init__(self):

        self.columns = 5
        self.rows = 3

        self.CHROMATIC_SCALE_DICT = {}
        self.SEMITONE_INTERVAL_TO_MAJOR_SCALE_INTERVAL_DICT = {
            0: 0,  # 0 semitones means it’s the root note
            2: 1,  # 2 semitones means it’s a 2nd interval
            4: 2,  # 4 semitones means it’s a 3rd interval
            5: 3,  # 5 semitones means it’s a 4th interval
            7: 4,  # 7 semitones means it’s a 5th interval
            9: 5,  # 9 semitones means it’s a 6th interval
            11: 6  # 11 semitones means it’s a 7th interval
        }

        # Number of notes in the chromatic scale, and number of notes in a major scale
        self.CHROMATIC_SCALE_COUNT = 12
        self.BASE_OF_MAJOR_SCALE = 7

        # Specify the default starting octave of the harp, in this case, it's 4 (C4 D4 E4 etc.)
        self.default_starting_octave = 1

        # Compile regexes for notes to save before using
        # these regexes are used for validating whether an individual note is formatted correctly.
        self.note_name_with_octave_regex = None
        self.note_name_regex = None
        self.note_octave_regex = None

    def get_chromatic_scale_dict(self):

        return self.CHROMATIC_SCALE_DICT

    def get_semitone_interval_to_major_scale_interval_dict(self):

        return self.SEMITONE_INTERVAL_TO_MAJOR_SCALE_INTERVAL_DICT

    def get_chromatic_scale_count(self):

        return self.CHROMATIC_SCALE_COUNT

    def get_column_count(self):

        return self.columns

    def get_row_count(self):

        return self.rows

    def get_default_starting_octave(self):

        return self.default_starting_octave

    def get_base_of_western_major_scale(self):

        return self.BASE_OF_MAJOR_SCALE

    def get_note_name_with_octave_regex(self):

        return self.note_name_with_octave_regex

    def get_note_name_regex(self):

        return self.note_name_regex

    def get_note_octave_regex(self):

        return self.note_octave_regex

    def get_note_name(self, note):

        note_name = self.get_note_name_regex().search(note).group(0)

        return note_name

    def get_note_octave(self, note):

        note_octave = int(self.get_note_octave_regex().search(note).group(0))

        return note_octave

    def is_valid_note_name_with_octave(self, note):

        """
        Return True if note is in the format self.note_name_with_octave_regex, e.g. Ab4, else return False
        """

        note_regexobj = self.get_note_name_with_octave_regex().match(note)

        if note_regexobj:
            return True
        else:
            return False

    def english_note_name(self, note_name, reverse=False):
        from noteparsers import english
        if reverse:
            native_parser = english.English()
            foreign_parser = self
        else:
            native_parser = self
            foreign_parser = english.English()

        note_name = native_parser.note_name_regex.match(str(note_name))
        if note_name is not None:
            note_name = native_parser.sanitize_note_name(note_name.group(0))
        else:
            return None

        try:
            chromatic_value = native_parser.get_chromatic_scale_dict()[note_name]
            foreign_dict = foreign_parser.get_chromatic_scale_dict()
            foreign_note_name = list(foreign_dict.keys())[list(foreign_dict.values()).index(chromatic_value)]
        except:
            foreign_note_name = foreign_parser.note_name_regex.match(str(note_name))
            if foreign_note_name is not None:
                foreign_note_name = foreign_note_name.group(0)
            else:
                foreign_note_name = None

        return foreign_note_name

    def is_valid_note_name(self, note_name):

        """
        Return True if note is in the format self.note_name_regex, else return False
        """

        note_regexobj = self.get_note_name_regex().match(note_name)

        if note_regexobj:
            return True
        else:
            return False

    def parse_note(self, note, song_key, is_finding_key=False):

        """
        Returns a tuple containing note_name, note_name for a note in the format self.note_name_with_octave_regex

        When is_finding_key is True, the handle_note_name_without_octave method should be used
        """

        if self.is_valid_note_name_with_octave(note):
            note_name = self.get_note_name(note)
            note_octave = self.get_note_octave(note)
            return note_name, note_octave
        else:
            if self.is_valid_note_name(note):

                # Player has given note name without specifying an octave
                note_name = note

                if not is_finding_key:

                    note_octave = self.get_default_starting_octave()
                    return note_name, note_octave
                else:
                    return self.handle_note_name_without_octave(note_name, song_key)

            else:
                # Raise error, not a valid note
                raise SyntaxError('Note ' + str(note) + ' was not formatted correctly.')

    def handle_note_name_without_octave(self, note_name, song_key):

        """
        Handle notes specified without octaves (e.g. the note G in the key of Ab)
        """

        note_octave = self.get_default_starting_octave()

        chromatic_interval = self.convert_note_name_into_chromatic_position(
            note_name) - self.convert_note_name_into_chromatic_position(song_key)

        if chromatic_interval < 0:
            note_octave += 1

        return note_name, note_octave

    def convert_note_name_into_chromatic_position(self, note_name):

        """
        Returns the numeric equivalent of the note in the chromatic scale
        """

        if self.is_valid_note_name(note_name):
            note_name = self.sanitize_note_name(note_name)
        else:
            # Error: note is not formatted right, output broken harp
            raise SyntaxError('Note ' + str(note_name) + ' was not formatted correctly.')

        chromatic_scale_dict = self.get_chromatic_scale_dict()

        if note_name in chromatic_scale_dict.keys():
            return chromatic_scale_dict[note_name]
        else:
            raise KeyError('Note ' + str(note_name) + ' was not found in the chromatic scale.')

    def convert_semitone_interval_to_major_scale_interval(self, semitone_interval):

        conversion_dict = self.get_semitone_interval_to_major_scale_interval_dict()

        if semitone_interval in conversion_dict.keys():
            return conversion_dict[semitone_interval]
        else:
            raise KeyError('Interval ' + str(semitone_interval) + ' is not in the major scale.')

    def calculate_coordinate_for_note(self, note, song_key='C', note_shift=0, is_finding_key=False):

        """

        For a note in the format self.note_name_with_octave_regex, this method returns the corresponding coordinate
        on the Sky piano (in the form of a tuple)

        song_key will be determined by the find_keys method, and is expected to match CHROMATIC_SCALE_DICT,
        otherwise the default key will be C. note_shift is the variable set by the user.

        When this method is being used to find the key, `is_finding_key` should be set to True.

        KeyError will be raised if:
        - note is not in the major scale of song key (using the dict)
        - note is not in the chromatic scale (using the dict)
        SyntaxError will be raised if:
        - note is not formatted correctly

        KeyError and SyntaxError can be caught, by any method that calls this one, to output a broken harp
        """

        # Convert note to base 7
        note_name, note_octave = self.parse_note(note, song_key, is_finding_key)

        # Find the major scale interval from the song_key to the note_name
        # Find the semitone interval from the song_key to the note_name first
        if song_key is None:
            song_key = 'C'
        try:
            song_key_chromatic_equivalent = self.convert_note_name_into_chromatic_position(song_key)
        except (KeyError, SyntaxError):
            # default to C major
            song_key_chromatic_equivalent = 0
        try:
            note_name_chromatic_equivalent = self.convert_note_name_into_chromatic_position(note_name)
        except KeyError:
            # will output broken harp
            raise KeyError('Note ' + str(note_name) + ' was not found in the chromatic scale.')
        except SyntaxError:
            raise SyntaxError('Note ' + str(note_name) + ' was not formatted correctly')

        interval_in_semitones = note_name_chromatic_equivalent - song_key_chromatic_equivalent
        if interval_in_semitones < 0:
            # Circular shift the interval back to a positive number
            interval_in_semitones += self.get_chromatic_scale_count()
            note_octave -= 1

        note_octave_str = self.convert_base_10_to_base_7(note_octave)

        try:
            major_scale_interval = self.convert_semitone_interval_to_major_scale_interval(interval_in_semitones)
        except KeyError:
            # Turn note into a broken harp, since note is not in the song_key
            raise KeyError('Note ' + str(note) + ' is not in the song key.')

        # Convert note to base 10 for arithmetic
        note_in_base_10 = self.convert_base_7_to_base_10(note_octave_str + str(major_scale_interval))
        note_in_base_10 -= self.get_base_of_western_major_scale() * self.get_default_starting_octave()

        if self.is_valid_note_name_with_octave(note):
            # Skip the note shift if no octave is specified
            note_in_base_10 += note_shift

        note_coordinate = self.convert_base_10_to_coordinate_of_another_base(note_in_base_10, self.get_column_count())

        if self.is_coordinate_in_range(note_coordinate):
            return note_coordinate
        else:
            # Coordinate is not in range of the two octaves of the Sky piano
            raise KeyError(
                'Note ' + str(note) + ' is not in range of the two octaves of the Sky piano: ' + str(note_coordinate))
            # TODO: define custom errors

    def convert_base_10_to_base_7(self, num):
        n = 3
        numstr = [0] * n
        base = self.get_base_of_western_major_scale()
        for i in range(n - 1, -1, -1):
            numstr[i] = int(num / (base ** i))
            num -= numstr[i] * (base ** i)
        numstr = list(map(str, numstr))
        return ''.join(numstr[::-1]).lstrip('0')

    def convert_base_7_to_base_10(self, num_in_base_7):

        """
        Given a number in base 7 as a string, returns the number in base 10 as an integer.
        """

        num_in_base_10 = int(num_in_base_7, self.get_base_of_western_major_scale())
        return num_in_base_10

    def convert_base_10_to_coordinate_of_another_base(self, num, base):

        """
        Convert a number in base 10 to base `self.columns` (using mod and floor), and return as a tuple
        """

        remainder = num % base
        quotient = math.floor(num / base)

        return quotient, remainder

    def sanitize_note_name(self, note_name):

        # Do any work here to sanitize the note_name so that it matches the keys of self.CHROMATIC_SCALE_DICT

        return note_name

    def is_coordinate_in_range(self, coordinate):

        """

        Returns True if the coordinate is in range of the Sky piano (as defined by self.columns and self.lines),
        return False if not. coordinate is expected to be a tuple.

        """

        if 0 <= coordinate[0] <= self.get_row_count() - 1 and 0 <= coordinate[1] <= self.get_column_count() - 1:
            # Check if the row number and column number of the coordinates are within the instrument's range
            return True
        else:
            return False
