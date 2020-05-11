import yaml
import os
import re
loaded = dict((locale, False) for locale in locales)
warn_count = 0

def load():
    with open(os.path.normpath(os.path.join(os.path.dirname(__file__), "..../", "preferences.yaml")), mode='r', encoding='utf-8', errors='ignore') as file:
        LANG[locale] = yaml.safe_load(file)
    loaded[locale] = True


def get_string(key, locale=None, replacements=()):
    global locales, warn_count
    if locale not in locales:
        substitute = find_substitute(locale)
        if not loaded[substitute]:
            print(f"\n***WARNING: missing locale '{locale}' for key '{key}'. Replacing with {substitute}\n")
        locale = substitute

    if not loaded[locale]:
        load(locale)

    key_list = key.split("/")
    obj = LANG[locale]

    for i in key_list:
        if i not in obj:
            if warn_count < 10:
                print(f"\n***WARNING: could not find lang key '{i}' for locale '{locale}'\n")
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
