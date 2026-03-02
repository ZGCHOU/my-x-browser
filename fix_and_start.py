from camoufox.sync_api import Camoufox
import os
import shutil

# 1. 物理层面的最后检查
ADDON_DIR = "/home/chenyi/.cache/camoufox/addons"
expected = ["ublock", "canvasblocker", "fontblocker"]

print("🧹 正在进行最后的目录净化...")
if os.path.exists(ADDON_DIR):
    for item in os.listdir(ADDON_DIR):
        item_path = os.path.join(ADDON_DIR, item)
        # 如果文件夹里没 manifest.json，直接删掉
        if os.path.isdir(item_path) and not os.path.exists(os.path.join(item_path, "manifest.json")):
            print(f"🗑️ 删除无效文件夹: {item}")
            shutil.rmtree(item_path)

# 2. 重新扫描有效插件
valid_addons = []
if os.path.exists(ADDON_DIR):
    for name in expected:
        path = os.path.join(ADDON_DIR, name)
        if os.path.exists(os.path.join(path, "manifest.json")):
            valid_addons.append(path)

print(f"🚀 尝试加载以下有效插件: {[os.path.basename(p) for p in valid_addons]}")

def launch(with_addons=True):
    addons_to_load = valid_addons if with_addons else []
    try:
        with Camoufox(
            os="windows",
            geoip=True,
            addons=addons_to_load,
            # 禁止自动下载干扰
            exclude_addons=["ublock", "canvasblocker", "fontblocker", "ublock-origin"],
            proxy={"server": "http://127.0.0.1:7897"}
        ) as browser:
            page = browser.new_page()
            print("\n✨ 奇迹发生！窗口已弹出。")
            page.goto("https://abrahamjuliot.github.io/creepjs/")
            input("\n[预览模式] 操作完成后，按回车或 Ctrl+C 关闭...")
            return True
    except Exception as e:
        print(f"\n❌ {'带插件' if with_addons else '纯净'}模式启动失败: {e}")
        return False

# 优先尝试带插件启动
if not launch(with_addons=True):
    print("\n⚠️ 带插件启动失败，正在尝试【无插件纯净模式】启动以验证核心功能...")
    launch(with_addons=False)

