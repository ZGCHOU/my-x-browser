"""窗口管理模块 - 管理和排列浏览器窗口"""
import subprocess
import platform
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class WindowInfo:
    """窗口信息"""
    window_id: str
    title: str
    x: int
    y: int
    width: int
    height: int
    account_name: Optional[str] = None


class WindowManager:
    """窗口管理器 - 用于排列和管理浏览器窗口"""
    
    def __init__(self):
        self.system = platform.system()
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查系统依赖"""
        if self.system == "Linux":
            # 检查是否有 X11 和必要的工具
            try:
                result = subprocess.run(
                    ["echo", "$DISPLAY"], 
                    capture_output=True, 
                    text=True, 
                    shell=True
                )
                self.has_x11 = result.stdout.strip() != ""
            except:
                self.has_x11 = False
        elif self.system == "Darwin":  # macOS
            # 检查 osascript 是否可用
            success, _ = self._run_command(["which", "osascript"])
            self.has_osascript = success
            if not success:
                print("⚠️ 警告: macOS 上未找到 osascript，窗口管理功能可能受限")
            else:
                print("✅ macOS 窗口管理可用（需要辅助功能权限）")
        else:
            self.has_x11 = False
    
    def _run_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """运行系统命令"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, str(e)
    
    def list_windows(self) -> List[WindowInfo]:
        """列出所有窗口"""
        windows = []
        
        if self.system == "Linux" and self.has_x11:
            windows = self._list_windows_linux()
        elif self.system == "Windows":
            windows = self._list_windows_windows()
        elif self.system == "Darwin":
            windows = self._list_windows_macos()
        
        return windows
    
    def _list_windows_linux(self) -> List[WindowInfo]:
        """Linux: 使用 xdotool 或 wmctrl 列出窗口"""
        windows = []
        window_ids = set()
        
        # 方法1: 优先搜索包含方括号标题的窗口（我们的账号标记）
        # 这是最快的方法，因为我们设置了 [账号名] 前缀
        success, output = self._run_command([
            "xdotool", "search", "--name", "[", "--all"
        ])
        if success and output.strip():
            window_ids.update(output.strip().split("\n"))
        
        # 方法2: 尝试搜索类名
        if not window_ids:
            for class_name in ["camoufox-default", "camoufox", "Camoufox", "firefox", "Firefox", "Navigator"]:
                success, output = self._run_command([
                    "xdotool", "search", "--class", class_name, 
                    "--all", "--sync"
                ])
                if success and output.strip():
                    window_ids.update(output.strip().split("\n"))
        
        # 尝试搜索 Mozilla 类窗口（Camoufox 基于 Firefox）
        if not window_ids:
            success, output = self._run_command([
                "xdotool", "search", "--class", "Mozilla", "--all"
            ])
            if success and output.strip():
                window_ids.update(output.strip().split("\n"))
        
        # 最后尝试获取所有窗口并过滤标题
        if not window_ids:
            success, output = self._run_command([
                "xdotool", "search", "--class", ""
            ])
            if success and output.strip():
                # 过滤出包含 Camoufox 或 [ 的窗口
                for window_id in output.strip().split("\n"):
                    window_id = window_id.strip()
                    if not window_id:
                        continue
                    _, title = self._run_command([
                        "xdotool", "getwindowname", window_id
                    ])
                    title = title.strip()
                    if "camoufox" in title.lower() or "[" in title:
                        window_ids.add(window_id)
        
        for window_id in window_ids:
            window_id = window_id.strip()
            if not window_id or not window_id.isdigit():
                continue
                
            # 获取窗口标题
            _, title = self._run_command([
                "xdotool", "getwindowname", window_id
            ])
            title = title.strip()
            
            # 跳过无效/空窗口
            if not title or title in ["n/a", "N/A", ""]:
                continue
            
            # 只保留包含账号标记 [xxx] 的窗口，或者是浏览器窗口
            is_browser = any(keyword in title.lower() for keyword in [
                "firefox", "camoufox", "chrome", "chromium", "mozilla"
            ])
            has_account_tag = "[" in title and "]" in title
            
            if not (is_browser or has_account_tag):
                continue
            
            # 获取窗口位置和大小
            _, geometry = self._run_command([
                "xdotool", "getwindowgeometry", window_id
            ])
            
            # 解析几何信息
            x, y, width, height = 0, 0, 1200, 800
            for line in geometry.split("\n"):
                if "Position:" in line:
                    try:
                        parts = line.split("Position: ")[1].split(",")
                        if len(parts) == 2:
                            x = int(parts[0].strip())
                            y = int(parts[1].strip().split("(")[0].strip())
                    except:
                        pass
                elif "Geometry:" in line:
                    try:
                        parts = line.split("Geometry: ")[1].split("x")
                        if len(parts) == 2:
                            width = int(parts[0].strip())
                            height = int(parts[1].strip())
                    except:
                        pass
            
            # 提取账号名（从标题中）
            account_name = None
            if "[" in title and "]" in title:
                try:
                    account_name = title.split("[")[1].split("]")[0]
                except:
                    pass
            
            windows.append(WindowInfo(
                window_id=window_id,
                title=title,
                x=x, y=y,
                width=width, height=height,
                account_name=account_name
            ))
        
        return windows
    
    def _list_windows_windows(self) -> List[WindowInfo]:
        """Windows: 使用 pygetwindow 或 win32gui"""
        windows = []
        try:
            import pygetwindow as gw
            for window in gw.getAllWindows():
                if "firefox" in window.title.lower() or "camoufox" in window.title.lower():
                    account_name = None
                    title = window.title
                    if "[" in title and "]" in title:
                        account_name = title.split("[")[1].split("]")[0]
                    
                    windows.append(WindowInfo(
                        window_id=str(window._hWnd),
                        title=title,
                        x=window.left,
                        y=window.top,
                        width=window.width,
                        height=window.height,
                        account_name=account_name
                    ))
        except ImportError:
            pass
        return windows
    
    def _list_windows_macos(self) -> List[WindowInfo]:
        """macOS: 使用 osascript 获取 Firefox 窗口"""
        windows = []
        
        # 先尝试获取 Firefox 进程ID
        pid_script = '''
        tell application "System Events"
            set firefoxProcesses to (every process whose name contains "firefox" or name contains "Firefox")
            set pids to {}
            repeat with proc in firefoxProcesses
                set end of pids to unix id of proc
            end repeat
            return pids as string
        end tell
        '''
        
        success, output = self._run_command(["osascript", "-e", pid_script])
        
        if not success or not output.strip():
            # 备用方案：尝试直接通过应用名获取
            return self._list_windows_macos_fallback()
        
        pids = output.strip().split(", ")
        
        for pid in pids:
            pid = pid.strip()
            if not pid:
                continue
                
            # 获取该进程的所有窗口
            window_script = f'''
            tell application "System Events"
                tell (first process whose unix id is {pid})
                    set windowList to {{}}
                    repeat with i from 1 to (count of windows)
                        set win to window i
                        try
                            set winName to name of win
                            set winPos to position of win
                            set winSize to size of win
                            set end of windowList to {{winName, (item 1 of winPos) as string, (item 2 of winPos) as string, (item 1 of winSize) as string, (item 2 of winSize) as string, i as string}}
                        on error
                            set end of windowList to {{"Unknown", "0", "0", "800", "600", i as string}}
                        end try
                    end repeat
                    return windowList as string
                end tell
            end tell
            '''
            
            success, output = self._run_command(["osascript", "-e", window_script])
            
            if success and output.strip():
                try:
                    # 解析 AppleScript 列表格式: {{name, x, y, w, h, idx}, {name2, ...}}
                    content = output.strip()
                    if content.startswith("{{") and content.endswith("}}"):
                        content = content[2:-2]
                        
                    # 分割窗口条目
                    entries = content.split("}, {")
                    for entry in entries:
                        parts = entry.split(", ")
                        if len(parts) >= 6:
                            title = parts[0].strip().strip('"')
                            x = int(parts[1].strip())
                            y = int(parts[2].strip())
                            width = int(parts[3].strip())
                            height = int(parts[4].strip())
                            idx = parts[5].strip()
                            
                            # 提取账号名（从标题中）
                            account_name = None
                            if "[" in title and "]" in title:
                                account_name = title.split("[")[1].split("]")[0]
                            
                            windows.append(WindowInfo(
                                window_id=f"{pid}_{idx}",
                                title=title,
                                x=x, y=y,
                                width=width, height=height,
                                account_name=account_name
                            ))
                except Exception as e:
                    print(f"解析窗口信息失败: {e}, 输出: {output[:100]}")
        
        if not windows:
            # 备用方案
            return self._list_windows_macos_fallback()
        
        return windows
    
    def _list_windows_macos_fallback(self) -> List[WindowInfo]:
        """macOS 备用方案：只获取窗口标题"""
        windows = []
        
        # 简化版：只获取窗口标题
        script = '''
        tell application "Firefox"
            set winList to {}
            repeat with i from 1 to (count of windows)
                try
                    set w to window i
                    set t to name of w
                    set end of winList to {t, i}
                on error
                    set end of winList to {"Unknown", i}
                end try
            end repeat
            return winList as string
        end tell
        '''
        
        success, output = self._run_command(["osascript", "-e", script])
        
        if success and output.strip():
            try:
                content = output.strip()
                # 解析: {{title, idx}, {title2, idx2}}
                if content.startswith("{{") and content.endswith("}}"):
                    content = content[2:-2]
                    
                entries = content.split("}, {")
                for entry in entries:
                    parts = entry.split(", ")
                    if len(parts) >= 2:
                        title = parts[0].strip().strip('"')
                        idx = parts[1].strip()
                        
                        # 提取账号名
                        account_name = None
                        if "[" in title and "]" in title:
                            account_name = title.split("[")[1].split("]")[0]
                        
                        windows.append(WindowInfo(
                            window_id=idx,
                            title=title,
                            x=100, y=100,  # 默认值
                            width=1200, height=800,
                            account_name=account_name
                        ))
            except Exception as e:
                print(f"备用方案解析失败: {e}")
        
        return windows
    
    def focus_window(self, window_id: str) -> bool:
        """聚焦到指定窗口"""
        if self.system == "Linux":
            success, _ = self._run_command([
                "xdotool", "windowactivate", "--sync", window_id
            ])
            return success
        elif self.system == "Windows":
            try:
                import pygetwindow as gw
                hwnd = int(window_id)
                window = gw.Window(hwnd)
                window.activate()
                return True
            except:
                return False
        elif self.system == "Darwin":  # macOS
            # window_id 格式: pid_idx 或 单纯索引
            if "_" in window_id:
                idx = window_id.split("_")[1]
            else:
                idx = window_id
            
            # 通过窗口索引激活
            script = f'''
            tell application "Firefox"
                activate
                set index of window {idx} to 1
            end tell
            '''
            success, output = self._run_command(["osascript", "-e", script])
            if not success:
                print(f"聚焦窗口失败: {output}")
            return success
        return False
    
    def move_window(self, window_id: str, x: int, y: int, width: int, height: int) -> bool:
        """移动和调整窗口大小"""
        if self.system == "Linux":
            success, _ = self._run_command([
                "xdotool", "windowmove", "--sync", window_id, str(x), str(y)
            ])
            if success:
                success, _ = self._run_command([
                    "xdotool", "windowsize", "--sync", window_id, str(width), str(height)
                ])
            return success
        elif self.system == "Windows":
            try:
                import pygetwindow as gw
                hwnd = int(window_id)
                window = gw.Window(hwnd)
                window.moveTo(x, y)
                window.resizeTo(width, height)
                return True
            except:
                return False
        elif self.system == "Darwin":  # macOS
            # window_id 格式: pid_idx 或 单纯索引
            if "_" in window_id:
                idx = window_id.split("_")[1]
            else:
                idx = window_id
            
            script = f'''
            tell application "System Events"
                tell application process "Firefox"
                    set position of window {idx} to {{{x}, {y}}}
                    set size of window {idx} to {{{width}, {height}}}
                end tell
            end tell
            '''
            success, output = self._run_command(["osascript", "-e", script])
            if not success:
                # 备用：尝试通过应用名
                script2 = f'''
                tell application "Firefox"
                    set bounds of window {idx} to {{{x}, {y}, {x + width}, {y + height}}}
                end tell
                '''
                success2, _ = self._run_command(["osascript", "-e", script2])
                return success2
            return success
        return False
    
    def tile_windows(self, window_ids: List[str], screen_width: int = 1920, 
                     screen_height: int = 1080, margin: int = 10) -> bool:
        """平铺排列窗口"""
        if not window_ids:
            return False
        
        count = len(window_ids)
        if count == 1:
            # 单个窗口居中
            return self.move_window(
                window_ids[0],
                (screen_width - 1200) // 2,
                (screen_height - 800) // 2,
                1200, 800
            )
        
        # 计算网格布局
        cols = int(count ** 0.5)
        if cols * cols < count:
            cols += 1
        rows = (count + cols - 1) // cols
        
        # 计算每个窗口的大小
        avail_width = screen_width - (cols + 1) * margin
        avail_height = screen_height - (rows + 1) * margin - 50  # 留出顶部空间
        
        window_width = avail_width // cols
        window_height = avail_height // rows
        
        # 排列窗口
        for i, window_id in enumerate(window_ids):
            row = i // cols
            col = i % cols
            
            x = margin + col * (window_width + margin)
            y = margin + row * (window_height + margin) + 50
            
            self.move_window(window_id, x, y, window_width, window_height)
        
        return True
    
    def cascade_windows(self, window_ids: List[str], start_x: int = 100, 
                       start_y: int = 100, offset: int = 40) -> bool:
        """层叠排列窗口"""
        if not window_ids:
            return False
        
        for i, window_id in enumerate(window_ids):
            x = start_x + i * offset
            y = start_y + i * offset
            self.move_window(window_id, x, y, 1200, 800)
        
        return True
    
    def minimize_all(self, window_ids: List[str]) -> bool:
        """最小化所有窗口"""
        for window_id in window_ids:
            if self.system == "Linux":
                self._run_command(["xdotool", "windowminimize", window_id])
            elif self.system == "Windows":
                try:
                    import pygetwindow as gw
                    gw.Window(int(window_id)).minimize()
                except:
                    pass
            elif self.system == "Darwin":  # macOS
                # window_id 格式: pid_idx 或 单纯索引
                if "_" in window_id:
                    idx = window_id.split("_")[1]
                else:
                    idx = window_id
                
                script = f'''
                tell application "System Events"
                    tell application process "Firefox"
                        set miniaturized of window {idx} to true
                    end tell
                end tell
                '''
                self._run_command(["osascript", "-e", script])
        return True
    
    def get_window_by_account(self, account_name: str) -> Optional[WindowInfo]:
        """根据账号名查找窗口"""
        windows = self.list_windows()
        for window in windows:
            if window.account_name == account_name:
                return window
        return None
