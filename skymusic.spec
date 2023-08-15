# -*- mode: python ; coding: utf-8 -*-
# First navigate to the project root directory using cd, or add the path before 'skymusic.spec' 
# Make sure you have set the proxy settings right (in .condarc for Anaconda)
#
# In MacOS Spyder: pyinstaller --distpath="~/Desktop/dist" --workpath="~/Desktop/build" skymusic.spec
# With MacOS Anaconda's python: ~/opt/anaconda3/bin/python -m PyInstaller --distpath="~/Desktop/dist" --workpath="~/Desktop/build" skymusic.spec
#
# In Windows WinPython: %homedrive%%homepath%\WinPython\python-3.7.2.amd64\python.exe -m PyInstaller --distpath="%homedrive%%homepath%\Desktop\dist" --workpath="%homedrive%%homepath%\Desktop\build" skymusic.spec
# In Windows Anaconda Prompt: python.exe -m PyInstaller --distpath="%homedrive%%homepath%\Desktop\dist" --workpath="%homedrive%%homepath%\Desktop\build" skymusic.spec
# In Windows Spyder: # ! pyinstaller --distpath="%homedrive%%homepath%\Desktop\dist" --workpath="%homedrive%%homepath%\Desktop\build" skymusic.spec

block_cipher = None

a = Analysis(['src/skymusic/command_line_player.py'],
             pathex=['src'],
             binaries=[],
             datas= [('src/skymusic/langs/*.yaml', 'skymusic/langs' ),
             		('src/skymusic/resources/fonts/*.otf', 'skymusic/resources/fonts' ),
            		('src/skymusic/resources/png/light/mobile/*.png', 'skymusic/resources/png/light/mobile' ),
            		('src/skymusic/resources/png/light/playstation/*.png', 'skymusic/resources/png/light/playstation' ),
            		('src/skymusic/resources/png/light/switch/*.png', 'skymusic/resources/png/light/switch' ),
             		('src/skymusic/resources/png/dark/mobile/*.png', 'skymusic/resources/png/dark/mobile' ),
             		('src/skymusic/resources/png/dark/playstation/*.png', 'skymusic/resources/png/dark/playstation' ),
             		('src/skymusic/resources/png/dark/switch/*.png', 'skymusic/resources/png/dark/switch' ),
             		('src/skymusic/resources/css/light/*.css', 'skymusic/resources/css/light' ),
            		('src/skymusic/resources/css/dark/*.css', 'skymusic/resources/css/dark' ),
            		('src/skymusic/resources/svg/light/*.svg', 'skymusic/resources/svg/light' ),
            		('src/skymusic/resources/svg/dark/*.svg', 'skymusic/resources/svg/dark' ),
            		('src/skymusic/resources/png/light/__init__.py', 'skymusic/resources/png/light' ),
             		('src/skymusic/resources/png/dark/__init__.py', 'skymusic/resources/png/dark' ),
            		('src/skymusic/resources/png/light/mobile/__init__.py', 'skymusic/resources/png/light/mobile' ),
            		('src/skymusic/resources/png/light/playstation/__init__.py', 'skymusic/resources/png/light/playstation' ),
            		('src/skymusic/resources/png/light/switch/__init__.py', 'skymusic/resources/png/light/switch' ),
            		('src/skymusic/resources/png/dark/mobile/__init__.py', 'skymusic/resources/png/dark/mobile' ),
            		('src/skymusic/resources/png/dark/playstation/__init__.py', 'skymusic/resources/png/dark/playstation' ),
            		('src/skymusic/resources/png/dark/switch/__init__.py', 'skymusic/resources/png/dark/switch' ),
             		('src/skymusic/resources/css/light/__init__.py', 'skymusic/resources/css/light' ),
            		('src/skymusic/resources/css/dark/__init__.py', 'skymusic/resources/css/dark' ),
            		('src/skymusic/resources/svg/light/__init__.py', 'skymusic/resources/svg/light' ),
            		('src/skymusic/resources/svg/dark/__init__.py', 'skymusic/resources/svg/dark' ),
             		#('src/skymusic/resources/js/*.js', 'skymusic.resources.js' )
             ],
             hookspath=[],
             hiddenimports=['PIL.Image', 'PIL.ImageDraw','PIL.ImageFont'],
             runtime_hooks=[],
             excludes=['numpy', 'IPython', 'matplotlib', 'scipy', 'tk', 'tkinter', 'multiprocessing',
             			'numpydoc', 'sphynx', 'gevent', 'jedi', 'setuptools', 'asyncio',
             			'jinja2', 'chardet', 'OpenSSL'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
"""
# Instructions for one-dir bundling (to dist folder)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SkyMusicSheetMaker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SkyMusicSheetMaker')   
"""   
# Instructions for one-file bundling
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SkyMusicSheetMaker_v302',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )          
