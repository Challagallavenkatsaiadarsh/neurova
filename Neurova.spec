# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# SAFE KIVY COLLECTION (NO collect_submodules)
kivy_datas, kivy_binaries, kivy_hidden = collect_all('kivy')
kivymd_datas, kivymd_binaries, kivymd_hidden = collect_all('kivymd')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=kivy_binaries + kivymd_binaries,
    datas=kivy_datas + kivymd_datas,
    hiddenimports=[
        *kivy_hidden,
        *kivymd_hidden,
        'screens',
        'requests',
        'numpy',
        'pygame',
        'oscpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,   # IMPORTANT for Kivy apps
)