# SeewoSplash - 希沃白板启动图片自定义工具

<div align="center">

![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)
![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg)

一个用于自定义希沃白板启动画面的简单工具

[功能特性](#✨功能特性) • [安装使用](#🚀安装使用) • [构建](#📦构建) • [常见问题](#🔧常见问题) • [许可证](#📄许可证)

</div>

---

## 📖简介

SeewoSplash 是一个 Fluent 风格的图形化工具，允许你自定义希沃白板的启动画面。告别单调的默认启动图片，让你的希沃白板展现个性！

### ✨功能特性

- 🎨 **预设图片** - 内置启动图片
- 📁 **自定义导入** - 支持导入自己的 PNG 图片
- 🔍 **路径检测** - 检测希沃白板安装路径
- 💾 **自动备份** - 替换前备份原始图片，支持还原
- 🖼️ **图片管理** - 支持重命名、删除自定义图片

### 🖼️应用截图

|  深色模式  |  浅色模式  |
|-----------|-----------|
| ![主页面-深色](docs/screenshots/main_window_dark.png "主页面-深色") | ![主页面-浅色](docs/screenshots/main_window_light.png "主页面-浅色") |

## 🚀安装使用

### 方式一：下载发行版（推荐）

1. 前往 [Releases](https://github.com/fengyec2/custom-seewo-splash-screen/releases) 页面
2. 下载最新版本的 SeewoSplash.zip`
3. 解压后运行 `SeewoSplash.exe` 即可使用

### 方式二：从源码运行

#### 环境要求

- Python 3.8 或更高版本
- Windows 操作系统

#### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/fengyec2/custom-seewo-splash-screen.git
cd custom-seewo-splash-screen
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **运行程序**

```bash
python main.py
```

## 📦构建

如果你想自己构建可执行文件：

```bash
# 安装 PyInstaller
pip install pyinstaller

# 构建
python build.py
```

构建完成后，可执行文件将位于 `dist/` 目录下。

## 📸使用说明

### 首次使用

1. **启动程序** - 运行 `SeewoSplash.exe`
2. **检测路径** - 点击"检测路径"按钮，程序会自动查找希沃白板安装路径
3. **选择图片** - 从图片列表中选择启动图片
4. **替换** - 点击"替换启动图片"按钮即可

### 导入自定义图片

1. 点击"导入图片"按钮
2. 选择一张 PNG 格式的图片
3. 图片将被自动导入到自定义图片库

### 还原原始图片

如果想恢复希沃白板的原始启动图片：

1. 点击"从备份还原"按钮
2. 程序会自动从备份恢复原始图片

## 📁项目结构

```
custom-seewo-splash-screen/
├── main.py                      # 程序入口
├── requirements.txt             # 依赖列表
├── build.py                    # 构建脚本
├── assets/                     # 资源文件
│   ├── icon.ico               # 程序图标
│   └── preset/                # 预设启动图片
├── core/                       # 核心功能模块
│   ├── app_info.py            # 应用信息管理
│   ├── config_manager.py      # 配置管理
│   ├── image_manager.py       # 图片管理
│   └── replacer.py            # 图片替换
├── ui/                         # 用户界面
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   ├── widgets/               # UI组件
│   │   ├── __init__.py
│   │   ├── path_card.py       # 路径信息卡片
│   │   ├── image_list.py      # 图片列表组件
│   │   └── action_bar.py      # 操作按钮栏
│   └── dialogs/               # 对话框
│       ├── __init__.py
│       ├── message_helper.py  # 消息提示辅助类
│       └── path_history_dialog.py  # 历史路径对话框
└── utils/                      # 工具模块
    ├── admin_helper.py        # 管理员权限
    ├── resource_path.py       # 资源路径管理
    └── path_detector.py       # 路径检测
```

## 🔧常见问题

### Q: 为什么检测不到希沃白板路径？

A: 请确保：
1. 希沃白板已正确安装
2. 程序具有管理员权限
3. 可以尝试手动选择路径

### Q: 替换后图片没有变化？

A: 请尝试：
1. 完全退出希沃白板后重新打开
2. 检查是否替换成功（查看浮窗提示）
3. 使用"从备份还原"后重新替换

### Q: 可以恢复到原始图片吗？

A: 可以！程序在首次替换时会自动备份原始图片，点击"从备份还原"即可恢复。

## 🤝贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄许可证

本项目采用 GNU General Public License v3.0 许可证 - 详见 [LICENSE](LICENSE)

## 📧联系方式

- Issue: [提交问题](https://github.com/fengyec2/custom-seewo-splash-screen/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by [fengyec2](https://github.com/fengyec2)

</div>