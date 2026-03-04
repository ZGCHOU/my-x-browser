# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE

is_windows = sys.platform.startswith('win')
block_cipher = None

from PyInstaller.utils.hooks import collect_all

datas = [('manager', 'manager')]

# 收集所有 camoufox 相关依赖的数据文件
packages_to_collect = [
    'camoufox',
    'browserforge', 
    'apify_fingerprint_datapoints',
    'language_tags',
]

for pkg in packages_to_collect:
    try:
        pkg_datas, _, _ = collect_all(pkg)
        datas.extend(pkg_datas)
        print(f"Collected {len(pkg_datas)} data files from {pkg}")
    except Exception as e:
        print(f"Warning: could not collect {pkg}: {e}")

hiddenimports = [
    'PyQt5.sip',
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'camoufox',
    'camoufox.sync_api',
    'browserforge',
    'browserforge.headers',
    'browserforge.fingerprints',
    'apify_fingerprint_datapoints',
    'language_tags',
]

if is_windows:
    hiddenimports.append('pygetwindow')

a = Analysis(
    ['run_manager.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='CamoufoxManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
