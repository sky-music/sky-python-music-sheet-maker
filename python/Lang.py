import yaml

LANG = dict()
loaded = False

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
            obj = obj[i] #Recursive search of yaml nested dictionaries???
