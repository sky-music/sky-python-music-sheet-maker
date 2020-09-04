# -*- mode: python ; coding: utf-8 -*-
# pyinstaller --distpath="/Users/lagaffe/Desktop/dist" --workpath="/Users/lagaffe/Desktop/build" skymusic.spec

block_cipher = None


a = Analysis(['src/skymusic/command_line_player.py'],
             pathex=['src/skymusic'],
             binaries=[],
             datas= [('src/skymusic/resources/fonts/*.otf', 'skymusic.resources.fonts' ),
             		('src/skymusic/resources/png/light/*.png', 'skymusic.resources.png.light' ),
             		('src/skymusic/resources/png/light/*.png', 'skymusic.resources.png.dark' ),
             		('src/skymusic/resources/css/light/*.css', 'skymusic.resources.css.light' ),
             		('src/skymusic/resources/css/light/*.css', 'skymusic.resources.css.dark' ),
             		#('src/skymusic/resources/js/*.js', 'js' )             
             ],
             hiddenimports=['skymusic.resources.fonts', 'skymusic.resources.png.light', 'skymusic.resources.png.dark', 'skymusic.resources.css.light', 'skymusic.resources.css.dark' ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SkyMusic',
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
               name='SkyMusic')
