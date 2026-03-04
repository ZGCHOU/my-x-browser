# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE

# 检测平台
is_windows = sys.platform.startswith('win')

# 基础配置
block_cipher = None

# 收集数据文件
from PyInstaller.utils.hooks import collect_all

# 收集 browserforge 和 apify_fingerprint_datapoints 的所有数据
datas = [('manager', 'manager')]

# 收集 browserforge
try:
    bf_datas, bf_binaries, bf_hidden = collect_all('browserforge')
    datas.extend(bf_datas)
except:
    pass

# 收集 apify_fingerprint_datapoints（browserforge 的依赖）
try:
    apify_datas, apify_binaries, apify_hidden = collect_all('apify_fingerprint_datapoints')
    datas.extend(apify_datas)
except:
    pass

# 隐藏导入
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
