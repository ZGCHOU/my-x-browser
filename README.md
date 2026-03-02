# Camoufox 多账号管理平台

一个基于 Camoufox 的多账号指纹浏览器管理工具，支持 Windows 和 Linux 平台。

## 功能特点

- 🎯 多账号管理：添加、删除、编辑多个浏览器账号
- 🔒 配置隔离：每个账号独立的配置文件和 Cookie
- 🌐 代理支持：为每个账号配置独立的代理
- 🖥️ 图形界面：简洁易用的 PyQt5 界面
- 🚀 一键启动：快速启动和停止浏览器实例
- 📊 状态监控：实时显示浏览器运行状态

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd camoufox
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动管理平台

```bash
python run_manager.py
```

### 基本操作

1. **添加账号**
   - 点击"+ 添加账号"按钮
   - 填写账号名称（必填）
   - 可选填写代理地址和备注
   - 点击确定

2. **启动浏览器**
   - 在左侧列表选择账号
   - 在"启动URL"输入框填写要访问的网址
   - 点击"🚀 启动浏览器"

3. **停止浏览器**
   - 选择正在运行的账号
   - 点击"🛑 停止浏览器"

4. **删除账号**
   - 选择账号（需先停止浏览器）
   - 点击"🗑️ 删除账号"

## 项目结构

```
camoufox/
├── manager/                 # 管理平台核心代码
│   ├── core/               # 核心模块
│   │   ├── account_manager.py   # 账号管理
│   │   └── browser_manager.py   # 浏览器进程管理
│   ├── gui/                # GUI 界面
│   │   └── main_window.py       # 主窗口
│   └── data/               # 数据存储目录
│       └── accounts.json        # 账号数据（自动生成）
├── profiles/               # 浏览器配置文件目录
├── run_manager.py          # 启动脚本
├── requirements.txt        # 依赖列表
└── README.md              # 说明文档
```

## 配置说明

### 代理格式

```
http://127.0.0.1:7897
socks5://127.0.0.1:1080
```

### 数据存储

- 账号数据：`manager/data/accounts.json`
- 浏览器配置：`profiles/<账号名>/`

## 注意事项

1. 每个账号的浏览器配置完全隔离
2. 删除账号不会删除配置文件目录
3. 关闭管理平台会自动停止所有浏览器
4. 建议为不同用途的账号配置不同的代理

## 依赖

- Python 3.7+
- camoufox
- PyQt5

## 许可证

MIT License
