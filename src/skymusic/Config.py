#!/usr/bin/env python3
import argparse
import os
import sys
import pathlib

def parse_args(args=None):
    parser = argparse.ArgumentParser()
    # set batch mode and json recording uploads mutually exclusive to avoid strains on the server
    mgroup = parser.add_mutually_exclusive_group()
    mgroup.add_argument(
        "-b",
        "--batch_mode",
        action="store_true",
        help="enable batch processing of preference .yaml files in the batch_dir"
    )
    mgroup.add_argument(
        "-u",
        "--skyjson_url",
        nargs="?",
        const=True,
        help="enable conversion of the song to a recording stored in JSON format using the API key of sky-music.herokuapp.com"
    )
    parser.add_argument(
        "--batch_dir",
        nargs="?",
        const="",
        help="set the batch song preference processing directory, defaults to batch_songs"
    )
    parser.add_argument(
        "-p",
        "--pref_file",
        nargs="?",
        const="",
        help="set the default song preference file, defaults to `skymusic_preferences.yaml`"
    )
    parser.add_argument(
        "--in_dir",
        nargs="?",
        const="",
        help="set the input directory for song processing, defaults to `test_songs`"
    )
    parser.add_argument(
        "--out_dir",
        nargs="?",
        const="",
        help="set the output directory for song processing, defaults to `songs_out`"
    )

    try:
        if args is None:
            return parser.parse_args()
        else:
            return parser.parse_args(args)

    except (ValueError, TypeError) as err:
        print(str(err))
        sys.exit(2) # On Unix, exit status 2 is used for command line syntax errors

def verify_path(path, prop="dir"):
    # workaround wrapper for storing methods in a dict() structure
    # probably should catch AttributeError or TypeError
    plookup = {
        "dir" : lambda x: x.is_dir(),
        "file" : lambda x: x.is_file(),
        "mount" : lambda x: x.is_mount(),
        "symlink" : lambda x: x.is_symlink(),
        "block" : lambda x: x.is_block_device(),
        "char" : lambda x: x.is_char_device()
    }

    if path is None:
        return None

    try:
        normpath = pathlib.Path(os.path.normcase(path)).resolve()

        # structure needs revising
        if not normpath.exists():
            print("**ERROR: the path passed to Config: {:s} is either not valid or access permission is denied".format(str(normpath)))
            sys.exit(2)
        elif normpath.is_reserved():
            # check if the path object is reserved under Windows, performing file operations can have side effects on reserved paths
            print("**ERROR: the path passed to Config: {:s} is a reserved path".format(str(normpath)))
            sys.exit(2)
        elif not plookup[prop](normpath):
            print("**ERROR: the path passed to Config: {:s} is not the type {:s}".format(str(normpath), prop))
            sys.exit(2)

        return str(normpath)

    except OSError as err:
        print(str(err))
        sys.exit(2)

# pargs - parsed arguments
# args  - unparsed arguments
def get_configuration(pargs):
    config = {
        "pref_file": None,
        "song_dir_out": None,
        "song_dir_in": None,
        "batch_mode": pargs.batch_mode,
        "batch_dir": None,
        "skyjson_url": pargs.skyjson_url
    }

    # re-setting dictionary key-val pairs to perserve NoneType when exception is catched
    config["pref_file"] = verify_path(pargs.pref_file, "file")
    config["song_dir_in"] = verify_path(pargs.in_dir)
    config["song_dir_out"] = verify_path(pargs.out_dir)
    config["batch_dir"] = verify_path(pargs.batch_dir)

    return config

