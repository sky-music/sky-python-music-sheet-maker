from setuptools import setup, find_packages

PKG = 'skymusic'  # root package name; should have a directory

long_description = '''
A tool to generate sheet music for the game
[Sky](https://thatgamecompany.com/sky/).
Instructions are available at the project homepage.
'''

setup(
    name='Sky Music Sheet Maker',
    description='Make visual music sheets for thatskygame',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Tracey',
    maintainer_email='bloomexperimentxx@gmail.com',

    url='https://sky.bloomexperiment.com/t/sky-python-music-sheet-maker/102',
    project_urls={
        'Source': 'https://github.com/sky-music/sky-python-music-sheet-maker',
    },

    license='MIT',

    # This option breaks some parts of setuptools, so it won't actually work.
    # The solution is to put the Python code in a properly-named package
    # directory.
    #package_dir={PKG: 'python'},  # The root package is in `python/`.

#    packages=[
#        PKG,
#        # Collect any subpackages and add the root package (there aren't any on
#        # master, but there are some on the dev branch).
#        *('{PKG}.{}'.format(pkg, PKG=PKG) for pkg in find_packages()),
#    ],

    python_requires='>=3.6',  # 3.6 if we use f-strings, which I want.
    install_requires=[
        'Pillow',
        'mido',
    ],

    entry_points={
        # This entry point is no longer valid on the dev branch.
        # It makes a script called 'skymusic' that runs skymusic.main.main().
        'console_scripts': [
            '{PKG} = {PKG}.main:command_line_player'.format(PKG=PKG),
        ],
    },

    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Multimedia :: Sound/Audio :: Editors',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'Topic :: Games/Entertainment',
        ],
)
