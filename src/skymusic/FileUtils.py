"""
A collection of file utilities for the Music Sheet Maker
"""
import os

BINARY_EXT = ('.bin',)

def shortest_path(path, start_path):
    """Finds the shortest path expression from 'path', to startpath"""
    abs_path = os.pathunicodedata_exists = os.path.abspath(path)

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
    """Returns an integer depending on file status"""
    
    if len(file_path) > 256:
        isfile = 0
    else:
        isfile = os.path.isfile(file_path)
    
        if isfile:
            isfile = 1 # Rigorously a file in the filesystem
        else:
            isfile = -1
            bare_ext = os.path.splitext(file_path)[1].strip('.')
            
            closest, score = closest_file(file_path)
            
            file_suspect = (not bare_ext.startswith(' ') and (2 <= len(bare_ext) <= 4)) # has a file extension, not a pause . followed by a musical note
            
            if closest and (score > 0.8 or (score > 0.6 and file_suspect)):
            
                (file_path, isfile) = (closest, 1) # is a file, but path was invalid (typo)       
            else:
                isfile = 0 # Not a file
            
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
    '''Fuzzy name matching'''
    filedir, filename = os.path.split(filepath)
    
    best_file = None
    best_score = 0
    score_threshold = 0.5
    for (root, dirs, files) in os.walk(filedir):
        for file in files:
            bare_file = __strip_accents__(os.path.splitext(os.path.splitext(file)[0])[0]).lower()
            bare_filename = __strip_accents__(os.path.splitext(os.path.splitext(filename)[0])[0]).lower()
            d = __edit_distance__(bare_file,bare_filename)
            score = 1 - (d/max(len(bare_file),len(bare_filename)))
            #print(f"d({file,filename})={d}")
            if score > score_threshold and score > best_score:
                best_file, best_score = os.path.join(root, file), score
                
    return (best_file, best_score)

#% Levenshtein

def __strip_accents__(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    try:
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
    except NameError:
        accents = {'à':'a','á':'a','â':'a','ä':'a',
                   'é':'e','è':'e','ê':'e','ë':'e',
                   'í':'i','ì':'i','î':'i','ï':'i',
                   'ò':'o','ó':'o','ô':'o','ö':'o',
                   'ù':'u','ú':'u','û':'u','ü':'u',
                   'ç':'c','ñ':'n'}
        for k,v in accents.items(): text = text.replace(k,v)
     
    return str(text)

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
    
def __edit_distance__(s, t):

    try:
        return __levenshtein__(s,t)
    except RecursionError:
        return max(len(s), len(t))
