import os, sys, shutil
from camoufox.sync_api import Camoufox

# 自动处理路径：支持源码运行和 EXE 运行
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADDON_DIR = os.path.join(BASE_DIR, "addons")
PROFILE_DIR = os.path.join(BASE_DIR, "profiles", "main_account")

def start():
    os.makedirs(ADDON_DIR, exist_ok=True)
    # 插件物理净化
    if os.path.exists(ADDON_DIR):
        for item in os.listdir(ADDON_DIR):
            p = os.path.join(ADDON_DIR, item)
            if os.path.isdir(p) and not os.path.exists(os.path.join(p, "manifest.json")):
                shutil.rmtree(p)

    valid_addons = [os.path.join(ADDON_DIR, n) for n in ["ublock", "canvasblocker", "fontblocker"] 
                    if os.path.exists(os.path.join(ADDON_DIR, n, "manifest.json"))]

    print("🚀 正在启动环境 (初次运行会自动下载必要组件)...")
    try:
        with Camoufox(
            path=PROFILE_DIR, os="windows", geoip=True, addons=valid_addons,
            exclude_addons=["ublock", "canvasblocker", "fontblocker", "ublock-origin"],
            proxy={"server": "http://127.0.0.1:7897"} # 对方也需要开 Clash 端口
        ) as browser:
            page = browser.new_page()
            page.goto("https://x.com/i/flow/login", timeout=90000)
            input("\n✅ 启动成功！按回车退出...")
    except Exception as e:
        print(f"❌ 出错: {e}")
        input("按回车退出...")

if __name__ == "__main__":
    start()
