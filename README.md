# sky-python-music-sheet-maker

This program lets you make visual music sheets for Sky: Children of the Light. It will ask you a few questions, and does not require previous knowledge of the command line to run.

More details at the [Sky-Music website](https://sky-music.github.io).

## Table of contents

<!--ts-->
* [Usage](#usage)
    * [Installation](#setup)
    * [Plug-and-play](#plugnplay)
    * [Command line](#running)
* [Configurations](#configs)
    * [Advanced usage](#functions)
    * [Docker images](#docker)
* [Credits](#credits)
    * [Authors](#authors)
    * [Contributors](#contributors)
* [Info](#info)
    * [License](#license)
    * [Code of conduct](#code-of-conduct)
    * [Contributing](#contrib)
<!--te-->

<a id="usage"></a>
## Usage

<a id="setup"></a>
### Installation

The program requires Python >= 3.6 and the following packages:

* pillow (PIL)
* import_resources (for Python < 3.8)
* pyYaml
* mido (optional: for generating midi output)
* requests (optional: for generating a link to skymusic.herokuapp.com)

The program can be installed by simply unzipping the code on your computer, and running the main script file, or by installing it in your Python distribution with pip: `pip install .`

The program can be installed on a desktop computer,  or a smartphone if a Python IDE is installed (such as [Pythonista](http://omz-software.com/pythonista/)).

The program can also be installed in a virtualenv to mitigate possible dependency clashes with system site-packages.

```sh
git clone https://github.com/sky-music/sky-python-music-sheet-maker.git
cd sky-python-music-sheet-maker
python3 -m venv --clear venv
source venv/bin/activate
pip3 install -r requirements.txt
```

You can activate the virtual environment with `source venv/bin/activate`, to exit the virtual enviroment use the `deactivate` command. Note, it is possible some packages are distributed via `bdist_wheel`, hence the wheel package may be required.

See [here](https://sky-music.github.io/make-your-own-sheet.html) for further details on how to download and install.

***

<a id="plugnplay"></a>
### Plug-and-play versions

If you’re afraid of the command line, there is a [website](https://jmmelko.pythonanywhere.com) running this script.
There is also a bot running an older version of the program, on thatskygame Discord server, that can be called by typing `!song` in a channel.
Executable binaries are also available for download at <https://sky-music.github.io>.

***

<a id="running"></a>
### Running the script

    python <path to installation folder>/sky-python-music-sheet-maker/src/skymusic/command_line_player.py

If you have installed the program by pip, just type: `skymusic` instead.

![Flower Dance intro music sheet](https://raw.githubusercontent.com/sky-music/sky-python-music-sheet-maker/master/images/flower_dance_intro.png)

As well as using QWERT ASDFG ZXCVB keys on the keyboard (like a piano), there are other supported notations for the notes you provide:

- Sky column/row notation (A1 A2 A3 A4 A5, B1 B2 B3 B4 B5, C1 C2 C3 C4 C5)
- English notation, followed by an optional number for octaves (C1, D1, E1, F1, G1, A1, B1)
- Jianpu (1 2 3 4 5 6 7, followed by + or - for octaves)
- French do ré mi + octave number
- Japanese do ré mi + octave number

You can type these directly in the command line prompt, but you are strongly advised to save the notes first in a text file. Text files are looked for by the program in the 'test_songs' folder. if you installed the program with pip, this folder must be moved in the Documents folder of your user home directory.

The output will be HTML, SVG, or PNG, with small icons of the Sky keyboard. If you use Western notation or Jianpu notation, it will also convert to Sky notation in a text file.

After generating a sheet, you are encouraged to publish the file on https://sky-music.github.io

<a id="configs"></a>
## Configurations

<a id="functions"></a>
### Advanced usage

In contrast with the website or bot versions, the command-line version supports functions for faster processing of songs:

* the default answer to any question can be put in the *skymusic\_preferences.yaml* file. This way, you will no longer be asked this question (for instance the aspect ratio of the visual sheet). You can  even put the notes in there!

* songs can be processed in a batch by placing preference-like *.yaml* files in the *batch\_songs* directory (see the example files in this folder to learn the right keywords) and passing the following flag to  *command\_line\_player.py*:

        -b/--batch_mode

* Visual sheets generated after July, 2020 1st can be read again by the program for further modification. You will have to enter the artist again though.

Customized configrations for default directory are supported via command line flags, flags that are not passed or are not valid will reference their default fallback vaules defined in *command\_line\_player.py*:

* input/output directories where the module will read from/write to can be defined by passing the following flag with the desired directory to *command\_line\_player.py* respectively:

        --in_dir <path/to/input/dir/>
        --out_dir <path/to/output/dir>

* a custom batch directory for storing preference *.yaml* files can be defined by passing the following flag with the desired directory to *command\_line\_player.py*:

        --batch-dir <path/to/batch/dir>

* the default preference *.yaml* file path where *command\_line\_player.py* reads from can be modified by passing the follow flag with the desired path:

        -p/--pref_file <path/to/pref/file>

* by default, conversion of the song to a music recording using JSON format is disabled. a link to hear the song being played on https://sky-music.herokuapp.com will be generated, to enable it setting the following flag:


        -r/--json_recording

Note that to minimize strain to the skymusic node server, the `-r/--json_recording` and `-b/--batch_mode` flags are mutually exclusive, meaning that only either one of them can be passed to the module but not both. Further help can be invoked via the `-h/--help` flag.

Note: json recording feature requires the `requests` library, which can be installed via the `pip` package manager by running:

    pip install requests

***

<a id="docker"></a>
### Docker images

Since it might be a bit difficult to ensure that all client python3 installations are functional and reproducible, there is a Dockerfile and Compose file provided. The Dockerfile contains the instructions to assemble a base image to run skymusic, while the Compose file orchestrate the instructions to run the image.

The prebuilt containers have the base skymusic modules included. `INPUT_DIR` specifies where the container will look for song inputs. `OUTPUT_DIR` is where the container will output generated music sheets.

1. [Install Docker](https://docs.docker.com/get-docker/)
2. [Install Docker Compose](https://docs.docker.com/compose/install/)
3. Run the skymusic module

```sh
INPUT_DIR=/path/to/dir/containing/test/songs \
OUTPUT_DIR=/path/to/output/dir/ \
docker-compose run skymusic
```

After running, the output will be placed in `/tmp/output/`, referring to the path inside the container. Your `OUTPUT_DIR` is bind mounted to `/tmp/output`.

The first time you execute the above command, Docker will pull the image from the Docker Registry and cache it. Any subsequent runs will utilize the cached image.
Note this is a development image with all optional dependencies included.

<a id="credits"></a>
## Credits

<a id="authors"></a>
### Authors

**Co-authors:** Tracey L, jmmelko

***

<a id="contributors"></a>
### Contributors

**Assets:**

SVG icons are thanks to [madwurmz](http://madwurmz.com).

**Codebase:**

Advices taken from Specy, Jurassimok, Skyventuree.

Docker images by heronwr aka lambdaw.

**Re-use and branching:**

This program is not being actively maintained by its original creator Tracey. Assistance is currently provided by jmmelko, but this may not last. Feel free to branch the code and build upon it.

**Translators:**

- jdewfiez (Vietnamese)
- jmmelko (French)
- Kai00 (simplified chinese)
- we are looking for a japanese translator

<a id="info"></a>
## Info

<a id="license"></a>
### License

```
MIT License

Copyright (c) 2019 Tracey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

***

<a id="code-of-conduct"></a>
### Code of conduct

We use an adapted version of the Contributor Covenant Code of Conduct, please see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for more details.

***

<a id="contrib"></a>
### Contributing

There are several domain-specific guidelines for contributions, largely dealing with the previously established structure of the repo. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.
