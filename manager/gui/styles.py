"""现代化 UI 样式定义 - 专业多账号管理平台 (柔和灰白系大气版)"""

# 主色调 - 专业蓝紫渐变
PRIMARY_COLOR = "#6366f1"      # Indigo
PRIMARY_HOVER = "#4f46e5"
PRIMARY_LIGHT = "#818cf8"
ACCENT_COLOR = "#8b5cf6"       # Purple
SUCCESS_COLOR = "#10b981"      # Emerald
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"
INFO_COLOR = "#06b6d4"         # Cyan

# 柔和灰白主题 - 降低对比度
LIGHT_BG = "#f5f7fa"           # 主背景 (更柔和的灰白)
LIGHT_BG_SECONDARY = "#eef1f6" # 次级背景
LIGHT_CARD = "#ffffff"         # 卡片背景 (纯白)
LIGHT_CARD_HOVER = "#f5f7fa"   # 卡片悬停
LIGHT_BORDER = "#dce1e8"       # 边框 (更深一点)
LIGHT_BORDER_LIGHT = "#c5cad3" # 深边框
LIGHT_TEXT = "#1a202c"         # 主文本 (稍微浅一点)
LIGHT_TEXT_SECONDARY = "#4a5568" # 次级文本
LIGHT_TEXT_MUTED = "#718096"   # 弱化文本

# 超大字体 - 大气风格
FONT_SMALL = "20px"      # 小字
FONT_NORMAL = "22px"     # 正常
FONT_LARGE = "26px"      # 大
FONT_TITLE = "32px"      # 标题
FONT_HEADER = "38px"     # 大标题

# 兼容旧变量名
DARK_BG = LIGHT_BG


def get_main_stylesheet():
    """主窗口样式表 - 专业白色系主题 (超大气版)"""
    return f"""
    QMainWindow {{
        background-color: {LIGHT_BG};
        font-family: 'Inter', 'SF Pro Display', 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    }}

    QWidget {{
        background-color: {LIGHT_BG};
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
    }}

    /* 顶部工具栏 - 白色渐变 */
    QWidget#top_bar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {LIGHT_CARD}, stop:0.5 #fefeff, stop:1 {LIGHT_CARD});
        border-bottom: 1px solid {LIGHT_BORDER};
        padding: 20px 28px;
    }}

    QLabel {{
        background-color: transparent;
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
    }}

    /* 输入框 - 大字号 */
    QLineEdit {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        padding: 14px 18px;
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
        selection-background-color: {PRIMARY_COLOR};
        min-height: 28px;
    }}

    QLineEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
        background-color: {LIGHT_CARD};
        padding: 13px 17px;
    }}

    QLineEdit:hover {{
        border-color: {LIGHT_BORDER_LIGHT};
        background-color: {LIGHT_BG_SECONDARY};
    }}

    QLineEdit::placeholder {{
        color: {LIGHT_TEXT_MUTED};
        font-size: {FONT_NORMAL};
    }}

    /* 文本编辑框 */
    QTextEdit {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        padding: 18px;
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
        line-height: 1.6;
    }}

    QTextEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
        padding: 17px;
    }}

    /* 主按钮 - 默认 */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_COLOR}, stop:1 {ACCENT_COLOR});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 16px 28px;
        font-size: {FONT_NORMAL};
        font-weight: 600;
        min-height: 32px;
    }}

    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_LIGHT}, stop:1 #a78bfa);
    }}

    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_HOVER}, stop:1 #7c3aed);
    }}

    QPushButton:disabled {{
        background: #e2e8f0;
        color: #64748b;
        border: 1px solid #cbd5e1;
    }}

    /* 次要按钮 - 白色边框 */
    QPushButton#secondary_btn {{
        background: {LIGHT_CARD};
        border: 2px solid {LIGHT_BORDER};
        color: {LIGHT_TEXT_SECONDARY};
    }}

    QPushButton#secondary_btn:hover {{
        background: {LIGHT_BG_SECONDARY};
        border-color: {LIGHT_BORDER_LIGHT};
        color: {LIGHT_TEXT};
    }}

    QPushButton#secondary_btn:pressed {{
        background: {LIGHT_BORDER};
    }}

    QPushButton#secondary_btn:disabled {{
        background: #f1f5f9;
        color: #cbd5e1;
        border: 2px solid #e2e8f0;
    }}

    /* 危险按钮 - 深红文字 */
    QPushButton#danger_btn {{
        background: #fee2e2;
        border: 2px solid {DANGER_COLOR};
        color: #991b1b;
    }}

    QPushButton#danger_btn:hover {{
        background: #fecaca;
        border-color: #dc2626;
        color: #7f1d1d;
    }}

    QPushButton#danger_btn:pressed {{
        background: #fca5a5;
    }}

    QPushButton#danger_btn:disabled {{
        background: #fef2f2;
        color: #fca5a5;
        border: 2px solid #fecaca;
    }}

    /* 成功按钮 - 深绿文字 */
    QPushButton#success_btn {{
        background: #dcfce7;
        border: 2px solid {SUCCESS_COLOR};
        color: #166534;
    }}

    QPushButton#success_btn:hover {{
        background: #bbf7d0;
        border-color: #16a34a;
        color: #14532d;
    }}

    QPushButton#success_btn:pressed {{
        background: #86efac;
    }}

    QPushButton#success_btn:disabled {{
        background: #f0fdf4;
        color: #86efac;
        border: 2px solid #bbf7d0;
    }}

    /* 列表样式 - 大条目 */
    QListWidget {{
        background-color: transparent;
        border: none;
        padding: 8px;
        outline: none;
        font-size: {FONT_NORMAL};
    }}

    QListWidget::item {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        padding: 18px 20px;
        margin: 6px 0;
        color: {LIGHT_TEXT_SECONDARY};
        font-size: {FONT_NORMAL};
    }}

    QListWidget::item:hover {{
        background-color: {LIGHT_BG_SECONDARY};
        border-color: {LIGHT_BORDER_LIGHT};
        color: {LIGHT_TEXT};
    }}

    QListWidget::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(99, 102, 241, 0.1), stop:1 rgba(139, 92, 246, 0.1));
        border: 2px solid {PRIMARY_COLOR};
        color: {PRIMARY_COLOR};
        font-weight: 600;
    }}

    /* 复选框 - 大号 */
    QCheckBox {{
        color: {LIGHT_TEXT_SECONDARY};
        font-size: {FONT_NORMAL};
        spacing: 12px;
    }}

    QCheckBox::indicator {{
        width: 24px;
        height: 24px;
        border-radius: 6px;
        border: 2px solid {LIGHT_BORDER_LIGHT};
        background-color: {LIGHT_CARD};
    }}

    QCheckBox::indicator:hover {{
        border-color: {PRIMARY_COLOR};
        background-color: rgba(99, 102, 241, 0.05);
    }}

    QCheckBox::indicator:checked {{
        background-color: {PRIMARY_COLOR};
        border-color: {PRIMARY_COLOR};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
    }}

    /* 分割器 */
    QSplitter::handle {{
        background-color: transparent;
        width: 2px;
    }}

    QSplitter::handle:hover {{
        background-color: {PRIMARY_COLOR};
    }}

    /* 滚动条 */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: rgba(148, 163, 184, 0.4);
        border-radius: 5px;
        min-height: 40px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: rgba(148, 163, 184, 0.6);
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* 对话框 - 强制白色背景 */
    QDialog {{
        background-color: {LIGHT_BG} !important;
        color: {LIGHT_TEXT} !important;
    }}

    QDialog QWidget {{
        background-color: transparent;
        color: {LIGHT_TEXT};
    }}

    QMessageBox {{
        background-color: {LIGHT_BG};
    }}

    QMessageBox QLabel {{
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
    }}

    QMessageBox QPushButton {{
        min-width: 100px;
        padding: 12px 24px;
    }}

    /* Tooltip */
    QToolTip {{
        background-color: {LIGHT_TEXT};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: {FONT_SMALL};
    }}

    /* 菜单 */
    QMenu {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        padding: 8px;
    }}

    QMenu::item {{
        padding: 12px 24px;
        border-radius: 8px;
        color: {LIGHT_TEXT_SECONDARY};
        font-size: {FONT_NORMAL};
    }}

    QMenu::item:selected {{
        background-color: {LIGHT_BG_SECONDARY};
        color: {LIGHT_TEXT};
    }}

    QMenu::separator {{
        height: 1px;
        background-color: {LIGHT_BORDER};
        margin: 8px 16px;
    }}

    /* 分组框 */
    QGroupBox {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 12px;
        margin-top: 16px;
        padding-top: 16px;
        font-weight: 600;
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 20px;
        padding: 0 12px;
        color: {LIGHT_TEXT_SECONDARY};
    }}

    /* Tab 控件 */
    QTabWidget::pane {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
    }}

    QTabBar::tab {{
        background-color: transparent;
        border: none;
        padding: 14px 28px;
        margin-right: 4px;
        color: {LIGHT_TEXT_MUTED};
        font-size: {FONT_NORMAL};
        border-bottom: 2px solid transparent;
    }}

    QTabBar::tab:hover {{
        color: {LIGHT_TEXT_SECONDARY};
        background-color: rgba(0, 0, 0, 0.02);
    }}

    QTabBar::tab:selected {{
        color: {PRIMARY_COLOR};
        border-bottom: 2px solid {PRIMARY_COLOR};
        font-weight: 600;
    }}

    /* 下拉框 */
    QComboBox {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        padding: 12px 18px;
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
        min-width: 140px;
    }}

    QComboBox:hover {{
        border-color: {LIGHT_BORDER_LIGHT};
    }}

    QComboBox:focus {{
        border: 2px solid {PRIMARY_COLOR};
        padding: 11px 17px;
    }}

    QComboBox::drop-down {{
        border: none;
        width: 36px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        selection-background-color: {LIGHT_BG_SECONDARY};
        color: {LIGHT_TEXT};
        padding: 8px;
    }}

    /* 进度条 */
    QProgressBar {{
        background-color: {LIGHT_BORDER};
        border: none;
        border-radius: 6px;
        height: 8px;
        text-align: center;
        color: transparent;
    }}

    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_COLOR}, stop:1 {ACCENT_COLOR});
        border-radius: 6px;
    }}
    """


def get_window_manager_stylesheet():
    """窗口管理器样式 - 白色主题强制版"""
    return f"""
    /* 对话框根元素 - 强制白色 */
    QDialog {{
        background-color: {LIGHT_BG} !important;
        color: {LIGHT_TEXT} !important;
        border: 1px solid {LIGHT_BORDER};
        border-radius: 14px;
    }}
    
    /* 所有子widget透明背景 */
    QDialog > QWidget {{
        background-color: transparent;
        color: {LIGHT_TEXT};
    }}
    
    /* 布局内的widget */
    QDialog QWidget {{
        background-color: transparent;
        color: {LIGHT_TEXT};
        font-size: {FONT_NORMAL};
    }}

    /* 列表样式 */
    QListWidget {{
        background-color: {LIGHT_CARD};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 12px;
        padding: 10px;
        font-size: {FONT_NORMAL};
    }}

    QListWidget::item {{
        background-color: {LIGHT_BG};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
        padding: 18px 24px;
        margin: 8px 0;
        color: {LIGHT_TEXT_SECONDARY};
    }}

    QListWidget::item:hover {{
        background-color: {LIGHT_BG_SECONDARY};
        border-color: {LIGHT_BORDER_LIGHT};
        color: {LIGHT_TEXT};
    }}

    QListWidget::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(99, 102, 241, 0.1), stop:1 rgba(139, 92, 246, 0.1));
        border: 2px solid {PRIMARY_COLOR};
        color: {PRIMARY_COLOR};
    }}

    /* 按钮样式 */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_COLOR}, stop:1 {ACCENT_COLOR});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 28px;
        font-weight: 600;
        font-size: {FONT_NORMAL};
    }}

    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_LIGHT}, stop:1 #a78bfa);
    }}

    QPushButton#close_btn {{
        background: {LIGHT_BG_SECONDARY};
        border: 2px solid {LIGHT_BORDER};
        color: {LIGHT_TEXT_SECONDARY};
    }}

    QPushButton#close_btn:hover {{
        background: {LIGHT_BORDER};
        color: {LIGHT_TEXT};
    }}

    QPushButton#secondary_btn {{
        background: {LIGHT_CARD};
        border: 2px solid {LIGHT_BORDER};
        color: {LIGHT_TEXT_SECONDARY};
    }}

    QPushButton#secondary_btn:hover {{
        background: {LIGHT_BG_SECONDARY};
        color: {LIGHT_TEXT};
    }}

    QLabel {{
        background-color: transparent;
        color: {LIGHT_TEXT};
    }}

    QLabel#header_label {{
        font-size: {FONT_TITLE};
        font-weight: bold;
        color: {PRIMARY_COLOR};
    }}

    QLabel#hint_label {{
        font-size: {FONT_SMALL};
        color: {LIGHT_TEXT_MUTED};
    }}
    """


# 兼容旧代码的变量导出
# 主色调
PRIMARY = {
    "50": "#eef2ff",
    "100": "#e0e7ff",
    "200": "#c7d2fe",
    "300": "#a5b4fc",
    "400": PRIMARY_LIGHT,
    "500": PRIMARY_COLOR,
    "600": PRIMARY_HOVER,
    "700": "#4338ca",
    "800": "#3730a3",
    "900": "#312e81",
}

SUCCESS = {"light": "#6ee7b7", "DEFAULT": SUCCESS_COLOR, "dark": "#047857"}
WARNING = {"light": "#fcd34d", "DEFAULT": WARNING_COLOR, "dark": "#b45309"}
DANGER = {"light": "#fca5a5", "DEFAULT": DANGER_COLOR, "dark": "#b91c1c"}
INFO = {"light": "#67e8f9", "DEFAULT": INFO_COLOR, "dark": "#0e7490"}

# 中性色
NEUTRAL = {
    "950": "#030712",
    "900": LIGHT_TEXT,
    "850": LIGHT_TEXT_SECONDARY,
    "800": LIGHT_TEXT_MUTED,
    "750": LIGHT_BORDER_LIGHT,
    "700": LIGHT_BORDER,
    "600": LIGHT_BG_SECONDARY,
    "500": LIGHT_BG,
    "400": LIGHT_CARD_HOVER,
    "300": LIGHT_CARD,
    "200": "#f8fafc",
    "100": "#ffffff",
    "50": "#ffffff",
}

# 功能色简写
ACCENT = {"purple": ACCENT_COLOR, "emerald": SUCCESS_COLOR}

# 字体
FONT = {
    "xs": FONT_SMALL,
    "sm": FONT_SMALL,
    "base": FONT_NORMAL,
    "lg": FONT_LARGE,
    "xl": FONT_LARGE,
    "2xl": FONT_TITLE,
    "3xl": FONT_TITLE,
    "4xl": FONT_HEADER,
    "5xl": FONT_HEADER,
}

WEIGHT = {"normal": "400", "medium": "500", "semibold": "600", "bold": "700"}

SPACING = {"0": "0", "1": "4px", "2": "8px", "3": "12px", "4": "16px", "5": "20px", "6": "24px"}

RADIUS = {"none": "0", "sm": "4px", "DEFAULT": "6px", "md": "8px", "lg": "10px", "xl": "12px", "2xl": "16px", "full": "9999px"}


def get_status_style(status="default"):
    """获取状态样式"""
    styles = {
        "default": ("rgba(99, 102, 241, 0.1)", PRIMARY_COLOR, "rgba(99, 102, 241, 0.2)"),
        "success": ("rgba(16, 185, 129, 0.1)", SUCCESS_COLOR, "rgba(16, 185, 129, 0.2)"),
        "warning": ("rgba(245, 158, 11, 0.1)", WARNING_COLOR, "rgba(245, 158, 11, 0.2)"),
        "danger": ("rgba(239, 68, 68, 0.1)", DANGER_COLOR, "rgba(239, 68, 68, 0.2)"),
        "running": ("rgba(16, 185, 129, 0.15)", SUCCESS_COLOR, "rgba(16, 185, 129, 0.3)"),
    }
    bg, color, border = styles.get(status, styles["default"])
    return f"""
        background: {bg};
        color: {color};
        border-radius: 24px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: {FONT_SMALL};
        border: 1px solid {border};
    """


def get_card_style(variant="default", hover=False):
    """获取卡片样式"""
    base = f"border-radius: 14px; padding: 24px;"
    if variant == "glass":
        style = f"background-color: {LIGHT_CARD}; border: 1px solid {LIGHT_BORDER};"
    elif variant == "elevated":
        style = f"background-color: {LIGHT_CARD}; border: 1px solid {LIGHT_BORDER};"
    else:
        style = f"background-color: {LIGHT_CARD}; border: 1px solid {LIGHT_BORDER};"
    return base + style


# 空函数兼容
responsive_font_size = lambda x, y=None: x
responsive_spacing = lambda x, y=None: x
get_animation_duration = lambda fast=False, slow=False: 150 if fast else (400 if slow else 250)
gradient = lambda **kwargs: ""
glass_effect = lambda **kwargs: ""
shadow = lambda size="md": ""
