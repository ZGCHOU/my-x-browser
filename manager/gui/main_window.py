"""GUI 主界面 - 使用 PyQt5 实现"""
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QLineEdit, QTextEdit,
                             QDialog, QFormLayout, QMessageBox, QListWidgetItem, QSplitter,
                             QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from manager.core.account_manager import AccountManager, Account
from manager.core.browser_manager import BrowserManager


class AddAccountDialog(QDialog):
    """添加/编辑账号对话框"""
    def __init__(self, parent=None, account=None, default_proxy=""):
        super().__init__(parent)
        self.account = account
        self.setModal(True)
        self.resize(450, 350)

        if account:
            self.setWindowTitle("编辑账号")
        else:
            self.setWindowTitle("添加新账号")

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: Twitter_Account_1")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("例如: https://x.com/home")

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("例如: http://127.0.0.1:7897 (留空则不使用代理)")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注信息 (可选)")
        self.notes_input.setMaximumHeight(80)

        # 如果是编辑模式，填充现有数据
        if account:
            self.name_input.setText(account.name)
            self.name_input.setEnabled(False)  # 不允许修改账号名
            self.url_input.setText(account.url or "https://www.google.com")
            self.proxy_input.setText(account.proxy or "")
            self.notes_input.setText(account.notes or "")
        else:
            # 新建时使用默认代理
            self.url_input.setText("https://www.google.com")
            if default_proxy:
                self.proxy_input.setText(default_proxy)

        layout.addRow("账号名称*:", self.name_input)
        layout.addRow("启动URL*:", self.url_input)
        layout.addRow("代理地址:", self.proxy_input)

        # 添加代理说明
        proxy_hint = QLabel("💡 支持 http/socks5 代理，例如:\n   http://127.0.0.1:7897\n   socks5://127.0.0.1:1080")
        proxy_hint.setStyleSheet("color: #666; font-size: 11px;")
        layout.addRow("", proxy_hint)

        layout.addRow("备注:", self.notes_input)

        # 按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addRow(btn_layout)
        self.setLayout(layout)

    def get_data(self):
        """获取输入数据"""
        return {
            'name': self.name_input.text().strip(),
            'url': self.url_input.text().strip() or "https://www.google.com",
            'proxy': self.proxy_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip()
        }


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camoufox 多账号管理平台")
        self.resize(900, 600)

        # 初始化管理器
        self.account_manager = AccountManager()
        self.browser_manager = BrowserManager()

        # 默认代理设置
        self.default_proxy = ""

        # 创建UI
        self.init_ui()

        # 加载账号列表
        self.refresh_account_list()

        # 定时器：更新浏览器状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_browser_status)
        self.timer.start(1000)  # 每秒更新一次

    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # 顶部：全局设置栏
        top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 5, 10, 5)

        proxy_label = QLabel("默认代理:")
        self.global_proxy_input = QLineEdit()
        self.global_proxy_input.setPlaceholderText("例如: http://127.0.0.1:7897 (新建账号时自动填充)")
        self.global_proxy_input.setMinimumWidth(300)
        self.global_proxy_input.textChanged.connect(self.on_global_proxy_changed)

        top_layout.addWidget(proxy_label)
        top_layout.addWidget(self.global_proxy_input)
        top_layout.addStretch()

        top_bar.setLayout(top_layout)
        top_bar.setStyleSheet("background-color: #f8f9fa; border-bottom: 1px solid #dee2e6;")

        # 中间：主内容区
        content_layout = QHBoxLayout()

        # 左侧：账号列表
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # 标题和按钮
        title_layout = QHBoxLayout()
        title_label = QLabel("账号列表")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.add_btn = QPushButton("+ 添加账号")
        self.add_btn.clicked.connect(self.add_account)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.add_btn)

        # 账号列表
        self.account_list = QListWidget()
        self.account_list.itemClicked.connect(self.on_account_selected)

        left_layout.addLayout(title_layout)
        left_layout.addWidget(self.account_list)

        left_panel.setLayout(left_layout)

        # 右侧：账号详情和操作
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # 账号信息
        info_label = QLabel("账号信息")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("🚀 启动浏览器")
        self.start_btn.clicked.connect(self.start_browser)
        self.start_btn.setEnabled(False)

        self.stop_btn = QPushButton("🛑 停止浏览器")
        self.stop_btn.clicked.connect(self.stop_browser)
        self.stop_btn.setEnabled(False)

        self.edit_btn = QPushButton("✏️ 编辑账号")
        self.edit_btn.clicked.connect(self.edit_account)
        self.edit_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑️ 删除账号")
        self.delete_btn.clicked.connect(self.delete_account)
        self.delete_btn.setEnabled(False)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)

        # 启动URL输入
        url_layout = QHBoxLayout()
        url_label = QLabel("启动URL:")
        self.url_input = QLineEdit()
        self.url_input.setText("https://www.google.com")
        self.url_input.setPlaceholderText("浏览器启动后访问的网址")

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        # 临时禁用代理选项
        self.disable_proxy_checkbox = QCheckBox("临时禁用代理（直连模式）")
        self.disable_proxy_checkbox.setToolTip("勾选后本次启动将忽略账号的代理设置")

        # 状态显示
        self.status_label = QLabel("状态: 未选择账号")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")

        right_layout.addWidget(info_label)
        right_layout.addWidget(self.info_text)
        right_layout.addLayout(url_layout)
        right_layout.addWidget(self.disable_proxy_checkbox)
        right_layout.addLayout(btn_layout)
        right_layout.addWidget(self.status_label)
        right_layout.addStretch()

        right_panel.setLayout(right_layout)

        # 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        content_layout.addWidget(splitter)

        # 组装主布局
        main_layout.addWidget(top_bar)
        main_layout.addLayout(content_layout)
        central_widget.setLayout(main_layout)

    def on_global_proxy_changed(self, text):
        """全局代理输入框变化时"""
        self.default_proxy = text.strip()

    def refresh_account_list(self):
        """刷新账号列表"""
        self.account_list.clear()
        accounts = self.account_manager.get_all_accounts()

        for account in accounts:
            item = QListWidgetItem(f"📁 {account.name}")
            item.setData(Qt.UserRole, account.id)
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
            # 显示账号信息
            info = f"账号名称: {account.name}\n"
            info += f"ID: {account.id}\n"
            info += f"启动URL: {account.url}\n"
            info += f"配置目录: {account.profile_dir}\n"
            info += f"代理: {account.proxy or '无'}\n"
            info += f"备注: {account.notes or '无'}\n"
            info += f"创建时间: {account.created_at}\n"
            info += f"最后使用: {account.last_used or '从未使用'}"

            self.info_text.setText(info)

            # 自动填充URL输入框
            self.url_input.setText(account.url)

            # 更新按钮状态
            is_running = self.browser_manager.is_running(account_id)
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
            print(f"⚠️ 临时禁用代理，使用直连模式")

        try:
            self.browser_manager.start_browser(
                account_id=account.id,
                account_name=account.name,
                profile_dir=account.profile_dir,
                proxy=proxy,
                url=url
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
            self.status_label.setText(f"状态: 🟢 浏览器运行中 - {account.name}")
            self.status_label.setStyleSheet("padding: 10px; background-color: #d4edda; border-radius: 5px; color: #155724;")
        else:
            self.status_label.setText(f"状态: ⚪ 浏览器未运行 - {account.name}")
            self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")

    def clear_info_panel(self):
        """清空信息面板"""
        self.info_text.clear()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.status_label.setText("状态: 未选择账号")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")

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
