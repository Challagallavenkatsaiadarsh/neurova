# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

# ========================
# COLLECT ALL MODULES
# ========================
kivy_hidden = collect_submodules('kivy')
kivymd_hidden = collect_submodules('kivymd')
screens_hidden = collect_submodules('screens')

hiddenimports = []
hiddenimports += kivy_hidden
hiddenimports += kivymd_hidden
hiddenimports += screens_hidden

# ========================
# MAIN BUILD
# ========================
a = Analysis(
    ['main.py'],
    pathex=['.'],   # IMPORTANT FIX (was empty)
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
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
    console=False,   # better for GUI apps
)