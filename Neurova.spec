# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'kivy',
        'kivy.core.window.window_sdl2',
        'kivy.core.text.text_sdl2',
        'kivy.core.image.img_sdl2',
        'kivy.uix.screenmanager',
        'kivymd',
        'requests',
        'numpy',
        'pygame',
        'oscpy',
        'screens',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Neurova',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)