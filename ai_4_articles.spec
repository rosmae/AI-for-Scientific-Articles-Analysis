# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('src\init_db.sql', '.'),
    ('README.md', '.'),
]

a = Analysis(
    ['src\main.py'],
    pathex=['src'],
    binaries=[],
    datas=added_files,
    hiddenimports=['Bio.Entrez', 'psycopg2', 'psycopg2.extras'],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ai_4_articles',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico'
)