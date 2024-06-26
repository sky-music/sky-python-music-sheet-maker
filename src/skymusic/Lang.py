import os, re, yaml
import locale as localepy

LANG_ROOT = os.path.join(os.path.dirname(__file__), "langs")
locales = ['en_US', 'fr_FR', 'vi_VN', 'zh_HANS']
substitutes = {'fr': 'fr_FR', 'en': 'en_US', 'vn': 'vi_VN', 'zh': 'zh_HANS', 'zh_CN': 'zh_HANS'}

'''Unicode ranges for non Asian characters'''
CHAR_RANGES = {'el': [0x370, 0x3ff], 'pl': [0x0, 0x24b], 'ar': [0x600, 0x7ff], 'he': [0x591, 0x5f4], 'th': [0xe01, 0xe5b],'ru': [0x400, 0x527], 'uk': [0x400, 0x527], 'hy': [0x531, 0x58a], 'ka': [0x10a0, 0x10fc]}

LANG = dict()
loaded = dict((locale, False) for locale in locales)
warn_count = 0

def family_from_text(text):
    '''Determines locale prefix from some text, analysing unicode characters positions'''
    m = 0
    text = re.sub('[^\w]+','',text) #Remove non-word characters
    text = re.sub('[A-Za-z]+','',text) #Removes letters, including accented ones, keeping accents isolated, to move average away from zero
    if not text:
        m = 0
        return ''
    else:
        m = sum([int(ord(c)) for c in text])/len(text)
        for loc, range in CHAR_RANGES.items():
            if m>range[0] and m<range[1]:
                return loc.lower()
    return ''
        

def sanitize_locale(locale):
    '''Sanitization: correct case and replacement of - in case the locale is a IETF language tag'''
    matchobj = re.match(r'([^_-]*)[_|-]*([^_-]*)', locale.strip())
    locale = '_'.join(filter(None,(matchobj.group(1).lower(), matchobj.group(2).upper())))
    return locale
    
def get_locale_family(locale):
    
    matchobj = re.match(r'([^_-]*)[_|-]*([^_-]*)', locale.strip())
    if matchobj:
        family = matchobj.group(1).lower()
    else:
        family = ''
    return family

def check_locale(locale):
    try:
        locale = locale.split('.')[0]
        if len(locale) < 2:
            return None
    except AttributeError:
        print(f"\n***WARNING: locale code '{locale}' too short")
        return None

    locale = sanitize_locale(locale)

    if locale not in locales:
        substitute = find_substitute(locale)
        if not loaded[substitute]:
            print(f"\n***WARNING: locale '{locale}' not found. Will replace with '{substitute}'")
        return substitute

    return locale


def guess_locale():
    try:
        import ctypes
        windll = ctypes.windll.kernel32
        windll.GetUserDefaultUILanguage()
        locale = localepy.windows_locale[windll.GetUserDefaultUILanguage()]
    except:
        locale = localepy.getdefaultlocale()[0]
        if locale is None:
            return locales[0]
        elif len(locale) < 2:
            return locales[0]
    
    return locale


def load(locale):
    global LANG, loaded
    
    file_path = os.path.join(LANG_ROOT, "%s.yaml" % locale)
    
    if not os.path.isfile(file_path):
        print(f"\n***WARNING: missing .yaml file for locale '{locale}'. Replacing with {locales[0]}")        
        file_path = os.path.join(LANG_ROOT, "%s.yaml" % locales[0])
    
    with open(file_path, mode='r', encoding='utf-8', errors='ignore') as file:
        LANG[locale] = yaml.safe_load(file)
            
    loaded[locale] = True
    
    return locale


def find_substitute(locale):
    global substitutes

    try:
        locale_radix = locale.split('_')[0]
    except AttributeError:
        return locales[0]

    try:
        return substitutes[locale_radix]
    except KeyError:
        for locale in locales:
            if re.match(locale_radix, locale) is not None:
                substitutes.update({locale_radix: locale})
                return substitutes[locale_radix]
        return locales[0]


def get_string(key, locale=None, replacements=()):
    global locales, warn_count
    if not locale in locales:
        substitute = find_substitute(locale)
        if not loaded[substitute]:
            print(f"\n***WARNING: missing locale '{locale}' for key '{key}'. Replacing with {substitute}")
        locale = substitute

    if not loaded[locale]:
        load(locale)

    key_list = key.split("/")
    obj = LANG[locale]

    for i in key_list:
        if not (i in obj):
            if warn_count < 10:
                print(f"\n***WARNING: could not find lang key '{i}' for locale '{locale}'")
                warn_count += 1
            return ''
            # raise KeyError(f"Unknown lang key: {i}")

        if obj[i] is None:
            return ''
        elif isinstance(obj[i], str):
            if len(replacements) != 0:
                return obj[i].format(*replacements)
            else:
                return obj[i]
        elif isinstance(obj[i], dict):
            obj = obj[i]
