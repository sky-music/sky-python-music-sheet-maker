# -*- coding: utf-8 -*-
import os, re
from operator import truediv, itemgetter
from collections import OrderedDict
from skymusic.modes import InputMode
from skymusic.parsers.html_parser import HtmlSongParser

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
        from skymusic.parsers import json_parser, midi_parser
        
        song_parser = self.song_parser
        #all_modes = [mode for mode in InputMode]
        
        is_midi = midi_parser.MidiSongParser(maker=self.song_parser.get_maker()).detect_midi(song_lines[0], strict=True)        
        if is_midi:
            return [InputMode.MIDI]
        
        jsonparser = json_parser.JsonSongParser(maker=self.song_parser.get_maker())        
        json_dict = jsonparser.load_dict(song_lines[0])     
        if json_dict:
            return [InputMode.SKYJSON]
                
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a list
            song_lines = song_lines.split(os.linesep)

        is_html = HtmlSongParser().detect_html(song_lines)
        if is_html:
            return [InputMode.SKYHTML]

        possible_modes = [mode for mode in InputMode if mode not in [InputMode.SKYJSON, InputMode.SKYHTML, InputMode.MIDI]]
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
                if line[0] != song_parser.lyric_delimiter:
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
        from skymusic.parsers import midi_parser
        
        if isinstance(song_lines, str):  # Break newlines and make sure the result is a List
            song_lines = song_lines.split(os.linesep)
        
        midi_song_parser = midi_parser.MidiSongParser(maker=self.song_parser.get_maker())
        is_midi = midi_song_parser.detect_midi(song_lines)
        if is_midi:
            song_key = midi_song_parser.find_key(song_lines)
            if song_key:
                return song_key
            else:
                song_lines = midi_song_parser.collect_notes(song_lines)
                if not song_lines:
                    return None
        
        song_parser = self.song_parser
        note_parser = song_parser.get_note_parser()
        is_note_regex = note_parser.note_name_regex
        not_note_regex = note_parser.not_note_name_regex

        try:           
            chromatic_dict = note_parser.CHROMATIC_SCALE_DICT
            if not chromatic_dict:
                return None #When case note_parser is undefined, default chromatic_dict is empty
        except AttributeError:
            # Parsers not having a chromatic scale keys should return None, eg Sky and Skykeyboard
            return None       

        # Removing synonyms
        inv_dict = OrderedDict({v: k for k, v in reversed(OrderedDict(chromatic_dict).items())})
        possible_keys = list(reversed(inv_dict.values()))
        
        scores = [0] * len(possible_keys)
        num_notes = [0] * len(possible_keys)
        for line in song_lines:
            if len(line) > 0:
                if line[0] != song_parser.lyric_delimiter:
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

        return self.most_likely(scores, possible_keys, 0.9)


    def most_likely(self, scores, items, threshold=0.9):
        """
        Returns the items with scores above threshold, removing duplicates defined in the dict       
        
        """
        if len(scores) == 0:
            return None
        if len(scores) == 1:
            return [items[0]]

        sorted_idx, sorted_scores = zip(*sorted([(i, e) for i, e in enumerate(scores)],
                                                 key=itemgetter(1), reverse=True))

        sorted_items = [items[i] for i in sorted_idx]

        if sorted_scores[0] == 1 and sorted_scores[1] < 1: # 100% match
            return [sorted_items[0]]

        if sorted_scores[0] == 1 and sorted_scores[1] == 1: # 2 perfect matches: undecidable case
            return [k for i, k in enumerate(sorted_items) if sorted_scores[i] == 1]

        if sorted_scores[0] < threshold: # Best candidate is below threshold
            sorted_items = [k for i, k in enumerate(sorted_items) if sorted_scores[i] > (3/4.0)*threshold]
        else:
            sorted_scores = list(map(truediv, sorted_scores, [max(sorted_scores)] * len(sorted_scores)))
            over_items = [k for i, k in enumerate(sorted_items) if sorted_scores[i] > threshold]
            if len(over_items) != 0:
                sorted_items = over_items

            sorted_items = [item for item in sorted_items if item is not None]

        return sorted_items   
    
    
    def spectrum(self, x, y):
        import cmath
        from math import log, ceil
        
        def omega(p, q):
            return cmath.exp((2.0 * cmath.pi * 1j * q) / p)
        
        def fft(signal):
            n = len(signal)
            if n == 1:
                return signal
            else:
                Feven = fft([signal[i] for i in range(0, n, 2)])
                Fodd = fft([signal[i] for i in range(1, n, 2)])
                combined = [0] * n
                for m in range(n // 2):
                    combined[m] = Feven[m] + omega(n, -m) * Fodd[m]
                    combined[m + n // 2] = Feven[m] - omega(n, -m) * Fodd[m]
            return combined        

        n1 = len(y)
        m = ceil(log(n1)/log(2))
        ffty = fft(y + [0]*(2**m - n1)) #Zero padding to a power of 2 length  
        n2 = len(ffty)
        dx = x[2] - x[1]
        f = [k/(dx*n2) for k in range(int(n2/2))]
        sp = [abs(ffty[k])**2 for k in range(int(n2/2))]
        return f, sp


    def find_peaks(self, x, y, threshold, max_peaks=3, x_bounds = ()):
                
        def find_barycenter(t, z, i0, di):
            while len(t) < 2*di+1:
                di = di - 1
            if di < 0:
                return None
            
            dt = t[1] - t[0]
            tmin = t[0]
            nmax = 10 #max number of iterations to find barycenter
            
            n = 0
            iG = i0
            iG_old = iG - 2 #to enter the loop once
            while (iG-iG_old) > 1 and n < nmax:            
                i1 = max([0,iG-di])
                i2 = min([len(t),iG+di])
                z_band = z[i1:i2+1]
                t_band = t[i1:i2+1]
                iG_old = iG
                tG = sum([z*t for (t,z) in zip(t_band, z_band)])/sum(z_band)
                iG = round((tG - tmin)/dt)
                n += 1        
            return (i1, i2), tG 
        
        def bounds_indices(array, bounds):
            if bounds:
                if bounds[1] > bounds[0]:
                    i1 = next((i for i in range(len(array)) if array[i]>=bounds[0]), None)
                    i2 = next((i for i in reversed(range(len(array))) if array[i]<=bounds[1]), None)
                else:
                    i1 = next((i for i in range(len(array)) if array[i]<=bounds[0]), None)
                    i2 = next((i for i in reversed(range(len(array))) if array[i]>=bounds[1]), None)
            else:
                (i1, i2) = (None, None)
            
            i1 = i1 if i1 else 0
            i2 = i2 if i2 else len(array)-1
            return (i1, i2)
        
        
        div_resol = 3 #precision increase        
        peaks = list() #list of (t,h) tuples
        (i1, i2) = bounds_indices(x, x_bounds)
        
        x2 = x.copy()[i1:i2+1]
        y2 = y.copy()[i1:i2+1]
        
        '''
        import matplotlib.pyplot as plt
        plt.plot(x2, y2)
        plt.xlabel('x2 (filtered)')
        ax = plt.gca()
        ax.set_xscale('log')
        ax.invert_xaxis()
        plt.show()
        '''
        
        for i in range(max_peaks):
            y0 = max(y2)
            if y0 < max(y2)*threshold:
                break
            i0 = y2.index(y0)
            (i1, i2), tG = find_barycenter(x2, y2, i0, div_resol)
            peaks.append((tG, y0))
            y2[i1:i2+1] = [0]*len(y2[i1:i2+1])#peak deletion 
        
        return [delay for (delay, occ) in peaks]

    
    def analyze_tempo(self, times, chord_delay, method='diff'):
        
        def build_histogram(vals, hbin):
            num_slots = 2 + int(max(vals) / hbin)
            h = [0]*num_slots #occurrences
            t = [i*hbin for i in range(num_slots)] #delays
            for v in vals: #histogram starting at t=0
                h[1+int(v/hbin)] += 1
            return (t, h)
        
        #div_resol = 3 #precision increase
        #tbin = chord_delay / div_resol
        tbin = 1
        
        # Typical spacing between two consecutive notes
        dtimes = [times[i] - times[i-1] for i in range(1, len(times))]
        (dt, dh) = build_histogram(dtimes, tbin)
        typ_diffs = self.find_peaks(dt, dh, 1/10, 3)
        typ_diffs = [diff for diff in typ_diffs if diff > 2*tbin]

        if method == 'diff':
            return typ_diffs

        # Notes strokes versus time
        (t, h) = build_histogram(times[:128], tbin)
        f, sp = self.spectrum(t, h)
        f0 = f[1]/2
        taus = [1/(max(x,f0)) for x in f]
        
        min_tau = min(typ_diffs)-tbin # to exclude quavers and quasi-chords
        max_tau = taus[1] # to exclude the zero-frequency component
        
        typ_taus = self.find_peaks(taus, sp, 1/5, 3, (max_tau, min_tau))
        
        #print('%DEBUG')
        #print(typ_diffs)
        #print(typ_taus)
        
        return typ_taus

