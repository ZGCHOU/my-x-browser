# GitHub Actions 构建说明

本项目使用 GitHub Actions 自动构建跨平台的可执行文件。

## 工作流说明

### 1. build.yml - 持续集成构建
- **触发条件**: 推送到 main/master 分支、Pull Request、手动触发
- **构建产物**: Windows (.exe)、Linux (可执行文件 + tar.gz)、macOS (.app)
- **产物下载**: 在 Actions 页面可以下载构建好的文件

### 2. release.yml - 发布构建
- **触发条件**: 推送以 `v` 开头的标签 (如 v1.0.0)
- **自动发布**: 构建完成后自动上传到 GitHub Releases

## 构建产物

| 平台 | 文件名 | 说明 |
|------|--------|------|
| Windows | `CamoufoxManager.exe` | 单文件可执行程序 |
| Linux | `CamoufoxManager` | 单文件可执行程序 |
| Linux | `CamoufoxManager_Linux.tar.gz` | 便携版压缩包（含启动脚本） |
| macOS | `CamoufoxManager_macOS.tar.gz` | .app 应用包压缩包 |

## 使用方法

### 方式一：下载自动构建的版本
1. 进入 GitHub 仓库的 **Actions** 页面
2. 选择最新的构建工作流
3. 下载对应平台的构建产物

### 方式二：发布新版本
1. 推送标签触发发布:
```bash
git tag v1.0.0
git push origin v1.0.0
```
2. 等待构建完成后，在 **Releases** 页面下载

## 本地打包

如果需要在本地打包，可以使用提供的打包脚本:

```bash
# 安装依赖
pip install pyinstaller

# Windows
python build_exe.py

# 或手动打包
pyinstaller --onefile --windowed run_manager.py
```

## 注意事项

1. **Windows**: 需要 `pygetwindow` 才能使用窗口管理功能
2. **Linux**: 需要安装 `xdotool` 才能使用窗口管理功能
3. **macOS**: 需要授予辅助功能权限才能使用窗口管理功能

## 系统要求

- Windows 10/11
- Ubuntu 20.04+ / CentOS 8+ / 其他 Linux 发行版
- macOS 11+
