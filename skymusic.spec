# -*- mode: python ; coding: utf-8 -*-
# pyinstaller --distpath="~/Desktop/dist" --workpath="~/Desktop/build" skymusic.spec
# Using conda's python: ~/opt/anaconda3/bin/python -m PyInstaller --distpath="~/Desktop/dist" --workpath="~/Desktop/build" skymusic.spec
# In Windows: %homedrive%%homepath%\WinPython\python-3.7.2.amd64\python.exe -m PyInstaller --distpath="%homedrive%%homepath%\Desktop\dist" --workpath="%homedrive%%homepath%\Desktop\build" skymusic.spec
# In Windows Spyder: # ! pyinstaller --distpath="%homedrive%%homepath%\Desktop\dist" --workpath="%homedrive%%homepath%\Desktop\build" skymusic.spec

block_cipher = None

a = Analysis(['src/skymusic/command_line_player.py'],
             pathex=['src'],
             binaries=[],
             datas= [('src/skymusic/langs/*.yaml', 'skymusic/langs' ),
             		('src/skymusic/resources/fonts/*.otf', 'skymusic/resources/fonts' ),
            		('src/skymusic/resources/png/light/*.png', 'skymusic/resources/png/light' ),
             		('src/skymusic/resources/png/dark/*.png', 'skymusic/resources/png/dark' ),
             		('src/skymusic/resources/css/light/*.css', 'skymusic/resources/css/light' ),
            		('src/skymusic/resources/css/dark/*.css', 'skymusic/resources/css/dark' ),
            		('src/skymusic/resources/svg/light/*.svg', 'skymusic/resources/svg/light' ),
            		('src/skymusic/resources/svg/dark/*.svg', 'skymusic/resources/svg/dark' ),
            		('src/skymusic/resources/png/light/__init__.py', 'skymusic/resources/png/light' ),
             		('src/skymusic/resources/png/dark/__init__.py', 'skymusic/resources/png/dark' ),
             		('src/skymusic/resources/css/light/__init__.py', 'skymusic/resources/css/light' ),
            		('src/skymusic/resources/css/dark/__init__.py', 'skymusic/resources/css/dark' ),
            		('src/skymusic/resources/svg/light/__init__.py', 'skymusic/resources/svg/light' ),
            		('src/skymusic/resources/svg/dark/__init__.py', 'skymusic/resources/svg/dark' ),
             		#('src/skymusic/resources/js/*.js', 'skymusic.resources.js' )
             ],
             hookspath=[],
             hiddenimports=[],
             runtime_hooks=[],
             excludes=['numpy', 'scipy', 'tk', 'tkinter', 'matplotlib', 'multiprocessing', 'numpydoc', 'sphynx', 'gevent', 'jedi', 'IPython', 'setuptools', 'asyncio', 'jinja2', 'chardet', 'OpenSSL'],
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
          name='SkyMusicSheetMaker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )          
