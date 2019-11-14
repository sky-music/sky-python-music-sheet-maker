#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 20:53:30 2019

@author: lagaffe
"""
import os
import re

from cairosvg import svg2png

os.chdir(".")

for file_path in os.listdir():
    
    (name, ext) = os.path.splitext(file_path)
    if ext == '.svg':
        if name in ['circle-highlighted-n', 'diamond-highlighted-n', 'root-highlighted-n']:
            for i in range(1,7):
                new_name = re.sub('-n','-' + str(i),name)
                new_file=open(new_name + ext, 'w+')
                for line in open(file_path, 'r'):
                    new_file.write(re.sub('highlighted-n','highlighted-' + str(i), line))
                new_file.close()
                svg2png(url=(new_name + ext),write_to=(new_name+'.png'))
        else:
            pass
#            svg2png(url=file_path,write_to=(name+'.png'))
