# sky-python-music-sheet-maker

See here for how to download and use.

**Instructions:** https://sky.bloomexperiment.com/t/sky-python-music-sheet-maker/102#how-to-download

![Flower Dance intro music sheet](https://raw.githubusercontent.com/sky-music/sky-python-music-sheet-maker/master/images/flower_dance_intro.png)

This program lets you make visual music sheets for Sky: Children of the Light. It is written in Python and does not require previous knowledge of the command line to run. 

SVG icons are thanks to [madwurmz](http://madwurmz.com).

Website with music sheets made using this program: 

https://sky-music.github.io

# Code

https://github.com/sky-music/sky-python-music-sheet-maker

# Templates

![music_sheet_template|690x324](https://sky.bloomexperiment.com/uploads/default/original/1X/228ee908a12320236b4fc07be9fc04005d3c0d8d.png) 

## Template 2
![SKY_MUSIC_SHEET_TEMPLATE|689x319](https://sky.bloomexperiment.com/uploads/default/original/1X/321441f67b523588a1e031c62d475abaf5003a8e.png) 


Templates are free to download and use without credit.

# Examples

[details=Click to expand]

## Chord Chart in C

![ChordChart|429x500](https://sky.bloomexperiment.com/uploads/default/original/1X/35846c5ed45a2241fe48c855e9ac39dfbaa2d188.png) 

## Let it go - intro piano melody
![Let_it_go_1|690x352](https://sky.bloomexperiment.com/uploads/default/original/1X/6668aad19292a1160270cfe0ea77c2c438a6bedd.png)

![let_it_go_2|690x298](https://sky.bloomexperiment.com/uploads/default/original/1X/450327ab3240743ec166d75322b86eaed2a3efa9.png) 

## Flower Dance - intro

![flower_dance_intro|690x346](https://sky.bloomexperiment.com/uploads/default/original/1X/e6f464e420070f7121c1f2ad4562ae58a3f607f1.png) 

[/details]

# How to download

Go to the GitHub page: https://github.com/sky-music/sky-python-music-sheet-maker

Click the green <kbd> Clone or Download </kbd> button and then <kbd> Download ZIP </kbd>.

Unzip the folder and save it to your Desktop. Rename the folder to `sky-python-music-sheet-maker`. 

(You can place it in any location and rename it however you like — just adjust the commands in the next section accordingly.)

if you don't yet have Python on your computer, you can download it from python.org

# How to run the program

1. Open cmd on Windows, or Terminal on Mac.

2. Type this command to go to the Python folder inside your program (if you saved it on your Desktop):

```
cd Desktop/sky-python-music-sheet-maker/python
```

Notes for troubleshooting:

This `cd` (change directory) command is to change your current folder to the Python folder inside `sky-python-music-sheet-maker`. Replace the filepath with where the Python folder is located on your computer if your folder structure turns out to be different.

This folder will have files called `main.py`,  `instrument.py`, `modes.py`, `notes.py` `parser.py`,  `render.py`. You can type `ls -la` to check the contents of the current folder.

3. Type this command to run the program:

  - **Windows:** 

```
python main.py
```

  - **Mac:** 

```
python3 main.py
```

Prompts will appear asking for song name etc. Press <kbd>Enter ↲ </kbd> to submit.

```text
==NEW SONG==
Song title: Mary Had A Little Lamb
============
```

When your song is done, it will tell you where your song is located. Double-click on the HTML file to open it in a web browser. 

(You may want to zoom out in the browser for smaller icons.)

# Cheatsheet

- Use these keys as the Sky keyboard:

<kbd>Q</kbd><kbd>W</kbd><kbd>E</kbd><kbd>R</kbd><kbd>T</kbd>
<kbd>A</kbd><kbd>S</kbd><kbd>D</kbd><kbd>F</kbd><kbd>G</kbd>
<kbd>Z</kbd><kbd>X</kbd><kbd>C</kbd><kbd>V</kbd><kbd>B</kbd>

- Use spaces between icons.

```text
Type line: d f g
```

![single notes example|690x179, 50%](https://sky.bloomexperiment.com/uploads/default/original/1X/54edd3ae95211f506835eed1b66a6a963ba04a8c.png) 

- Type letters next to each other for chords.

```text
Type line: qet 
Type line: adg
```

![chord examples|300x500, 50%](https://sky.bloomexperiment.com/uploads/default/original/1X/f59dea80479ed0496f799150d01a598de6401b95.png) 

- Use `.` for blank icons.

```text
Type line: g f d f g g g .
Type line: f f f . g g g .
```

![Mary Had A Little Lamb example|690x173](https://sky.bloomexperiment.com/uploads/default/original/1X/70fd16c9e78f6727bfeecf7854c80a7110fc6723.png) 

- Use `-` for coloured notes.

```
e-a-d-g-c
```

![colored note example |267x202, 50%](https://sky.bloomexperiment.com/uploads/default/original/1X/1e80b7d6d7be3978bf7ba58a4b7b2439a777a89f.png) 

- Press <kbd>Enter ↲ </kbd> for a new line. Pressing Enter on a blank line will end the program.

# Contribute

Feel very free to let me know if you'd like to post any songs to https://sky-music.github.io and I will post it for you!

Also, I would really like any additional help with the program, such as having an interface rather than using the command line, so let me know if you're interested.
