from camoufox.sync_api import Camoufox
import os

# 1. 自动扫描并锁定有效的真实插件路径
addon_base = "/home/chenyi/.cache/camoufox/addons"
my_addons = []

if os.path.exists(addon_base):
    for folder in os.listdir(addon_base):
        full_path = os.path.join(addon_base, folder)
        # 只有目录下确实存在 manifest.json 才会加入加载列表
        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "manifest.json")):
            my_addons.append(full_path)

print(f"🎨 正在启动全武装浏览器...")
print(f"🛡️  已检测到并准备加载的真实插件: {[os.path.basename(p) for p in my_addons]}")

try:
    with Camoufox(
        os="windows",           # 伪装成 Windows 环境
        geoip=True,             # 匹配新加坡代理 IP 的地理位置
        addons=my_addons,       # 仅加载验证通过的真实插件
        # 强制排除默认插件下载，防止干扰
        exclude_addons=["ublock", "canvasblocker", "fontblocker"],
        proxy={"server": "http://127.0.0.1:7897"} # 你的 Clash 端口
    ) as browser:
        page = browser.new_page()
        
        # 访问指纹检测页查看全套伪装效果
        print("🔍 正在打开高级指纹检测页 (CreepJS)...")
        page.goto("https://abrahamjuliot.github.io/creepjs/", timeout=90000)
        
        print("\n✅ 成功弹出！请看浏览器窗口。")
        print("-" * 40)
        print("👀 验证清单：")
        print("1. 右上角：是否有红色盾牌 (uBlock) 等图标？")
        print("2. 页面中：Timezone 是否显示为新加坡？")
        print("-" * 40)
        
        input("\n[预览模式] 查看完毕后，按回车键 [Enter] 彻底关闭...")

except Exception as e:
    print(f"\n❌ 启动失败。报错细节: {e}")
