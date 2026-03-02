"""浏览器进程管理模块 - 负责启动、停止、管理浏览器实例"""
import os
import subprocess
import threading
from typing import Dict, Optional
from camoufox.sync_api import Camoufox


class BrowserContext:
    """浏览器上下文（账号）"""
    def __init__(self, account_id: str, account_name: str, profile_dir: str, proxy: Optional[str] = None):
        self.account_id = account_id
        self.account_name = account_name
        self.profile_dir = profile_dir
        self.proxy = proxy
        self.context = None
        self.page = None
        self.is_running = False


class BrowserManager:
    """浏览器管理器 - 单浏览器多上下文模式"""
    def __init__(self):
        self.browser = None  # 共享的浏览器实例
        self.contexts: Dict[str, BrowserContext] = {}  # 每个账号一个上下文
        self.browser_thread = None
        self.is_browser_running = False
        self.playwright_manager = None

    def _ensure_browser_running(self):
        """确保浏览器实例正在运行"""
        if self.is_browser_running and self.browser:
            return

        def run_browser():
            try:
                print("🚀 启动共享浏览器实例...")
                # 启动单个浏览器实例（不使用 persistent_context）
                with Camoufox(
                    os="windows",
                    exclude_addons=["ublock", "canvasblocker", "fontblocker"]
                ) as browser:
                    self.browser = browser
                    self.is_browser_running = True
                    print("✅ 共享浏览器已启动")

                    # 保持浏览器运行
                    while self.is_browser_running:
                        import time
                        time.sleep(1)

            except Exception as e:
                print(f"❌ 浏览器启动失败: {e}")
                self.is_browser_running = False
            finally:
                self.browser = None
                self.is_browser_running = False

        self.is_browser_running = True
        self.browser_thread = threading.Thread(target=run_browser, daemon=True)
        self.browser_thread.start()

        # 等待浏览器启动
        import time
        max_wait = 10
        waited = 0
        while not self.browser and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        if not self.browser:
            raise Exception("浏览器启动超时")

    def start_browser(self, account_id: str, account_name: str, profile_dir: str,
                     proxy: Optional[str] = None, url: str = "https://www.google.com"):
        """为账号启动新的浏览器上下文（标签页）"""
        if account_id in self.contexts and self.contexts[account_id].is_running:
            print(f"账号 {account_name} 已在运行")
            return False

        try:
            # 确保浏览器实例在运行
            self._ensure_browser_running()

            # 准备代理配置
            proxy_config = None
            if proxy:
                proxy_config = {"server": proxy}
                print(f"🌐 [{account_name}] 使用代理: {proxy}")
            else:
                print(f"🌐 [{account_name}] 直连模式")

            # 为该账号创建独立的上下文
            context = self.browser.new_context(
                storage_state=profile_dir if os.path.exists(profile_dir) else None,
                proxy=proxy_config
            )

            # 创建新标签页
            page = context.new_page()

            # 设置页面标题（显示账号名）
            page.evaluate(f"document.title = '[{account_name}] ' + document.title")

            # 访问指定URL
            page.goto(url, timeout=60000)

            # 保存上下文信息
            ctx = BrowserContext(account_id, account_name, profile_dir, proxy)
            ctx.context = context
            ctx.page = page
            ctx.is_running = True
            self.contexts[account_id] = ctx

            print(f"✅ 账号 [{account_name}] 已在新标签页中启动")
            return True

        except Exception as e:
            print(f"❌ 启动账号 [{account_name}] 失败: {e}")
            return False

    def stop_browser(self, account_id: str):
        """停止指定账号的浏览器上下文"""
        if account_id not in self.contexts:
            return False

        try:
            ctx = self.contexts[account_id]

            # 保存状态到 profile_dir
            if ctx.context:
                # 保存 cookies 和 storage
                storage_state = ctx.context.storage_state()
                os.makedirs(os.path.dirname(ctx.profile_dir), exist_ok=True)
                with open(ctx.profile_dir, 'w') as f:
                    import json
                    json.dump(storage_state, f)

                ctx.context.close()

            ctx.is_running = False
            del self.contexts[account_id]

            print(f"🛑 账号 [{ctx.account_name}] 已停止")

            # 如果没有活跃的上下文，关闭浏览器
            if not self.contexts:
                self._stop_browser_instance()

            return True

        except Exception as e:
            print(f"停止账号失败: {e}")
            return False

    def _stop_browser_instance(self):
        """停止共享的浏览器实例"""
        if self.browser:
            try:
                self.is_browser_running = False
                self.browser.close()
                print("🛑 共享浏览器已关闭")
            except Exception as e:
                print(f"关闭浏览器失败: {e}")

    def is_running(self, account_id: str) -> bool:
        """检查账号是否在运行"""
        return account_id in self.contexts and self.contexts[account_id].is_running

    def stop_all(self):
        """停止所有账号"""
        for account_id in list(self.contexts.keys()):
            self.stop_browser(account_id)
        self._stop_browser_instance()
