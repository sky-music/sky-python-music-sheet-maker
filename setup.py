#!/usr/bin/env python3
from setuptools import setup, find_packages

#import src
#from src import skymusic

PKG = 'skymusic'  # root package name; should have a directory

long_description = '''
A tool to generate sheet music for the game
[Sky](https://thatgamecompany.com/sky/).
Instructions are available at the project homepage.
'''

setup(
    name = 'skymusic',
    version = '3.0.2',
    description = 'Make visual music sheets for Sky: Children of The Light',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Tracey',
    author_email = 'bloomexperimentxx@gmail.com',
    maintainer = 'maintainer',
    maintainer_email = 'skymusicwebsite@gmail.com',
    url = 'https://sky-music.github.io',
    download_url = {
        'Source': 'https://github.com/sky-music/sky-python-music-sheet-maker',
    },
    license = 'MIT',
    package_dir = {"": "src"},
    packages = find_packages('src'),
    include_package_data = True,
    package_data = {"": ["*.css", "*.png", "*.otf", "*.svg", "*.yaml", "*.txt", "*.js"],},
    python_requires = '>=3.6',
    install_requires = ['pillow', 'pyyaml', 'importlib_resources;python_version<"3.8"'],
    extras_require = {
        "extra": ["mido>=1.2.9", "requests"]
    },

    entry_points = {
        # This entry point is no longer valid on the dev branch.
        # It makes a script called 'skymusic' that runs skymusic.main.main().
        'console_scripts': [
            '{PKG} = {PKG}.command_line_player:command_line_player'.format(PKG = PKG),
        ],
    },

    classifiers = [
        "Programming Language :: Python",
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Multimedia :: Sound/Audio :: Editors',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'Topic :: Games/Entertainment',
        ],
)
