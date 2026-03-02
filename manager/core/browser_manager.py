"""浏览器进程管理模块 - 负责启动、停止、管理浏览器实例"""
import os
import subprocess
import threading
import queue
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
        
        # 命令队列：用于线程间通信
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def _browser_worker(self):
        """浏览器工作线程 - 所有浏览器操作都在此线程执行"""
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

                # 处理命令队列
                while self.is_browser_running:
                    try:
                        # 非阻塞方式检查命令，超时100ms
                        cmd = self.command_queue.get(timeout=0.1)
                        self._handle_command(cmd)
                    except queue.Empty:
                        continue

        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            self.is_browser_running = False
        finally:
            self.browser = None
            self.is_browser_running = False

    def _handle_command(self, cmd):
        """处理命令"""
        action = cmd.get('action')
        
        if action == 'new_context':
            self._do_new_context(cmd)
        elif action == 'close_context':
            self._do_close_context(cmd)
        elif action == 'stop_browser':
            self._do_stop_browser()
        else:
            self.result_queue.put({'success': False, 'error': f'未知命令: {action}'})

    def _do_new_context(self, cmd):
        """在浏览器线程中创建新上下文"""
        try:
            account_id = cmd['account_id']
            account_name = cmd['account_name']
            profile_dir = cmd['profile_dir']
            proxy = cmd['proxy']
            url = cmd['url']

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
            self.result_queue.put({'success': True})

        except Exception as e:
            print(f"❌ 启动账号 [{account_name}] 失败: {e}")
            self.result_queue.put({'success': False, 'error': str(e)})

    def _do_close_context(self, cmd):
        """在浏览器线程中关闭上下文"""
        try:
            account_id = cmd['account_id']
            if account_id not in self.contexts:
                self.result_queue.put({'success': False, 'error': '账号未运行'})
                return

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
            self.result_queue.put({'success': True, 'account_name': ctx.account_name})

        except Exception as e:
            print(f"停止账号失败: {e}")
            self.result_queue.put({'success': False, 'error': str(e)})

    def _do_stop_browser(self):
        """在浏览器线程中停止浏览器"""
        self.is_browser_running = False
        self.result_queue.put({'success': True})

    def _ensure_browser_running(self):
        """确保浏览器实例正在运行"""
        if self.is_browser_running and self.browser:
            return
        if self.browser_thread and self.browser_thread.is_alive():
            return

        self.browser_thread = threading.Thread(target=self._browser_worker, daemon=True)
        self.browser_thread.start()

        # 等待浏览器启动
        import time
        max_wait = 15
        waited = 0
        while not self.browser and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        if not self.browser:
            raise Exception("浏览器启动超时")

    def _send_command(self, cmd, timeout=30):
        """发送命令到浏览器线程并等待结果"""
        self.result_queue.queue.clear()  # 清空之前的结果
        self.command_queue.put(cmd)
        
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = self.result_queue.get(timeout=0.5)
                return result
            except queue.Empty:
                continue
        
        raise Exception("命令执行超时")

    def start_browser(self, account_id: str, account_name: str, profile_dir: str,
                     proxy: Optional[str] = None, url: str = "https://www.google.com"):
        """为账号启动新的浏览器上下文（标签页）"""
        if account_id in self.contexts and self.contexts[account_id].is_running:
            print(f"账号 {account_name} 已在运行")
            return False

        # 确保浏览器实例在运行
        self._ensure_browser_running()

        # 发送命令到浏览器线程执行
        cmd = {
            'action': 'new_context',
            'account_id': account_id,
            'account_name': account_name,
            'profile_dir': profile_dir,
            'proxy': proxy,
            'url': url
        }
        
        result = self._send_command(cmd)
        
        if result['success']:
            return True
        else:
            raise Exception(result.get('error', '未知错误'))

    def stop_browser(self, account_id: str):
        """停止指定账号的浏览器上下文"""
        if account_id not in self.contexts:
            return False

        # 发送命令到浏览器线程执行
        cmd = {
            'action': 'close_context',
            'account_id': account_id
        }
        
        result = self._send_command(cmd)
        
        # 如果没有活跃的上下文，关闭浏览器
        if result['success'] and not self.contexts:
            self._stop_browser_instance()
        
        return result['success']

    def _stop_browser_instance(self):
        """停止共享的浏览器实例"""
        if self.browser and self.is_browser_running:
            cmd = {'action': 'stop_browser'}
            self._send_command(cmd, timeout=5)
            print("🛑 共享浏览器已关闭")

    def is_running(self, account_id: str) -> bool:
        """检查账号是否在运行"""
        return account_id in self.contexts and self.contexts[account_id].is_running

    def stop_all(self):
        """停止所有账号"""
        for account_id in list(self.contexts.keys()):
            self.stop_browser(account_id)
        self._stop_browser_instance()
