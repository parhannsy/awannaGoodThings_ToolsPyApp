# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Mengambil absolute path dari direktori tempat file .spec ini berada
project_root = os.path.abspath(os.getcwd())
src_path = os.path.join(project_root, 'src')
venv_path = os.path.join(project_root, 'venv')

a = Analysis(
    ['main.py'],
    pathex=[project_root, src_path],
    binaries=[],
    datas=[
        # MEMAKSA PyInstaller menyalin seluruh isi folder 'src' ke dalam root executable
        (src_path, 'src'),
        # Menyalin library customtkinter dari environment venv
        (os.path.join(venv_path, 'Lib', 'site-packages', 'customtkinter'), 'customtkinter')
    ],
    hiddenimports=[
        'presentation',
        'presentation.app'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AwannaGoodThingsApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Menonaktifkan console terminal hitam saat aplikasi menyala
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AwannaGoodThingsApp',
)