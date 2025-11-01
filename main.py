import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow

def main():
    # 在创建QApplication之前设置高DPI支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 设置高DPI缩放策略
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # 创建应用程序
    app = QApplication(sys.argv)
    # 默认使用系统主题色（仅在 Windows 和 macOS 可用）
    try:
        if sys.platform in ["win32", "darwin"]:
            # qfluentwidgets 提供 setThemeColor，qframelesswindow 提供 getSystemAccentColor
            from qfluentwidgets import setThemeColor  # type: ignore
            from qframelesswindow.utils import getSystemAccentColor  # type: ignore

            # 仅临时应用系统主题色，不写入配置（save=False）
            try:
                setThemeColor(getSystemAccentColor(), save=False)
            except Exception:
                # 如果失败，继续启动但不阻塞
                pass
    except Exception:
        # qfluentwidgets 或 qframelesswindow 不可用，忽略
        pass
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
