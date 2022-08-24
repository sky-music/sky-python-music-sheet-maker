"""
A collection of file utilities for the Music Sheet Maker
"""
import os, re

BINARY_EXT = ('.bin',)

def shortest_path(path, start_path):
    """Finds the shortest path expression from 'path', to startpath"""
    abs_path = os.path.abspath(path)

    try:
        relpath = os.path.relpath(path,start=start_path)
    except ValueError:
        relpath = abs_path

    try:
        home_relpath = os.path.relpath(path,start=os.path.expanduser("~"))
    except ValueError:
        home_relpath = abs_path

    return sorted([relpath,abs_path,home_relpath],key=len)[0]


def file_status(file_path):
    """Returns an integer depending on file statis"""
    isfile = os.path.isfile(file_path)

    if isfile:
        isfile=1 #Definitely a file in the filesystem
    else:
        bare_ext = os.path.splitext(file_path)[1].strip('.')
        if not bare_ext.startswith(' ') and (2 <= len(bare_ext) <= 4):
            isfile = -1 # maybe a file, but path is invalid (typo)
            closest = closest_file(file_path)
            if closest:
                (file_path, isfile) = (closest, 1)
        else:
            isfile = 0 #Not a file attempt
            
    return (file_path, isfile)


def read_file(file_path, binary_ext=BINARY_EXT):
    """Read a file in binary or text mode, depending on file extension."""
    isfile = os.path.isfile(file_path)
    
    _, ext = os.path.splitext(file_path)
    
    if not isfile:
        raise FileNotFoundError("File does not exist: %s" % os.path.abspath(file_path))
    else:
        # load file
        try:
            if ext in set(binary_ext+BINARY_EXT):
                with open(file_path, mode='rb') as fp:
                    lines = fp.readlines()  # Returns a list of bytes
            else:
                with open(file_path, mode='r', encoding='utf-8', errors='ignore') as fp:
                    lines = fp.readlines()  # Returns a list of strings
        except (OSError, IOError) as err:
            raise err

        return lines

def closest_file(filepath):
    
    filedir, filename = os.path.split(filepath)
    
    best_file = None
    best_score = 1
    for (root, dirs, files) in os.walk(filedir):
        for file in files:
            d = edit_distance(file,filename)
            if d < 0.15:
                if d < best_score:
                    best_file = os.path.join(root, file)
                    best_score = d
                
    return best_file   

#% Levenshtein
def __memoize__(func):
    mem = {}
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]
    return memoizer

@__memoize__
def __levenshtein__(s, t):
    if s == "":
        return len(t)
    if t == "":
        return len(s)
    if s[-1] == t[-1]:
        cost = 0
    else:
        cost = 1
    
    res = min([__levenshtein__(s[:-1], t)+1,
               __levenshtein__(s, t[:-1])+1, 
               __levenshtein__(s[:-1], t[:-1]) + cost])

    return res
    
def edit_distance(s, t):

    return __levenshtein__(s,t)/max(len(s),len(t))
