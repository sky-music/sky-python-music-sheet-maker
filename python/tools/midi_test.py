#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 11:11:46 2019

@author: lagaffe
"""
import mido
import re
from math import log

# from mido import Message, MidiFile, MidiTrack, MetaMessage

mid = mido.MidiFile(type=0)
track = mido.MidiTrack()
mid.tracks.append(track)
tempo = mido.bpm2tempo(120)
sec = mido.second2tick(1, ticks_per_beat=mid.ticks_per_beat, tempo=tempo)


def note_to_pitch(note='A4'):
    A4freq = 440
    scale_sharps = ['C', 'C#', 'D', 'D#', 'E', 'F', 'G', 'G#', 'A', 'A#', 'B']
    scale_flats = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'G', 'Ab', 'A', 'Bb', 'B']

    octave = re.search('\d', note)
    if octave is not None:
        octave = int(octave.group())
    else:
        octave = 4
    note_name = re.match('[CDEFGAB][#b]?', note)

    if note_name is not None:
        note_name = note_name.group()
    else:
        return None

    pos = None
    try:
        pos = scale_sharps.index(note_name)
    except ValueError:
        try:
            pos = scale_flats.index(note_name)
        except ValueError:
            return None

    n = pos - scale_sharps.index('A')
    if n < 0:
        n += 12

    fn = 2 ** (n / 12) * A4freq
    m = int(12 * log(fn / A4freq, 2) + 69)

    return m


note_duration = 1 * sec

track.append(mido.MetaMessage('key_signature', key='C'))
track.append(mido.MetaMessage('set_tempo', tempo=tempo))
# track.append(mido.Message('program_change', program=12, time=0))
t = 1 * sec
track.append(mido.Message('note_on', note=60, velocity=127, time=int(t)))
track.append(mido.Message('note_on', note=64, velocity=127, time=0))
track.append(mido.Message('note_off', note=60, velocity=127, time=int(note_duration)))
track.append(mido.Message('note_off', note=64, velocity=127, time=0))

mid.save('new_song.mid')
