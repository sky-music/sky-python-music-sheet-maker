import yaml
import os


LANG = dict()
locales = ['en_US', 'ja_JP', 'fr_FR']
loaded = dict((locale, False) for locale in locales)
warn_count = 0
'''
def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)
'''
'''
def load():
    global LANG, loaded
    with open("lang.yaml") as file:
        LANG = yaml.safe_load(file)
    loaded = True
    
def get_string(key, **kwargs):
    if not loaded:
        load()

    key_list = key.split("/")
    obj = LANG
    for i in key_list:
        if i not in obj:
            print('\n***WARNING: could not find lang key {%s}\n'%str(i))
            return ''
            #raise KeyError(f"Unknown lang key: {i}")

        if isinstance(obj[i], str):
            return obj[i].format(**kwargs)
        elif isinstance(obj[i], dict):
            obj = obj[i]
'''


def load(locale):
    global LANG, loaded
    with open(os.path.join("python", "langs", "%s.yaml"%locale)) as file:
        LANG[locale] = yaml.safe_load(file)
    loaded[locale] = True


def get_string(key, locale=None, **kwargs):
    global locales, warn_count
    if locale not in locales:
        if not loaded[locales[0]]:
            print('\n***WARNING: bad locale %s for key %s. Reverting to %s\n' % (locale, str(key), locales[0]))
        locale = locales[0]

    if not loaded[locale]:
        load(locale)

    key_list = key.split("/")
    obj = LANG[locale]
    for i in key_list:
        if i not in obj:
            if warn_count < 10:
                print('\n***WARNING: could not find lang key %s for locale %s\n' % (str(i), locale))
                warn_count += 1
            return ''
            # raise KeyError(f"Unknown lang key: {i}")

        if isinstance(obj[i], str):
            return obj[i].format(**kwargs)
        elif isinstance(obj[i], dict):
            obj = obj[i]
