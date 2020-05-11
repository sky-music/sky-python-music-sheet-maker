# sky-python-music-sheet-maker

## NOTICE:

This program is not being actively maintained by Tracey. Feel free to take the code/ideas and build upon it.

***

The script requires Python >= 3.6 and the following packages:
* pillow (PIL)
* import_resources (for Python < 3.7)
* mido (optional: for generating midi output)

See here for how to download and use. This currently requires a Desktop computer and is a work-in-progress.

**Instructions:** https://sky.bloomexperiment.com/t/sky-python-music-sheet-maker/102#how-to-download

![Flower Dance intro music sheet](https://raw.githubusercontent.com/sky-music/sky-python-music-sheet-maker/master/images/flower_dance_intro.png)

This program lets you make visual music sheets for Sky: Children of the Light. It is written in Python and does not require previous knowledge of the command line to run. 

As well as using QWERT ASDFG ZXCVB keys as the keyboard, there are other supported notations:

- Sky notation (A1 A2 A3 A4 A5, B1 B2 B3 B4 B5, C1 C2 C3 C4 C5)
- English notation (C4, D4, E4, F4, G4, A4, B4)
- Jianpu (1 2 3 4 5 6 7, followed by + or - for octaves)
- French do ré mi
- Japanese do ré mi

You can type these in the command line, or save in a text file and import it. 

The output will be HTML, with small icons of the Sky keyboard. If you use Western notation or Jianpu notation, it will also convert to Sky notation for you in a txt file.

***

**Co-authors:** Tracey L, jmmelko

SVG icons are thanks to [madwurmz](http://madwurmz.com).

**Translators:**

- jdewfiez (Vietnamese)
- jmmelko (French)

***

Website with music sheets made using this program: https://sky-music.github.io
