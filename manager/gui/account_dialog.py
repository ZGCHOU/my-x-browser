"""
账号对话框 - 添加/编辑账号
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTextEdit, QComboBox, QFormLayout
)
from PyQt5.QtCore import Qt

from ..core.account_manager import AccountManager


class AccountDialog(QDialog):
    """账号添加/编辑对话框"""
    
    def __init__(self, account_manager: AccountManager, account_id=None, parent=None):
        super().__init__(parent)
        self.account_manager = account_manager
        self.account_id = account_id
        self.account = None
        
        self.setWindowTitle("编辑账号" if account_id else "添加账号")
        self.setMinimumWidth(450)
        self.init_ui()
        
        # 如果是编辑模式，加载数据
        if account_id:
            self.load_account()
    
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #1a202c;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #dce1e8;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                min-height: 24px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #6366f1;
            }
            QPushButton {
                background-color: #6366f1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton#cancel_btn {
                background-color: #f1f5f9;
                color: #64748b;
            }
            QPushButton#cancel_btn:hover {
                background-color: #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("编辑账号" if self.account_id else "添加新账号")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1a202c;")
        layout.addWidget(title)
        
        # 表单
        form = QFormLayout()
        form.setSpacing(12)
        
        # 账号名
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: google1")
        form.addRow("账号名称 *", self.name_input)
        
        # 平台选择（从名称推断，不单独存储）
        self.platform_input = QComboBox()
        self.platform_input.addItems(["gmail", "amazon", "twitter", "facebook", "other"])
        self.platform_input.setEditable(True)
        form.addRow("平台标签", self.platform_input)
        
        # 代理
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("例如: http://127.0.0.1:7897 (可选)")
        form.addRow("代理地址", self.proxy_input)
        
        # 启动URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.google.com")
        form.addRow("启动网址", self.url_input)
        
        # 窗口大小
        size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("1280")
        self.width_input.setMaximumWidth(100)
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("x"))
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("800")
        self.height_input.setMaximumWidth(100)
        size_layout.addWidget(self.height_input)
        size_layout.addStretch()
        form.addRow("窗口大小 (宽x高)", size_layout)
        
        # 备注
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注信息...")
        self.notes_input.setMaximumHeight(80)
        form.addRow("备注", self.notes_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_account(self):
        """加载账号数据"""
        self.account = self.account_manager.get_account(self.account_id)
        if not self.account:
            QMessageBox.warning(self, "错误", "账号不存在")
            self.reject()
            return
        
        self.name_input.setText(self.account.name)
        self.name_input.setReadOnly(True)  # 编辑时不能改名称
        
        # 尝试从 name 推断平台
        name_lower = self.account.name.lower()
        if "google" in name_lower or "gmail" in name_lower:
            self.platform_input.setCurrentText("gmail")
        elif "amazon" in name_lower:
            self.platform_input.setCurrentText("amazon")
        elif "twitter" in name_lower or "x" in name_lower:
            self.platform_input.setCurrentText("twitter")
        elif "facebook" in name_lower or "fb" in name_lower:
            self.platform_input.setCurrentText("facebook")
        else:
            self.platform_input.setCurrentText("other")
        
        if self.account.proxy:
            self.proxy_input.setText(self.account.proxy)
        
        if self.account.url:
            self.url_input.setText(self.account.url)
        
        # 加载窗口大小
        self.width_input.setText(str(self.account.window_width))
        self.height_input.setText(str(self.account.window_height))
        
        if self.account.notes:
            self.notes_input.setText(self.account.notes)
    
    def save(self):
        """保存账号"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入账号名称")
            return
        
        proxy = self.proxy_input.text().strip() or None
        url = self.url_input.text().strip() or "https://www.google.com"
        notes = self.notes_input.toPlainText().strip()
        
        # 获取窗口大小
        try:
            window_width = int(self.width_input.text()) if self.width_input.text() else 1280
            window_height = int(self.height_input.text()) if self.height_input.text() else 800
        except ValueError:
            window_width = 1280
            window_height = 800
        
        try:
            if self.account_id:
                # 编辑模式
                self.account_manager.update_account(
                    self.account_id,
                    proxy=proxy,
                    url=url,
                    notes=notes,
                    window_width=window_width,
                    window_height=window_height
                )
            else:
                # 添加模式
                # 检查名称是否已存在
                for acc in self.account_manager.get_all_accounts():
                    if acc.name == name:
                        QMessageBox.warning(self, "提示", f"账号 '{name}' 已存在")
                        return
                
                self.account_manager.add_account(
                    name=name,
                    proxy=proxy,
                    notes=notes,
                    url=url,
                    window_width=window_width,
                    window_height=window_height
                )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
    
    def get_account(self):
        """获取编辑后的账号（如果需要）"""
        if self.account_id:
            return self.account_manager.get_account(self.account_id)
        return None
