"""GUI 主界面 - 使用 PyQt5 实现"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QLineEdit, QTextEdit,
                             QDialog, QFormLayout, QMessageBox, QListWidgetItem, QSplitter,
                             QCheckBox, QGroupBox, QShortcut, QFrame, QScrollArea, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QFontDatabase

from manager.core.account_manager import AccountManager, Account
from manager.core.browser_manager import BrowserManager
from manager.core.window_manager import WindowManager, WindowInfo
from manager.gui.styles import (get_main_stylesheet, get_window_manager_stylesheet,
                                 LIGHT_BG, LIGHT_BG_SECONDARY, LIGHT_CARD, LIGHT_BORDER,
                                 LIGHT_BORDER_LIGHT, LIGHT_TEXT, LIGHT_TEXT_SECONDARY, LIGHT_TEXT_MUTED,
                                 PRIMARY_COLOR, SUCCESS_COLOR, DANGER_COLOR,
                                 FONT_SMALL, FONT_NORMAL, FONT_LARGE, FONT_TITLE, FONT_HEADER)


class AddAccountDialog(QDialog):
    """添加/编辑账号对话框 - 现代化样式"""
    def __init__(self, parent=None, account=None, default_proxy=""):
        super().__init__(parent)
        self.account = account
        self.setModal(True)
        self.setMinimumSize(800, 700)  # 响应式最小尺寸
        self.resize(850, 750)
        self.setStyleSheet(get_main_stylesheet())

        if account:
            self.setWindowTitle("编辑账号")
        else:
            self.setWindowTitle("添加新账号")

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # 标题区域
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(8)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(f"{'编辑' if account else '新建'}账号")
        title.setStyleSheet("""
            font-size: 38px;
            font-weight: 700;
            color: #6366f1;
            margin-bottom: 4px;
        """)
        title_layout.addWidget(title)

        # 副标题
        subtitle = QLabel("配置独立的浏览器环境和代理设置")
        subtitle.setStyleSheet("color: #1a202c; font-size: 22px; margin-bottom: 16px;")
        title_layout.addWidget(subtitle)

        main_layout.addWidget(title_container)

        # 表单区域 - 柔和卡片
        form_widget = QWidget()
        form_widget.setStyleSheet("""
            background-color: #fafbfc;
            border: 1px solid #dce1e8;
            border-radius: 12px;
            padding: 12px;
        """)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(28, 28, 28, 28)

        # 账号名称
        name_label = QLabel("账号名称 *")
        name_label.setStyleSheet("color: #1a202c; font-weight: 600; font-size: 20px; margin-bottom: 8px;")
        form_layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: Twitter_Account_1")
        form_layout.addWidget(self.name_input)

        # 启动URL
        url_label = QLabel("启动 URL *")
        url_label.setStyleSheet("color: #1a202c; font-weight: 600; font-size: 20px; margin-bottom: 8px; margin-top: 12px;")
        form_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("例如: https://x.com/home")
        form_layout.addWidget(self.url_input)

        # 代理地址
        proxy_label = QLabel("代理地址")
        proxy_label.setStyleSheet("color: #1a202c; font-weight: 600; font-size: 20px; margin-bottom: 8px; margin-top: 12px;")
        form_layout.addWidget(proxy_label)

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:7897 (留空则直连)")
        form_layout.addWidget(self.proxy_input)

        # 代理提示
        proxy_hint = QLabel("支持 HTTP / SOCKS5 代理格式")
        proxy_hint.setStyleSheet("color: #718096; padding: 8px 0; font-size: 18px;")
        form_layout.addWidget(proxy_hint)

        # 备注
        notes_label = QLabel("备注")
        notes_label.setStyleSheet("color: #1a202c; font-weight: 600; font-size: 20px; margin-bottom: 8px; margin-top: 12px;")
        form_layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("可选的备注信息...")
        self.notes_input.setMaximumHeight(100)
        form_layout.addWidget(self.notes_input)

        main_layout.addWidget(form_widget)

        # 如果是编辑模式，填充现有数据
        if account:
            self.name_input.setText(account.name)
            self.name_input.setEnabled(False)
            self.name_input.setStyleSheet("background-color: #334155; color: #64748b;")
            self.url_input.setText(account.url or "https://www.google.com")
            self.proxy_input.setText(account.proxy or "")
            self.notes_input.setText(account.notes or "")
        else:
            self.url_input.setText("https://www.google.com")
            if default_proxy:
                self.proxy_input.setText(default_proxy)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("secondary_btn")
        self.cancel_btn.clicked.connect(self.reject)

        self.ok_btn = QPushButton("保存")
        self.ok_btn.setObjectName("success_btn")
        self.ok_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def get_data(self):
        """获取输入数据"""
        return {
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip() or "https://www.google.com",
            'proxy': self.proxy_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip()
        }


class WindowManagerDialog(QDialog):
    """窗口管理器对话框 - 现代化样式"""
    def __init__(self, parent=None, browser_manager=None, window_manager=None):
        super().__init__(parent)
        self.browser_manager = browser_manager
        self.window_manager = window_manager
        self.setWindowTitle("窗口管理器")
        self.resize(760, 620)
        self.setModal(False)
        
        # 强制设置对话框背景为白色
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # 创建中央白色背景widget
        self.central_widget = QWidget(self)
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {LIGHT_BG};
                color: {LIGHT_TEXT};
            }}
        """)
        
        # 应用样式表
        self.setStyleSheet(get_window_manager_stylesheet())

        self.init_ui()
        self.refresh_window_list()

        # 定时刷新
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_window_list)
        self.timer.start(2000)
        
        # 设置布局到中央widget
        self.central_widget.setLayout(self.main_layout)
        
        # 创建对话框主布局
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(self.central_widget)
        self.setLayout(dialog_layout)

    def init_ui(self):
        """初始化UI"""
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(28, 28, 28, 28)

        # 标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_text = QLabel("窗口管理器")
        title_text.setStyleSheet("font-size: 34px; font-weight: 700; color: #6366f1;")

        header_layout.addWidget(title_text)
        header_layout.addStretch()

        self.main_layout.addWidget(header)

        # 窗口列表卡片 - 白色背景
        list_card = QWidget()
        list_card.setStyleSheet(f"""
            QWidget {{
                background-color: {LIGHT_CARD};
                border-radius: 16px;
                border: 1px solid {LIGHT_BORDER};
            }}
        """)
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(24, 24, 24, 24)

        list_title = QLabel("运行中的浏览器窗口")
        list_title.setStyleSheet(f"color: {LIGHT_TEXT}; font-weight: 600; font-size: 22px; margin-bottom: 8px;")
        list_layout.addWidget(list_title)

        self.window_list = QListWidget()
        self.window_list.setMinimumHeight(240)
        self.window_list.itemClicked.connect(self.on_window_selected)
        list_layout.addWidget(self.window_list)

        self.main_layout.addWidget(list_card)

        # 快速操作按钮组 - 白色背景
        ops_card = QWidget()
        ops_card.setStyleSheet(f"""
            QWidget {{
                background-color: {LIGHT_CARD};
                border-radius: 16px;
                border: 1px solid {LIGHT_BORDER};
            }}
        """)
        ops_layout = QHBoxLayout(ops_card)
        ops_layout.setSpacing(16)
        ops_layout.setContentsMargins(24, 24, 24, 24)

        self.focus_btn = QPushButton("聚焦窗口")
        self.focus_btn.clicked.connect(self.focus_selected_window)
        self.focus_btn.setEnabled(False)

        self.minimize_btn = QPushButton("最小化全部")
        self.minimize_btn.setObjectName("secondary_btn")
        self.minimize_btn.clicked.connect(self.minimize_all)

        ops_layout.addWidget(self.focus_btn)
        ops_layout.addWidget(self.minimize_btn)
        self.main_layout.addWidget(ops_card)

        # 提示信息
        hint = QLabel("点击窗口列表选择目标 · 快捷键 Ctrl+1~9 快速切换")
        hint.setStyleSheet(f"color: {LIGHT_TEXT_MUTED}; font-size: 19px;")
        hint.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(hint)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(close_btn)
    
    def refresh_window_list(self):
        """刷新窗口列表"""
        current_item = self.window_list.currentItem()
        current_data = current_item.data(Qt.UserRole) if current_item else None
        
        self.window_list.clear()
        
        # 从 browser_manager 获取运行中的账号（优先使用已保存的 window_id）
        running_accounts = {}
        if self.browser_manager:
            for account_id, ctx in self.browser_manager.contexts.items():
                if ctx.is_running:
                    running_accounts[ctx.account_name] = {
                        'account_id': account_id,
                        'account_name': ctx.account_name,
                        'window_id': ctx.window_id  # 使用已保存的窗口 ID
                    }
        
        # 尝试从系统获取窗口信息
        detected_windows = []
        if self.window_manager:
            detected_windows = self.window_manager.list_windows()
            print(f"检测到 {len(detected_windows)} 个浏览器窗口")
            for w in detected_windows:
                print(f"  - {w.window_id}: {w.title[:50]}")
        
        # 合并数据：优先使用系统检测到的窗口信息
        merged = {}
        
        # 先添加系统检测到的窗口
        for window in detected_windows:
            if window.account_name:
                merged[window.account_name] = {
                    'account_id': None,
                    'account_name': window.account_name,
                    'window_id': window.window_id,
                    'title': window.title,
                    'status': 'detected'
                }
        
        # 再添加 browser_manager 中的运行账号（优先保留系统检测到的 window_id）
        for name, data in running_accounts.items():
            if name in merged:
                merged[name]['account_id'] = data['account_id']
                merged[name]['status'] = 'running+detected'
                # 如果 browser_manager 有 window_id 但系统检测没有，使用 browser_manager 的
                if data['window_id'] and not merged[name].get('window_id'):
                    merged[name]['window_id'] = data['window_id']
            else:
                merged[name] = {
                    'account_id': data['account_id'],
                    'account_name': name,
                    'window_id': data['window_id'],  # 使用从 browser_manager 获取的 window_id
                    'title': None,
                    'status': 'running'
                }
        
        # 显示到列表
        for name, data in sorted(merged.items()):
            if data['status'] == 'running+detected':
                text = f"[{name}] - {data['title'][:30] if data['title'] else '运行中'}"
            elif data['status'] == 'detected':
                text = f"[{name}] - {data['title'][:30] if data['title'] else '已检测'}"
            else:
                text = f"[{name}] - 运行中(未检测到窗口)"

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, data)
            self.window_list.addItem(item)
        
        # 恢复选中状态
        if current_data:
            for i in range(self.window_list.count()):
                item = self.window_list.item(i)
                data = item.data(Qt.UserRole)
                if data and data.get('account_name') == current_data.get('account_name'):
                    self.window_list.setCurrentItem(item)
                    break
    
    def on_window_selected(self, item):
        """选中窗口时"""
        self.focus_btn.setEnabled(True)
    
    def focus_selected_window(self):
        """聚焦到选中的窗口"""
        item = self.window_list.currentItem()
        if not item:
            QMessageBox.information(self, "提示", "请先选择一个窗口")
            return
        
        data = item.data(Qt.UserRole)
        if not data:
            return
        
        account_name = data.get('account_name')
        window_id = data.get('window_id')
        
        print(f"尝试聚焦: account={account_name}, window_id={window_id}")
        
        # 先尝试通过 window_id 聚焦
        if window_id and self.window_manager:
            print(f"使用 window_id 聚焦: {window_id}")
            if self.window_manager.focus_window(window_id):
                print("聚焦成功")
                return
            else:
                print("通过 window_id 聚焦失败")
        
        # 如果失败，尝试通过账号名查找
        if account_name and self.window_manager:
            print(f"尝试通过账号名查找: {account_name}")
            window = self.window_manager.get_window_by_account(account_name)
            if window:
                print(f"找到窗口: {window.window_id}, 尝试聚焦")
                if self.window_manager.focus_window(window.window_id):
                    print("聚焦成功")
                    return
            else:
                print(f"未找到账号 '{account_name}' 的窗口")
        
        QMessageBox.warning(
            self, 
            "聚焦失败",
            "无法聚焦到该窗口。可能原因：\n"
            "1. 窗口已被关闭\n"
            "2. xdotool 没有权限（Wayland 环境不支持）\n"
            "3. 窗口 ID 无法获取"
        )
    
    def minimize_all(self):
        """最小化所有窗口"""
        window_ids = []
        for i in range(self.window_list.count()):
            item = self.window_list.item(i)
            data = item.data(Qt.UserRole)
            if data and data.get('window_id'):
                window_ids.append(data['window_id'])
        
        if window_ids and self.window_manager:
            self.window_manager.minimize_all(window_ids)
    
    def closeEvent(self, event):
        """关闭时停止定时器"""
        self.timer.stop()
        event.accept()


class MainWindow(QMainWindow):
    """主窗口 - 现代化多账号管理平台"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camoufox 多账号管理平台")
        self.setMinimumSize(1400, 850)  # 响应式最小尺寸
        self.resize(1600, 1000)

        # 应用样式表
        self.setStyleSheet(get_main_stylesheet())

        # 初始化管理器
        self.account_manager = AccountManager()
        self.browser_manager = BrowserManager()
        self.window_manager = WindowManager()

        # 默认代理设置
        self.default_proxy = ""
        
        # 窗口管理器对话框
        self.window_manager_dialog = None

        # 创建UI
        self.init_ui()

        # 加载账号列表
        self.refresh_account_list()

        # 定时器：更新浏览器状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_browser_status)
        self.timer.start(1000)  # 每秒更新一次
        
        # 设置快捷键
        self.setup_shortcuts()

    def init_ui(self):
        """初始化现代化 UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== 顶部工具栏 - 白色渐变 =====
        top_bar = QWidget()
        top_bar.setObjectName("top_bar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 16, 24, 16)
        top_layout.setSpacing(20)

        # Logo 和标题 - 渐变文字效果
        logo_layout = QHBoxLayout()
        logo_text = QLabel("Camoufox")
        logo_text.setStyleSheet(f"""
            font-size: 42px;
            font-weight: 700;
            color: {PRIMARY_COLOR};
            letter-spacing: 0.5px;
        """)

        subtitle_text = QLabel("多账号管理平台")
        subtitle_text.setStyleSheet(f"""
            font-size: 24px;
            color: {LIGHT_TEXT_MUTED};
            margin-left: 12px;
        """)

        logo_layout.addWidget(logo_text)
        logo_layout.addWidget(subtitle_text)
        logo_layout.addSpacing(40)

        # 全局代理设置区域
        proxy_container = QWidget()
        proxy_layout = QHBoxLayout(proxy_container)
        proxy_layout.setContentsMargins(0, 0, 0, 0)
        proxy_layout.setSpacing(12)

        proxy_label = QLabel("全局代理")
        proxy_label.setStyleSheet(f"color: {LIGHT_TEXT}; font-weight: 600; font-size: 21px;")

        self.global_proxy_input = QLineEdit()
        self.global_proxy_input.setPlaceholderText("http://127.0.0.1:7897")
        self.global_proxy_input.setMinimumWidth(300)
        self.global_proxy_input.setMaximumWidth(450)
        self.global_proxy_input.textChanged.connect(self.on_global_proxy_changed)

        proxy_layout.addWidget(proxy_label)
        proxy_layout.addWidget(self.global_proxy_input)

        top_layout.addLayout(logo_layout)
        top_layout.addWidget(proxy_container)
        top_layout.addStretch()

        # ===== 主内容区 =====
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {LIGHT_BG}; padding: 24px;")
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(24)
        content_layout.setContentsMargins(24, 24, 24, 24)

        # ===== 左侧面板 - 白色卡片 =====
        left_card = QWidget()
        left_card.setObjectName("left_card")
        left_card.setStyleSheet(f"""
            QWidget#left_card {{
                background-color: {LIGHT_CARD};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 12px;
            }}
        """)
        left_layout = QVBoxLayout(left_card)
        left_layout.setSpacing(18)
        left_layout.setContentsMargins(28, 28, 28, 28)

        # 左侧标题栏
        left_header = QHBoxLayout()
        left_title = QLabel("账号列表")
        left_title.setStyleSheet(f"font-size: 30px; font-weight: 700; color: {LIGHT_TEXT};")

        self.add_btn = QPushButton("+ 添加账号")
        self.add_btn.setObjectName("success_btn")
        self.add_btn.clicked.connect(self.add_account)

        left_header.addWidget(left_title)
        left_header.addStretch()
        left_header.addWidget(self.add_btn)
        left_layout.addLayout(left_header)

        # 账号列表
        self.account_list = QListWidget()
        self.account_list.setMinimumWidth(320)
        self.account_list.setMaximumWidth(450)
        self.account_list.itemClicked.connect(self.on_account_selected)
        left_layout.addWidget(self.account_list)

        # ===== 右侧面板 - 白色卡片 =====
        right_card = QWidget()
        right_card.setObjectName("right_card")
        right_card.setStyleSheet(f"""
            QWidget#right_card {{
                background-color: {LIGHT_CARD};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 12px;
            }}
        """)
        right_layout = QVBoxLayout(right_card)
        right_layout.setSpacing(24)
        right_layout.setContentsMargins(32, 32, 32, 32)

        # 右侧标题
        right_title = QLabel("账号详情")
        right_title.setStyleSheet(f"font-size: 30px; font-weight: 700; color: {LIGHT_TEXT};")
        right_layout.addWidget(right_title)

        # 账号信息卡片 - 浅色内嵌
        info_card = QWidget()
        info_card.setStyleSheet(f"""
            QWidget {{
                background-color: {LIGHT_BG_SECONDARY};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 0.5em;
            }}
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(24, 24, 24, 24)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                color: {LIGHT_TEXT};
                line-height: 1.8;
                font-size: 20px;
            }}
        """)
        self.info_text.setMinimumHeight(350)
        self.info_text.setMaximumHeight(500)
        info_layout.addWidget(self.info_text)
        right_layout.addWidget(info_card)

        # 启动 URL 设置
        url_group = QWidget()
        url_layout = QHBoxLayout(url_group)
        url_layout.setSpacing(12)
        url_label = QLabel("启动 URL")
        url_label.setStyleSheet(f"color: {LIGHT_TEXT}; font-weight: 600; font-size: 20px; background-color: transparent;")
        url_label.setFixedWidth(110)
        self.url_input = QLineEdit()
        self.url_input.setText("https://www.google.com")
        self.url_input.setPlaceholderText("浏览器启动后访问的网址")

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        right_layout.addWidget(url_group)

        # 代理选项
        proxy_option = QWidget()
        proxy_option_layout = QHBoxLayout(proxy_option)
        self.disable_proxy_checkbox = QCheckBox("临时禁用代理（直连模式）")
        self.disable_proxy_checkbox.setStyleSheet(f"color: {LIGHT_TEXT}; font-size: 20px;")
        proxy_option_layout.addWidget(self.disable_proxy_checkbox)
        proxy_option_layout.addStretch()
        right_layout.addWidget(proxy_option)

        # 窗口大小设置
        window_size_group = QWidget()
        window_size_layout = QHBoxLayout(window_size_group)
        window_size_layout.setSpacing(12)
        window_size_label = QLabel("窗口大小")
        window_size_label.setStyleSheet(f"color: {LIGHT_TEXT}; font-weight: 600; font-size: 20px; background-color: transparent;")
        window_size_label.setFixedWidth(110)
        
        self.window_size_combo = QComboBox()
        self.window_size_combo.addItem("默认", None)
        self.window_size_combo.addItem("1920 x 1080 (全高清)", {"width": 1920, "height": 1080})
        self.window_size_combo.addItem("1600 x 900", {"width": 1600, "height": 900})
        self.window_size_combo.addItem("1440 x 900", {"width": 1440, "height": 900})
        self.window_size_combo.addItem("1366 x 768", {"width": 1366, "height": 768})
        self.window_size_combo.addItem("1280 x 720 (720p)", {"width": 1280, "height": 720})
        self.window_size_combo.addItem("1024 x 768", {"width": 1024, "height": 768})
        self.window_size_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {LIGHT_CARD};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 12px 18px;
                color: {LIGHT_TEXT};
                font-size: {FONT_NORMAL};
                min-width: 200px;
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
                font-size: {FONT_NORMAL};
            }}
        """)
        
        window_size_layout.addWidget(window_size_label)
        window_size_layout.addWidget(self.window_size_combo)
        window_size_layout.addStretch()
        right_layout.addWidget(window_size_group)

        # 操作按钮区 - 现代布局
        btn_card = QWidget()
        btn_card.setStyleSheet(f"""
            QWidget {{
                background-color: {LIGHT_BG_SECONDARY};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 10px;
            }}
        """)
        btn_layout = QHBoxLayout(btn_card)
        btn_layout.setSpacing(14)
        btn_layout.setContentsMargins(20, 20, 20, 20)

        # 操作按钮 - 带明确样式
        self.start_btn = QPushButton("启动")
        self.start_btn.setObjectName("success_btn")
        self.start_btn.setMinimumWidth(120)
        self.start_btn.clicked.connect(self.start_browser)
        self.start_btn.setEnabled(False)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("danger_btn")
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.clicked.connect(self.stop_browser)
        self.stop_btn.setEnabled(False)

        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setObjectName("secondary_btn")
        self.edit_btn.setMinimumWidth(100)
        self.edit_btn.clicked.connect(self.edit_account)
        self.edit_btn.setEnabled(False)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setObjectName("danger_btn")
        self.delete_btn.setMinimumWidth(100)
        self.delete_btn.clicked.connect(self.delete_account)
        self.delete_btn.setEnabled(False)

        self.window_mgr_btn = QPushButton("窗口管理")
        self.window_mgr_btn.setObjectName("secondary_btn")
        self.window_mgr_btn.setMinimumWidth(140)
        self.window_mgr_btn.clicked.connect(self.open_window_manager)
        self.window_mgr_btn.setToolTip("管理所有运行中的浏览器窗口 (Ctrl+W)")

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.window_mgr_btn)
        right_layout.addWidget(btn_card)

        # 状态栏 - 现代指示器
        self.status_label = QLabel("未选择账号")
        self.status_label.setObjectName("status_stopped")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background: rgba(148, 163, 184, 0.1);
                color: #94a3b8;
                border-radius: 8px;
                padding: 0.7em 1.2em;
                font-weight: 600;
                font-size: 0.95em;
                border: 1px solid rgba(148, 163, 184, 0.2);
            }
        """)
        right_layout.addWidget(self.status_label)
        right_layout.addStretch()

        # 分割器 - 现代细线
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_card)
        splitter.addWidget(right_card)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
                margin: 0 8px;
            }
            QSplitter::handle:hover {
                background-color: #6366f1;
            }
        """)

        content_layout.addWidget(splitter)

        # 组装主布局
        main_layout.addWidget(top_bar)
        main_layout.addWidget(content_widget)
        central_widget.setLayout(main_layout)

    def on_global_proxy_changed(self, text):
        """全局代理输入框变化时"""
        self.default_proxy = text.strip()

    def refresh_account_list(self):
        """刷新账号列表"""
        self.account_list.clear()
        accounts = self.account_manager.get_all_accounts()

        for account in accounts:
            is_running = self.browser_manager.is_running(account.id)
            # 使用更现代的状态指示器
            if is_running:
                status_icon = "●"
                status_text = "运行中"
            else:
                status_icon = "○"
                status_text = "离线"

            item = QListWidgetItem(f"{status_icon} {account.name}")
            item.setData(Qt.UserRole, account.id)

            # 添加工具提示
            item.setToolTip(f"{account.name}\n状态: {status_text}\nID: {account.id}")

            self.account_list.addItem(item)

    def add_account(self):
        """添加账号"""
        dialog = AddAccountDialog(self, default_proxy=self.default_proxy)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            if not data['name']:
                QMessageBox.warning(self, "错误", "账号名称不能为空！")
                return

            try:
                self.account_manager.add_account(
                    name=data['name'],
                    url=data['url'],
                    proxy=data['proxy'],
                    notes=data['notes']
                )
                self.refresh_account_list()
                QMessageBox.information(self, "成功", f"账号 '{data['name']}' 已添加！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"添加账号失败: {e}")

    def edit_account(self):
        """编辑账号"""
        current_item = self.account_list.currentItem()
        if not current_item:
            return

        account_id = current_item.data(Qt.UserRole)
        account = self.account_manager.get_account(account_id)

        dialog = AddAccountDialog(self, account=account)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()

            try:
                self.account_manager.update_account(
                    account_id=account_id,
                    url=data['url'],
                    proxy=data['proxy'],
                    notes=data['notes']
                )
                self.refresh_account_list()
                self.on_account_selected(current_item)  # 刷新显示
                QMessageBox.information(self, "成功", f"账号 '{account.name}' 已更新！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新账号失败: {e}")

    def delete_account(self):
        """删除账号"""
        current_item = self.account_list.currentItem()
        if not current_item:
            return

        account_id = current_item.data(Qt.UserRole)
        account = self.account_manager.get_account(account_id)

        # 检查浏览器是否在运行
        if self.browser_manager.is_running(account_id):
            QMessageBox.warning(self, "警告", "请先停止浏览器再删除账号！")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除账号 '{account.name}' 吗？\n\n注意：配置文件不会被删除。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.account_manager.remove_account(account_id)
            self.refresh_account_list()
            self.clear_info_panel()

    def on_account_selected(self, item):
        """选中账号时"""
        account_id = item.data(Qt.UserRole)
        account = self.account_manager.get_account(account_id)

        if account:
            is_running = self.browser_manager.is_running(account_id)
            status_color = "#10b981" if is_running else "#64748b"
            status_text = "运行中" if is_running else "未运行"
            status_icon = "●" if is_running else "○"

            info_html = f"""
            <div style="line-height: 2.2; color: #1a202c;">
                <table style="width: 100%; border-spacing: 0 10px;">
                    <tr>
                        <td style="color: #718096; width: 120px; padding: 8px 0; font-size: 19px;">名称</td>
                        <td style="font-weight: 700; color: #1a202c; font-size: 23px;">{account.name}</td>
                    </tr>
                    <tr>
                        <td style="color: #718096; padding: 8px 0; font-size: 19px;">状态</td>
                        <td style="color: {status_color}; font-weight: 600; font-size: 20px;">{status_icon} {status_text}</td>
                    </tr>
                    <tr>
                        <td style="color: #718096; padding: 8px 0; font-size: 19px;">ID</td>
                        <td style="font-family: 'Consolas', monospace; color: #718096; font-size: 17px;">{account.id}</td>
                    </tr>
                    <tr>
                        <td style="color: #718096; padding: 8px 0; font-size: 19px;">启动URL</td>
                        <td style="font-size: 19px;"><a href="{account.url}" style="color: #6366f1; text-decoration: none;">{account.url[:50]}{'...' if len(account.url) > 50 else ''}</a></td>
                    </tr>
                    <tr>
                        <td style="color: #718096; padding: 8px 0; vertical-align: top; font-size: 19px;">配置目录</td>
                        <td style="color: #718096; font-size: 16px; word-break: break-all; font-family: 'Consolas', monospace;">{account.profile_dir}</td>
                    </tr>
                    <tr>
                        <td style="color: #718096; padding: 8px 0; font-size: 19px;">代理</td>
                        <td style="color: {('#10b981' if account.proxy else '#718096')}; font-weight: 500; font-size: 19px;">
                            {('代理: ' + account.proxy) if account.proxy else '直连模式'}
                        </td>
                    </tr>
                    {(account.notes and f"<tr><td style='color: #718096; padding: 8px 0; vertical-align: top; font-size: 19px;'>备注</td><td style='color: #1a202c; font-size: 19px;'>{account.notes}</td></tr>") or ""}
                    <tr>
                        <td style="color: #718096; padding: 8px 0; font-size: 19px;">创建时间</td>
                        <td style="color: #718096; font-size: 19px;">{account.created_at[:16].replace('T', ' ')}</td>
                    </tr>
                    <tr>
                        <td style="color: #718096; padding: 8px 0; font-size: 19px;">最后使用</td>
                        <td style="color: {status_color}; font-weight: 500; font-size: 19px;">{account.last_used[:16].replace('T', ' ') if account.last_used else '从未使用'}</td>
                    </tr>
                </table>
            </div>
            """

            self.info_text.setHtml(info_html)

            # 自动填充URL输入框
            self.url_input.setText(account.url)

            # 更新按钮状态
            self.start_btn.setEnabled(not is_running)
            self.stop_btn.setEnabled(is_running)
            self.edit_btn.setEnabled(not is_running)
            self.delete_btn.setEnabled(not is_running)

            # 更新状态
            self.update_status_label(account_id)

    def start_browser(self):
        """启动浏览器"""
        current_item = self.account_list.currentItem()
        if not current_item:
            return

        account_id = current_item.data(Qt.UserRole)
        account = self.account_manager.get_account(account_id)

        url = self.url_input.text().strip()
        if not url:
            url = "https://www.google.com"

        # 检查是否临时禁用代理
        proxy = account.proxy
        if self.disable_proxy_checkbox.isChecked():
            proxy = None
            print(f"[注意] 临时禁用代理，使用直连模式")

        # 获取窗口大小设置
        window_size = self.window_size_combo.currentData()
        if window_size:
            print(f"[设置] 窗口大小: {window_size['width']}x{window_size['height']}")

        try:
            self.browser_manager.start_browser(
                account_id=account.id,
                account_name=account.name,
                profile_dir=account.profile_dir,
                proxy=proxy,
                url=url,
                window_size=window_size
            )

            # 更新最后使用时间
            self.account_manager.update_last_used(account_id)

            # 更新按钮状态
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.delete_btn.setEnabled(False)

            QMessageBox.information(self, "成功", f"浏览器 '{account.name}' 正在启动...")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动浏览器失败: {e}")

    def stop_browser(self):
        """停止浏览器"""
        current_item = self.account_list.currentItem()
        if not current_item:
            return

        account_id = current_item.data(Qt.UserRole)
        account = self.account_manager.get_account(account_id)

        try:
            self.browser_manager.stop_browser(account_id)

            # 更新按钮状态
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.delete_btn.setEnabled(True)

            QMessageBox.information(self, "成功", f"浏览器 '{account.name}' 已停止")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"停止浏览器失败: {e}")

    def update_browser_status(self):
        """更新浏览器状态"""
        current_item = self.account_list.currentItem()
        if current_item:
            account_id = current_item.data(Qt.UserRole)
            self.update_status_label(account_id)

            # 更新按钮状态
            is_running = self.browser_manager.is_running(account_id)
            self.start_btn.setEnabled(not is_running)
            self.stop_btn.setEnabled(is_running)
            self.edit_btn.setEnabled(not is_running)
            self.delete_btn.setEnabled(not is_running)

    def update_status_label(self, account_id):
        """更新状态标签"""
        account = self.account_manager.get_account(account_id)
        is_running = self.browser_manager.is_running(account_id)

        if is_running:
            self.status_label.setText(f"运行中 · {account.name}")
            self.status_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(16, 185, 129, 0.1), stop:1 rgba(6, 182, 212, 0.1));
                    color: #10b981;
                    border-radius: 8px;
                    padding: 0.7em 1.4em;
                    font-weight: 600;
                    font-size: 0.95em;
                    border: 1px solid rgba(16, 185, 129, 0.25);
                }
            """)
        else:
            self.status_label.setText(f"离线 · {account.name}")
            self.status_label.setStyleSheet("""
                QLabel {
                    background: rgba(148, 163, 184, 0.1);
                    color: #94a3b8;
                    border-radius: 8px;
                    padding: 0.7em 1.4em;
                    font-weight: 600;
                    font-size: 0.95em;
                    border: 1px solid rgba(148, 163, 184, 0.2);
                }
            """)

    def clear_info_panel(self):
        """清空信息面板"""
        self.info_text.clear()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.status_label.setText("状态: 未选择账号")
        self.status_label.setStyleSheet("padding: 14px; background-color: #f0f0f0; border-radius: 10px; font-size: 19px;")

    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+W 打开窗口管理器
        shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut.activated.connect(self.open_window_manager)
        
        # Ctrl+1~9 快速切换到对应账号（如果已启动）
        for i in range(1, 10):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda checked, idx=i-1: self.quick_switch_account(idx))
    
    def open_window_manager(self):
        """打开窗口管理器"""
        import platform
        
        # 检查 xdotool 是否安装 (Linux)
        if platform.system() == "Linux":
            import shutil
            if not shutil.which("xdotool"):
                QMessageBox.warning(
                    self,
                    "缺少依赖",
                    "窗口管理功能需要 xdotool\n\n"
                    "请安装: sudo apt install xdotool"
                )
                return
        elif platform.system() == "Darwin":
            # macOS 提示
            QMessageBox.information(
                self, 
                "macOS 权限提示",
                "窗口管理功能需要辅助功能权限：\n\n"
                "1. 系统偏好设置 → 安全性与隐私 → 辅助功能\n"
                "2. 添加并勾选 '终端' 或 'Python'\n\n"
                "如果没有权限，聚焦/排列窗口功能将无法使用。"
            )
        
        if self.window_manager_dialog is None or not self.window_manager_dialog.isVisible():
            self.window_manager_dialog = WindowManagerDialog(
                self, 
                browser_manager=self.browser_manager,
                window_manager=self.window_manager
            )
            self.window_manager_dialog.show()
        else:
            self.window_manager_dialog.raise_()
            self.window_manager_dialog.activateWindow()
    
    def quick_switch_account(self, index):
        """快速切换到指定索引的账号窗口"""
        accounts = self.account_manager.get_all_accounts()
        if index < len(accounts):
            account = accounts[index]
            # 如果账号在运行，尝试聚焦到其窗口
            if self.browser_manager.is_running(account.id):
                window = self.window_manager.get_window_by_account(account.name)
                if window:
                    self.window_manager.focus_window(window.window_id)
                    print(f"切换到账号: {account.name}")

    def closeEvent(self, event):
        """关闭窗口时"""
        # 停止所有浏览器
        self.browser_manager.stop_all()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
