# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.building.api import BUNDLE

# 检测平台
is_windows = sys.platform.startswith('win')
is_macos = sys.platform == 'darwin'

# 基础配置
block_cipher = None

# 数据文件
added_files = [
    ('manager', 'manager'),
]

# 尝试找到 browserforge 的数据文件
try:
    import browserforge
    browserforge_path = os.path.dirname(browserforge.__file__)
    # browserforge 的数据文件通常在包的子目录中
    data_dir = os.path.join(browserforge_path, 'fingerprints', 'data')
    if os.path.exists(data_dir):
        added_files.append((data_dir, 'browserforge/fingerprints/data'))
    # 还有 apify_fingerprint_datapoints 数据
    apify_data = os.path.join(browserforge_path, '..', 'apify_fingerprint_datapoints', 'data')
    if os.path.exists(apify_data):
        added_files.append((apify_data, 'apify_fingerprint_datapoints/data'))
except ImportError:
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
]

if is_windows:
    hiddenimports.append('pygetwindow')

a = Analysis(
    ['run_manager.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
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
