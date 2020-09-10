#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 19:49:17 2020

@author: lagaffe
"""
import os, sys, re

try:
    this_file = os.path.abspath(__file__)
except NameError:
    this_file = os.path.abspath(sys.argv[0])
    
application_root = os.path.dirname(this_file)


replacements = [('xmlns="https://www.w3.org/2000/svg"',''),
                ('<html>', '<html xmlns:svg="http://www.w3.org/2000/svg" lang="fr_FR">'),
                ('width="1em" height="1em" ',''),
                ('instrument-button-icon', 'icon'),
                ('instrument-button', 'button'),
                ('note-(\w+)', r'\1'),
                ('harp-button', 'button'),
                ('unhighlighted', 'OFF'),
                ('highlighted', 'ON'),
                ('(\s)+', r'\1'),
                (' "', '"')
        
        
        
        
        
        ]

found = False
while not found:
    filepath = input("Relative file path: ")
    filepath = os.path.normpath(os.path.join(application_root, filepath))
    (fileroot, filename) = os.path.split(filepath)
    (basename, extension) = os.path.splitext(filename)
    new_filepath = os.path.join(fileroot, basename + '_converted' + extension)
    
    try:
        with open(filepath, mode='r', encoding='utf-8', errors='ignore') as file:    
            content = file.read()
            found = True
    except FileNotFoundError:
        found = False

for (pattern, repl) in replacements:   
    content = re.sub(pattern, repl, content)
    

with open(new_filepath, mode='w', encoding='utf-8') as file:    
    file.write(content)    