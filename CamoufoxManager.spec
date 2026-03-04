# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE

# 检测平台
is_windows = sys.platform.startswith('win')
is_macos = sys.platform == 'darwin'

# 基础配置
block_cipher = None

# 数据文件 - 使用 collect_all 来自动收集包数据
from PyInstaller.utils.hooks import collect_all, collect_data_files

# 收集 browserforge 的所有数据
browserforge_datas = collect_all('browserforge')

# 基础数据文件
datas = [('manager', 'manager')]

# 添加 browserforge 的数据
if browserforge_datas:
    datas.extend(browserforge_datas[0])

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
