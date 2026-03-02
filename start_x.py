from camoufox.sync_api import Camoufox
import os
import shutil

# 1. 物理目录净化：彻底铲除导致报错的无效文件夹
ADDON_DIR = "/home/chenyi/.cache/camoufox/addons"
if os.path.exists(ADDON_DIR):
    for item in os.listdir(ADDON_DIR):
        item_path = os.path.join(ADDON_DIR, item)
        # 核心逻辑：如果文件夹里没有 manifest.json，直接删掉，防止库报错
        if os.path.isdir(item_path) and not os.path.exists(os.path.join(item_path, "manifest.json")):
            print(f"🧹 已清理干扰项: {item}")
            shutil.rmtree(item_path)

# 2. 锁定有效插件路径
valid_addons = []
for name in ["ublock", "canvasblocker", "fontblocker"]:
    path = os.path.join(ADDON_DIR, name)
    if os.path.exists(os.path.join(path, "manifest.json")):
        valid_addons.append(path)

print(f"🚀 正在启动全武装环境 (加载 {len(valid_addons)} 个真插件)...")

try:
    with Camoufox(
        os="windows",           # 伪装 Windows
        geoip=True,             # 匹配新加坡地理位置
        addons=valid_addons,    # 只加载刚才校验成功的插件
        # 明确排除默认插件，防止它再次尝试下载并报错
        exclude_addons=["ublock", "canvasblocker", "fontblocker", "ublock-origin"],
        proxy={"server": "http://127.0.0.1:7897"} # 对应你的 Clash 端口
    ) as browser:
        page = browser.new_page()
        
        print("🌐 正在直通 X (Twitter) 登录页面...")
        # 目标：X 官方登录流页面
        page.goto("https://x.com/i/flow/login", timeout=90000)
        
        print("\n✅ 窗口已成功弹出！")
        print("🛡️  右上角应有红色 uBlock 图标，请在此进行登录操作。")
        
        # 兼容处理终端回车问题
        print("\n💡 操作完成后，如果按回车没反应，请直接按 [Ctrl + C] 退出。")
        input("\n[运行中] 登录成功后，按回车或 Ctrl+C 关闭...")

except Exception as e:
    print(f"\n❌ 启动依然失败: {e}")
