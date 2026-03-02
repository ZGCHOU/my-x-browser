#!/usr/bin/env python3
"""Camoufox 多账号管理平台 - 启动脚本"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manager.gui.main_window import main

if __name__ == '__main__':
    main()
