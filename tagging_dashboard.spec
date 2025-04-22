# tagging_dashboard.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


from PyInstaller.utils.hooks import collect_submodules
hidden_imports = collect_submodules('encodings') + collect_submodules("fastapi") + collect_submodules("starlette") + collect_submodules("uvicorn") + [
    'asyncio',
    'app.main',
    'app.api',
    'app.api.v1',
    'app.dependencies',
    'app.services.backgroundTasks.projectDataUpdater',
    'app.services.backgroundTasks.liveDataProcess',
]


a = Analysis(
    ['main_entry.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    # exclude_binaries=True,
    name='tagging_dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # set to False to hide console window on Windows
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tagging_dashboard'
)
