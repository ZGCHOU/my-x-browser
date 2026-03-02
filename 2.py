from camoufox.sync_api import Camoufox
import os, shutil

# 1. 物理目录净化 (防止 manifest.json missing 报错)
ADDON_DIR = os.path.expanduser("~/.cache/camoufox/addons")
if os.path.exists(ADDON_DIR):
    for item in os.listdir(ADDON_DIR):
        path = os.path.join(ADDON_DIR, item)
        if os.path.isdir(path) and not os.path.exists(os.path.join(path, "manifest.json")):
            shutil.rmtree(path)

# 2. 定义账号存放点 (实现多开隔离)
# 换新账号只需修改这里的文件夹名，如 acc_2, acc_3
profile_dir = os.path.abspath("./profiles/acc_1")
os.makedirs(profile_dir, exist_ok=True)

# 3. 锁定有效插件
valid_addons = [os.path.join(ADDON_DIR, n) for n in ["ublock", "canvasblocker", "fontblocker"] 
                if os.path.exists(os.path.join(ADDON_DIR, n, "manifest.json"))]

try:
    with Camoufox(
        os="windows",           # 伪装系统
        geoip=True,             # 对齐地理位置
        addons=valid_addons,    # 加载真插件
        persistent_directory=profile_dir, # 物理隔离 Cookie
        proxy={"server": "http://127.0.0.1:7897"}, # 绑定 IP
        exclude_addons=["ublock", "canvasblocker", "fontblocker", "ublock-origin"]
    ) as browser:
        page = browser.new_page()
        page.goto("https://x.com/i/flow/login", timeout=90000) # 直达 X
        input("\n✅ 已成功启动！登录后按回车或 Ctrl+C 退出...")
except Exception as e:
    print(f"❌ 启动失败: {e}")
