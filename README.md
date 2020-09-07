# sky-python-music-sheet-maker
***
This program lets you make visual music sheets for Sky: Children of the Light. It will ask you a few questions, and does not require previous knowledge of the command line to run. 

More details at the [Sky-Music website] (https://sky-music.github.io).

## Installation

The program requires Python >= 3.6 and the following packages:

* pillow (PIL)
* import_resources (for Python < 3.8)
* pyYaml
* mido (optional: for generating midi output)
* requests (optional: for generating a link to skymusic.herokuapp.com)

The program can be installed by simply unzipping the code on your computer, and running the main script file, or by installing it in your Python distribution with pip: `pip install .`

The program can be installed on a desktop computer,  or a smartphone if a Python IDE is installed (such as [Pythonista] (http://omz-software.com/pythonista/)).

See [here] (https://sky-music.github.io/make-your-own-sheet.html) for further details on how to download and install.

## Plug-and-play versions

If you’re afraid of the command line, there is a [website] (https://jmmelko.pythonanywhere.com) running this script.
There is also a bot running an older version of the program, on thatskygame Discord server, that can be called by typing `!song` in a channel.
Executable binaries are also available for download at <https://sky-music.github.io>.

## Running the script

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

## Advanced functions

In contrast with the website or bot versions, the command-line version supports functions for faster processing of songs:

* the default answer to any question can be put in the *skymusic\_preferences.yaml* file. This way, you will no longer be asked this question (for instance the aspect ratio of the visual sheet). You can  even put the notes in there! 
* songs can be processed in a batch by placing preference-like *.yaml* files in the *batch\_songs* directory (see the example files in this folder to learn the right keywords) and modifying the following line in  *command\_line\_player.py*:

        BATCH_MODE = True
* Visual sheets generated after July, 2020 1st can be read again by the program for further modification.

By default, conversion of the song to a music recording using JSON format is disabled. to enable it change the following line:

    SKYJSON_URL = True

You can also change the names of the directories in which the songs are read and written, by modifying `SONGS_DIR_IN` and `SONGS_DIR_OUT`.

***

## Docker images

Since it might be a bit difficult to ensure that all client python3 installations are functional and reproducible, there is a Dockerfile and Compose file provided. The Dockerfile contains the instructions to assemble a basic image to run skymusic, while the Compose file orchestrate the instructions to run the image.

The prebuilt containers have the basis skymusic modules included. `INPUT_DIR` specifies where the container will look for song inputs. 'OUTPUT_DIR' is where the container will output generated music sheets.

1. [Install Docker](https://docs.docker.com/get-docker/)
2. [Install Docker Compose](https://docs.docker.com/compose/install/)
3. Run the skymusic script

```sh
INPUT_DIR=/path/to/dir/containing/test/songs \
OUTPUT_DIR=/path/to/output/dir/ \
docker-compose run skymusic
```

After running, the output will be placed in `/tmp/output/`, referring to the path inside the container. Your `OUTPUT_DIR` is bind mounted to `/tmp/output`.

The first time you execute the above command, Docker will pull the image from the Docker Registry and cache it. Any subsequent runs will utilize the cached image.
Note this is a development image with all optional dependencies included.

***

**Co-authors:** Tracey L, jmmelko

SVG icons are thanks to [madwurmz](http://madwurmz.com).
Advices taken from Specy, Jurassimok, Skyventuree.
Docker images by heronwr aka lambdaw.

**Re-use and branching:**

This program is not being actively maintained by its original creator Tracey. Assistance is currently provided by jmmelko, but this may not last. Feel free to branch the code and build upon it.

**Translators:**

- jdewfiez (Vietnamese)
- jmmelko (French)
- Kai00 (simplified chinese)
- we are looking for a japanese translator

***
