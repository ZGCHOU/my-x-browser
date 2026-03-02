"""账号管理模块 - 负责账号的增删改查"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class Account:
    """账号数据模型"""
    def __init__(self, name: str, profile_dir: str, proxy: Optional[str] = None,
                 notes: str = "", url: str = "https://www.google.com", account_id: Optional[str] = None):
        self.id = account_id or self._generate_id()
        self.name = name
        self.profile_dir = profile_dir
        self.proxy = proxy  # 格式: http://127.0.0.1:7897
        self.notes = notes
        self.url = url  # 启动时访问的URL
        self.created_at = datetime.now().isoformat()
        self.last_used = None

    def _generate_id(self) -> str:
        """生成唯一ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'profile_dir': self.profile_dir,
            'proxy': self.proxy,
            'notes': self.notes,
            'url': self.url,
            'created_at': self.created_at,
            'last_used': self.last_used
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Account':
        """从字典创建账号"""
        account = cls(
            name=data['name'],
            profile_dir=data['profile_dir'],
            proxy=data.get('proxy'),
            notes=data.get('notes', ''),
            url=data.get('url', 'https://www.google.com'),
            account_id=data.get('id')
        )
        account.created_at = data.get('created_at', account.created_at)
        account.last_used = data.get('last_used')
        return account


class AccountManager:
    """账号管理器"""
    def __init__(self, data_file: str = "manager/data/accounts.json"):
        self.data_file = data_file
        self.accounts: List[Account] = []
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

    def load(self):
        """从文件加载账号数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.accounts = [Account.from_dict(acc) for acc in data]
            except Exception as e:
                print(f"加载账号数据失败: {e}")
                self.accounts = []
        else:
            self.accounts = []

    def save(self):
        """保存账号数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                data = [acc.to_dict() for acc in self.accounts]
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存账号数据失败: {e}")

    def add_account(self, name: str, proxy: Optional[str] = None, notes: str = "", url: str = "https://www.google.com") -> Account:
        """添加新账号"""
        # 自动生成 profile 目录
        profile_dir = os.path.abspath(f"./profiles/{name}")
        os.makedirs(profile_dir, exist_ok=True)

        account = Account(name=name, profile_dir=profile_dir, proxy=proxy, notes=notes, url=url)
        self.accounts.append(account)
        self.save()
        return account

    def remove_account(self, account_id: str) -> bool:
        """删除账号"""
        for i, acc in enumerate(self.accounts):
            if acc.id == account_id:
                self.accounts.pop(i)
                self.save()
                return True
        return False

    def update_account(self, account_id: str, **kwargs) -> bool:
        """更新账号信息"""
        for acc in self.accounts:
            if acc.id == account_id:
                if 'name' in kwargs:
                    acc.name = kwargs['name']
                if 'proxy' in kwargs:
                    acc.proxy = kwargs['proxy']
                if 'notes' in kwargs:
                    acc.notes = kwargs['notes']
                if 'url' in kwargs:
                    acc.url = kwargs['url']
                self.save()
                return True
        return False

    def get_account(self, account_id: str) -> Optional[Account]:
        """获取指定账号"""
        for acc in self.accounts:
            if acc.id == account_id:
                return acc
        return None

    def get_all_accounts(self) -> List[Account]:
        """获取所有账号"""
        return self.accounts

    def update_last_used(self, account_id: str):
        """更新最后使用时间"""
        for acc in self.accounts:
            if acc.id == account_id:
                acc.last_used = datetime.now().isoformat()
                self.save()
                break
