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
    '''Fuzzy name matching'''
    filedir, filename = os.path.split(filepath)
    
    best_file = None
    best_score = 99
    for (root, dirs, files) in os.walk(filedir):
        for file in files:
            bare_file = __strip_accents__(os.path.splitext(os.path.splitext(file)[0])[0]).lower()
            bare_filename = __strip_accents__(os.path.splitext(os.path.splitext(filename)[0])[0]).lower()
            d = edit_distance(bare_file,bare_filename)
            #print(f"d({file,filename})={d}")
            if d < 3 or (d<4 and len(filename)>10):
                if d < best_score:
                    best_file = os.path.join(root, file)
                    best_score = d
                
    return best_file   

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
    
def edit_distance(s, t):

    return __levenshtein__(s,t)
