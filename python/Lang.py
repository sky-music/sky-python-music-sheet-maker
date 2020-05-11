import yaml
import os
import re
import locale as localepy

LANG = dict()
locales = ['en_US', 'ja_JP', 'fr_FR', 'vi_VN']
substitutes = {'fr': 'fr_FR', 'en': 'en_US', 'vn': 'vi_VN'}
loaded = dict((locale, False) for locale in locales)
warn_count = 0


def check_locale(locale):
    try:
        locale = locale.split('.')[0]
        if len(locale) < 2:
            return None
    except AttributeError:
        return None

    locale = locale.replace('-', '_')  # In case the locale is a IETF language tag

    if locale not in locales:
        substitute = find_substitute(locale)
        if not loaded[substitute]:
            print("\n***WARNING: locale '%s' not found. Will replace with '%s'\n" % (locale, substitute))
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
    with open(os.path.normpath(os.path.join(os.path.dirname(__file__), "langs", "%s.yaml" % locale)), mode='r', encoding='utf-8', errors='ignore') as file:
        LANG[locale] = yaml.safe_load(file)
    loaded[locale] = True


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
    if locale not in locales:
        substitute = find_substitute(locale)
        if not loaded[substitute]:
            print(
                "\n***WARNING: missing locale '%s' for key '%s'. Replacing with %s\n" % (locale, str(key), substitute))
        locale = substitute

    if not loaded[locale]:
        load(locale)

    key_list = key.split("/")
    obj = LANG[locale]

    for i in key_list:
        if i not in obj:
            if warn_count < 10:
                print("\n***WARNING: could not find lang key '%s' for locale '%s'\n" % (str(i), locale))
                warn_count += 1
            return ''
            # raise KeyError(f"Unknown lang key: {i}")

        if isinstance(obj[i], str):
            if len(replacements) != 0:
                return obj[i].format(*replacements)
            else:
                return obj[i]
        elif isinstance(obj[i], dict):
            obj = obj[i]
