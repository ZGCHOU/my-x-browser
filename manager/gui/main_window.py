"""
主窗口 - 紧凑单列布局，始终置顶
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QApplication
)
from PyQt5.QtCore import Qt, QSize, QTimer

from ..core.account_manager import AccountManager
from ..core.browser_manager import BrowserManager
from ..core.window_manager import WindowManager
from .account_dialog import AccountDialog
from .styles import (
    get_main_stylesheet, PRIMARY_COLOR, SUCCESS_COLOR, DANGER_COLOR, WARNING_COLOR,
    LIGHT_BG, LIGHT_CARD, LIGHT_TEXT, LIGHT_TEXT_SECONDARY, LIGHT_TEXT_MUTED,
    LIGHT_BORDER
)


class MainWindow(QMainWindow):
    """主窗口 - 紧凑单列布局"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camoufox")
        
        # 窗口设置 - 置顶 + 固定大小
        self.setFixedSize(520, 700)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowStaysOnTopHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        
        # 组件
        self.db = AccountManager()
        self.browser_manager = BrowserManager()
        self.window_manager = WindowManager()
        
        # 正在启动/停止的账号集合
        self.starting_accounts = set()
        self.stopping_accounts = set()
        
        self.init_ui()
        self.load_accounts()
        
        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(2000)
    
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet(get_main_stylesheet())
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题栏
        header = QHBoxLayout()
        
        title = QLabel("Camoufox")
        title.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {PRIMARY_COLOR};")
        header.addWidget(title)
        
        header.addStretch()
        
        # 添加按钮
        add_btn = QPushButton("+")
        add_btn.setFixedSize(44, 44)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {SUCCESS_COLOR}; }}
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_account)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # 副标题
        subtitle = QLabel("多账号管理")
        subtitle.setStyleSheet(f"font-size: 18px; color: {LIGHT_TEXT_MUTED};")
        layout.addWidget(subtitle)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background-color: {LIGHT_BORDER};")
        line.setFixedHeight(2)
        layout.addWidget(line)
        
        # 账号列表
        self.account_list = QListWidget()
        self.account_list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
            }}
            QListWidget::item {{
                background-color: {LIGHT_CARD};
                border: 2px solid {LIGHT_BORDER};
                border-radius: 14px;
                padding: 0px;
                margin: 8px 0;
            }}
            QListWidget::item:hover {{
                border-color: {PRIMARY_COLOR};
            }}
            QListWidget::item:selected {{
                background-color: rgba(99, 102, 241, 0.1);
                border: 3px solid {PRIMARY_COLOR};
            }}
        """)
        self.account_list.setSpacing(6)
        layout.addWidget(self.account_list, 1)
        
        # 底部批量操作
        footer = QFrame()
        footer.setStyleSheet(f"background-color: {LIGHT_BG}; border-radius: 12px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 12, 12, 12)
        footer_layout.setSpacing(10)
        
        # 统计
        self.stats_label = QLabel("0个账号")
        self.stats_label.setStyleSheet(f"font-size: 16px; color: {LIGHT_TEXT_MUTED};")
        footer_layout.addWidget(self.stats_label)
        
        footer_layout.addStretch()
        
        # 启动全部
        start_all = QPushButton("全部启动")
        start_all.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #16a34a; }}
        """)
        start_all.setCursor(Qt.PointingHandCursor)
        start_all.clicked.connect(self.start_all_accounts)
        footer_layout.addWidget(start_all)
        
        # 停止全部
        stop_all = QPushButton("全部停止")
        stop_all.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #dc2626; }}
        """)
        stop_all.setCursor(Qt.PointingHandCursor)
        stop_all.clicked.connect(self.stop_all_accounts)
        footer_layout.addWidget(stop_all)
        
        layout.addWidget(footer)
    
    def create_account_item_widget(self, acc):
        """创建账号列表项部件"""
        widget = QFrame()
        widget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        
        is_running = self.browser_manager.is_running(acc.id)
        is_starting = acc.id in self.starting_accounts
        is_stopping = acc.id in self.stopping_accounts
        
        # 状态指示
        if is_starting:
            status_text = "◌"
            status_color = WARNING_COLOR
        elif is_stopping:
            status_text = "◌"
            status_color = DANGER_COLOR
        else:
            status_text = "●"
            status_color = SUCCESS_COLOR if is_running else '#cbd5e1'
        status = QLabel(status_text)
        status.setStyleSheet(f"""
            color: {status_color};
            font-size: 20px;
        """)
        layout.addWidget(status)
        
        # 账号名
        name = QLabel(acc.name)
        name.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {LIGHT_TEXT};
        """)
        name.setMaximumWidth(140)
        name.setWordWrap(False)
        layout.addWidget(name, 1)
        
        # 操作按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        # 启动/停止按钮
        action_btn = QPushButton()
        action_btn.setFixedSize(48, 42)
        if is_starting or is_stopping:
            action_btn.setText("...")
            bg_color = WARNING_COLOR if is_starting else DANGER_COLOR
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 0;
                }}
            """)
            action_btn.setEnabled(False)
        elif is_running:
            action_btn.setText("停")
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DANGER_COLOR};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0;
                }}
                QPushButton:hover {{ background-color: #dc2626; }}
            """)
        else:
            action_btn.setText("启")
            action_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {SUCCESS_COLOR};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 0;
                }}
                QPushButton:hover {{ background-color: #16a34a; }}
            """)
        action_btn.setCursor(Qt.PointingHandCursor)
        if not is_starting:
            action_btn.clicked.connect(lambda checked, aid=acc.id: self.on_action_clicked(aid))
        btn_layout.addWidget(action_btn)
        
        # 编辑按钮
        edit_btn = QPushButton("编")
        edit_btn.setFixedSize(42, 42)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {LIGHT_BG};
                color: {LIGHT_TEXT_SECONDARY};
                border: 2px solid {LIGHT_BORDER};
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BORDER};
                color: {LIGHT_TEXT};
            }}
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda checked, aid=acc.id: self.edit_account(aid))
        btn_layout.addWidget(edit_btn)
        
        # 删除按钮
        del_btn = QPushButton("删")
        del_btn.setFixedSize(42, 42)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {DANGER_COLOR};
                border: 2px solid {DANGER_COLOR};
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {DANGER_COLOR};
                color: white;
            }}
        """)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda checked, aid=acc.id: self.delete_account(aid))
        btn_layout.addWidget(del_btn)
        
        layout.addLayout(btn_layout)
        
        # 点击整个部件聚焦窗口
        widget.mousePressEvent = lambda event, aid=acc.id: self.on_item_clicked(aid)
        
        return widget
    
    def on_item_clicked(self, acc_id):
        """点击账号项 - 聚焦窗口"""
        # 如果正在运行，聚焦窗口
        if self.browser_manager.is_running(acc_id):
            self.focus_account_window(acc_id)
    
    def on_action_clicked(self, acc_id):
        """点击启动/停止按钮"""
        self.toggle_account(acc_id)
    
    def load_accounts(self):
        """加载账号列表"""
        self.account_list.clear()
        accounts = self.db.get_all_accounts()
        
        for acc in accounts:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 80))
            self.account_list.addItem(item)
            
            widget = self.create_account_item_widget(acc)
            self.account_list.setItemWidget(item, widget)
        
        running = sum(1 for a in accounts if self.browser_manager.is_running(a.id))
        self.stats_label.setText(f"{len(accounts)}个账号 | {running}运行中")
    
    def refresh_status(self):
        """刷新状态"""
        self.load_accounts()
    
    def focus_account_window(self, acc_id):
        """聚焦账号对应的浏览器窗口"""
        if not self.browser_manager.is_running(acc_id):
            return
        
        ctx = self.browser_manager.contexts.get(acc_id)
        acc = self.db.get_account(acc_id)
        if not acc:
            return
        
        # 方法1: 使用已知的 window_id
        if ctx and ctx.window_id:
            if self.window_manager.focus_window(ctx.window_id):
                return
        
        # 方法2: 通过账号名查找窗口
        window = self.window_manager.get_window_by_account(acc.name)
        if window:
            if self.window_manager.focus_window(window.window_id):
                if ctx:
                    ctx.window_id = window.window_id
                return
        
        # 方法3: 尝试通过浏览器管理器查找窗口ID
        if ctx:
            window_id = self.browser_manager._find_window_id(acc.name)
            if window_id:
                ctx.window_id = window_id
                self.window_manager.focus_window(window_id)
    
    def toggle_account(self, acc_id):
        """切换账号状态"""
        if self.browser_manager.is_running(acc_id):
            # 停止操作
            self.stopping_accounts.add(acc_id)
            self.load_accounts()
            QApplication.processEvents()
            
            # 使用定时器延迟停止，让UI有时间刷新
            QTimer.singleShot(100, lambda: self._do_stop_browser(acc_id))
        else:
            self.start_browser(acc_id)
    
    def _do_stop_browser(self, acc_id):
        """实际停止浏览器的操作"""
        try:
            self.browser_manager.stop_browser(acc_id)
        finally:
            # 停止完成后移除加载状态
            QTimer.singleShot(500, lambda: self._on_stop_complete(acc_id))
    
    def _on_stop_complete(self, acc_id):
        """停止完成回调"""
        self.stopping_accounts.discard(acc_id)
        self.load_accounts()
    
    def start_browser(self, acc_id):
        """启动浏览器"""
        acc = self.db.get_account(acc_id)
        if not acc:
            return
        
        # 添加到正在启动集合并立即刷新UI
        self.starting_accounts.add(acc_id)
        self.load_accounts()
        
        # 强制刷新UI，确保加载状态立即显示
        QApplication.processEvents()
        
        # 使用定时器延迟启动，让UI有时间刷新
        QTimer.singleShot(100, lambda: self._do_start_browser(acc_id, acc))
    
    def _do_start_browser(self, acc_id, acc):
        """实际启动浏览器的操作"""
        try:
            self.browser_manager.start_browser(
                acc_id, acc.name, acc.profile_dir,
                proxy=acc.proxy,
                url=acc.url or 'https://www.google.com',
                window_size={'width': 1280, 'height': 800}
            )
        except Exception as e:
            QMessageBox.critical(self, "启动失败", str(e))
        finally:
            # 启动完成后移除加载状态
            QTimer.singleShot(1000, lambda: self._on_start_complete(acc_id))
    
    def _on_start_complete(self, acc_id):
        """启动完成回调"""
        self.starting_accounts.discard(acc_id)
        self.load_accounts()
    
    def start_all_accounts(self):
        """启动所有账号"""
        for acc in self.db.get_all_accounts():
            if not self.browser_manager.is_running(acc.id):
                try:
                    self.start_browser(acc.id)
                except:
                    pass
        QTimer.singleShot(1000, self.load_accounts)
    
    def stop_all_accounts(self):
        """停止所有账号"""
        for acc in self.db.get_all_accounts():
            if self.browser_manager.is_running(acc.id):
                self.browser_manager.stop_browser(acc.id)
        QTimer.singleShot(500, self.load_accounts)
    
    def add_account(self):
        """添加账号"""
        dlg = AccountDialog(self.db, parent=self)
        if dlg.exec_():
            self.load_accounts()
    
    def edit_account(self, acc_id):
        """编辑账号"""
        dlg = AccountDialog(self.db, acc_id, parent=self)
        if dlg.exec_():
            self.load_accounts()
    
    def delete_account(self, acc_id):
        """删除账号"""
        acc = self.db.get_account(acc_id)
        if not acc:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f'确定删除账号 "{acc.name}" 吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.browser_manager.is_running(acc_id):
                self.browser_manager.stop_browser(acc_id)
            self.db.remove_account(acc_id)
            self.load_accounts()
    
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出吗？所有运行的浏览器将被关闭。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.browser_manager.cleanup()
            except:
                pass
            event.accept()
        else:
            event.ignore()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
