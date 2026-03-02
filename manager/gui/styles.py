"""现代化 UI 样式定义 - 高分辨率大屏适配"""

# 主色调
PRIMARY_COLOR = "#3b82f6"
PRIMARY_HOVER = "#2563eb"
SUCCESS_COLOR = "#22c55e"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"

# 深色主题
DARK_BG = "#0b0f19"
DARK_CARD = "#151b2b"
DARK_CARD_LIGHT = "#1e2538"
DARK_BORDER = "#2d3748"
DARK_TEXT = "#f8fafc"
DARK_TEXT_SECONDARY = "#94a3b8"

# 超大字体定义 (适配高分辨率屏幕)
FONT_SMALL = "15px"      # 小字
FONT_NORMAL = "18px"     # 正常
FONT_LARGE = "22px"      # 大
FONT_TITLE = "28px"      # 标题
FONT_HEADER = "36px"     # 大标题


def get_main_stylesheet():
    """主窗口样式表 - 超大气主题"""
    return f"""
    QMainWindow {{
        background-color: {DARK_BG};
        font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    }}
    
    QWidget {{
        background-color: {DARK_BG};
        color: {DARK_TEXT};
        font-size: {FONT_NORMAL};
    }}
    
    /* 顶部工具栏 */
    QWidget#top_bar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 #151b2b, stop:1 #1e2538);
        border-bottom: 3px solid {PRIMARY_COLOR};
        border-radius: 0;
        padding: 16px 24px;
    }}
    
    QLabel {{
        color: {DARK_TEXT};
        font-size: {FONT_NORMAL};
    }}
    
    /* 输入框 - 超大尺寸 */
    QLineEdit {{
        background-color: {DARK_CARD};
        border: 2px solid {DARK_BORDER};
        border-radius: 12px;
        padding: 14px 18px;
        color: {DARK_TEXT};
        font-size: {FONT_NORMAL};
        min-height: 28px;
        selection-background-color: {PRIMARY_COLOR};
    }}
    
    QLineEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
        background-color: {DARK_CARD_LIGHT};
    }}
    
    QLineEdit::placeholder {{
        color: #64748b;
        font-size: {FONT_NORMAL};
    }}
    
    /* 文本编辑框 */
    QTextEdit {{
        background-color: {DARK_CARD};
        border: 2px solid {DARK_BORDER};
        border-radius: 12px;
        padding: 16px;
        color: {DARK_TEXT};
        font-size: {FONT_NORMAL};
        line-height: 1.8;
    }}
    
    QTextEdit:focus {{
        border: 2px solid {PRIMARY_COLOR};
    }}
    
    /* 超大按钮 */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {PRIMARY_COLOR}, stop:1 {PRIMARY_HOVER});
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px 32px;
        font-size: {FONT_NORMAL};
        font-weight: 600;
        min-height: 32px;
        min-width: 100px;
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #60a5fa, stop:1 {PRIMARY_COLOR});
    }}
    
    QPushButton:pressed {{
        background: #1d4ed8;
    }}
    
    QPushButton:disabled {{
        background: #334155;
        color: #64748b;
    }}
    
    /* 次要按钮 */
    QPushButton#secondary_btn {{
        background: transparent;
        border: 2px solid {DARK_BORDER};
        color: {DARK_TEXT_SECONDARY};
    }}
    
    QPushButton#secondary_btn:hover {{
        background: {DARK_CARD_LIGHT};
        border-color: #4b5563;
        color: {DARK_TEXT};
    }}
    
    /* 危险按钮 */
    QPushButton#danger_btn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {DANGER_COLOR}, stop:1 #dc2626);
    }}
    
    QPushButton#danger_btn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f87171, stop:1 {DANGER_COLOR});
    }}
    
    /* 成功按钮 */
    QPushButton#success_btn {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {SUCCESS_COLOR}, stop:1 #16a34a);
    }}
    
    QPushButton#success_btn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #4ade80, stop:1 {SUCCESS_COLOR});
    }}
    
    /* 超大列表样式 */
    QListWidget {{
        background-color: {DARK_CARD};
        border: 2px solid {DARK_BORDER};
        border-radius: 16px;
        padding: 12px;
        outline: none;
        font-size: {FONT_NORMAL};
    }}
    
    QListWidget::item {{
        background-color: transparent;
        border-radius: 12px;
        padding: 18px 24px;
        margin: 6px 0;
        color: #cbd5e1;
        font-size: {FONT_NORMAL};
        min-height: 32px;
    }}
    
    QListWidget::item:hover {{
        background-color: {DARK_CARD_LIGHT};
        color: {DARK_TEXT};
    }}
    
    QListWidget::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_COLOR}, stop:1 #3b82f6);
        color: white;
        font-weight: 600;
    }}
    
    /* 复选框 - 加大 */
    QCheckBox {{
        color: #cbd5e1;
        font-size: {FONT_NORMAL};
        spacing: 12px;
    }}
    
    QCheckBox::indicator {{
        width: 26px;
        height: 26px;
        border-radius: 8px;
        border: 2px solid #4b5563;
        background-color: {DARK_CARD};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {PRIMARY_COLOR};
        border-color: {PRIMARY_COLOR};
    }}
    
    /* 分割线 */
    QSplitter::handle {{
        background-color: {DARK_BORDER};
        width: 3px;
    }}
    
    QSplitter::handle:hover {{
        background-color: #4b5563;
    }}
    
    /* 滚动条 - 加宽 */
    QScrollBar:vertical {{
        background-color: {DARK_CARD};
        width: 14px;
        border-radius: 7px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: #4b5563;
        border-radius: 7px;
        min-height: 50px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: #64748b;
    }}
    
    /* 对话框 */
    QDialog {{
        background-color: {DARK_BG};
        color: {DARK_TEXT};
    }}
    
    QMessageBox {{
        background-color: {DARK_BG};
    }}
    
    QMessageBox QLabel {{
        color: {DARK_TEXT};
        font-size: {FONT_NORMAL};
    }}
    
    QMessageBox QPushButton {{
        min-width: 100px;
        padding: 12px 24px;
    }}
    """


def get_window_manager_stylesheet():
    """窗口管理器样式 - 超大"""
    return f"""
    QDialog {{
        background-color: {DARK_BG};
        border: 2px solid {DARK_BORDER};
        border-radius: 20px;
    }}
    
    QWidget {{
        background-color: transparent;
        color: {DARK_TEXT};
        font-size: {FONT_NORMAL};
    }}
    
    QListWidget {{
        background-color: {DARK_CARD};
        border: 2px solid {DARK_BORDER};
        border-radius: 16px;
        padding: 12px;
        font-size: {FONT_NORMAL};
    }}
    
    QListWidget::item {{
        background-color: {DARK_CARD_LIGHT};
        border-radius: 12px;
        padding: 18px 24px;
        margin: 6px 0;
        color: #cbd5e1;
        min-height: 32px;
    }}
    
    QListWidget::item:hover {{
        background-color: #334155;
    }}
    
    QListWidget::item:selected {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_COLOR}, stop:1 #3b82f6);
        color: white;
    }}
    
    QPushButton {{
        background: {PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 18px 32px;
        font-weight: 600;
        font-size: {FONT_NORMAL};
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background: #3b82f6;
    }}
    
    QPushButton#close_btn {{
        background: {DARK_CARD_LIGHT};
        color: #cbd5e1;
    }}
    
    QPushButton#close_btn:hover {{
        background: #334155;
        color: white;
    }}
    
    QPushButton#secondary_btn {{
        background: transparent;
        border: 2px solid #4b5563;
        color: #94a3b8;
    }}
    
    QPushButton#secondary_btn:hover {{
        background: {DARK_CARD_LIGHT};
        color: white;
    }}
    
    QLabel#header_label {{
        font-size: {FONT_TITLE};
        font-weight: bold;
        color: {PRIMARY_COLOR};
    }}
    
    QLabel#hint_label {{
        font-size: {FONT_SMALL};
        color: #64748b;
    }}
    """
