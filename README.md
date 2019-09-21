# sky-python-music-sheet-maker

See here for how to download and use.

**Instructions:** https://sky.bloomexperiment.com/t/sky-python-music-sheet-maker/102#how-to-download

![Flower Dance intro music sheet](https://raw.githubusercontent.com/sky-music/sky-python-music-sheet-maker/master/images/flower_dance_intro.png)

This program lets you make visual music sheets for Sky: Children of the Light. It is written in Python and does not require previous knowledge of the command line to run. 

SVG icons are thanks to [madwurmz](http://madwurmz.com).

Website with music sheets made using this program: 

https://sky-music.github.io

<div data-theme-toc="true"> </div>

# Code

https://github.com/sky-music/sky-python-music-sheet-maker

# Templates

[details=Image templates if you prefer (click to expand)]

## Template 1
![music_sheet_template|690x324](upload://4VIpUjk1wB04qNRh28XoA4eBq3P.png) 

## Template 2
![SKY_MUSIC_SHEET_TEMPLATE|689x319](upload://791h4xqAUOQ4L601lpJ3HkXgPfM.png) 

[/details]

Templates are free to download and use without credit.

# Examples

[details=Click to expand]

## Chord Chart in C

![ChordChart|429x500](upload://7Dr1l08uK9UMPQz0LFR4jD8MxFS.png) 

## Let it go - intro piano melody
![Let_it_go_1|690x352](upload://eBWWVWj049BipHYFyOfxEh57bpH.png)

![let_it_go_2|690x298](upload://9QvHHITDHdKiS0CDgcuMAXKDMj7.png) 

## Flower Dance - intro

![flower_dance_intro|690x346](upload://wX7qFxfxBJauwtUsivoLKgFVpAd.png) 

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

[details=Notes for troubleshooting]

This `cd` (change directory) command is to change your current folder to the Python folder inside `sky-python-music-sheet-maker`. Replace the filepath with where the Python folder is located on your computer if your folder structure turns out to be different.

This folder will have files called `main.py`,  `instrument.py`, `modes.py`, `notes.py` `parser.py`,  `render.py`. You can type `ls -la` to check the contents of the current folder.

[/details]

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

![single notes example|690x179, 50%](upload://c7jEfLKSGqtvEFuTqxKbNXz8WGE.png) 

- Type letters next to each other for chords.

```text
Type line: qet 
Type line: adg
```

![chord examples|300x500, 50%](upload://z2Pjs8Io7kjFPci1s7pR0q7tBhr.png) 

- Use `.` for blank icons.

```text
Type line: g f d f g g g .
Type line: f f f . g g g .
```

![Mary Had A Little Lamb example|690x173](upload://g7xItJbK6dCC0PILHK9s4qIfgZl.png) 

- Use `-` for coloured notes.

```
e-a-d-g-c
```

![colored note example |267x202, 50%](upload://4lQ6hQJUKXOJYoopLwURxIaZMVp.png) 

- Press <kbd>Enter ↲ </kbd> for a new line. Pressing Enter on a blank line will end the program.

# Contribute

Feel very free to let me know if you'd like to post any songs to https://sky-music.github.io and I will post it for you!

Also, I would really like any additional help with the program, such as having an interface rather than using the command line, so let me know if you're interested.
