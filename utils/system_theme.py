"""系统主题色获取工具 - 跨平台支持"""

import platform
from PyQt5.QtGui import QColor


def get_system_theme_color():
    """获取系统主题色
    
    Returns:
        QColor: 系统主题色，如果无法获取则返回默认颜色
    """
    system = platform.system()
    
    if system == "Windows":
        return _get_windows_theme_color()
    elif system == "Linux":
        return _get_linux_theme_color()
    else:
        # macOS 或其他系统，返回默认颜色
        return QColor("#009FAA")


def _get_windows_theme_color():
    """获取Windows系统主题色
    
    Returns:
        QColor: Windows系统主题色，如果无法获取则返回默认颜色
    """
    try:
        import winreg
        
        # Windows 10/11 使用注册表获取系统主题色
        # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
        # 或者使用 DWM API 获取系统强调色
        
        # 方法1: 尝试从注册表读取
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\DWM"
            )
            try:
                # Windows 10/11 的强调色（AccentColor）
                accent_color, _ = winreg.QueryValueEx(key, "AccentColor")
                # 注册表中的值是 BGR 格式的整数，需要转换为 RGB
                # 格式: 0x00BBGGRR
                r = accent_color & 0xFF
                g = (accent_color >> 8) & 0xFF
                b = (accent_color >> 16) & 0xFF
                return QColor(r, g, b)
            except FileNotFoundError:
                pass
            finally:
                winreg.CloseKey(key)
        except FileNotFoundError:
            pass
        
        # 方法2: 如果注册表方法失败，尝试使用 Windows API
        try:
            import ctypes
            
            # 使用 DwmGetColorizationColor API (需要 Windows Vista+)
            dwmapi = ctypes.windll.dwmapi
            
            # 定义函数签名
            DwmGetColorizationColor = dwmapi.DwmGetColorizationColor
            DwmGetColorizationColor.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_bool)]
            DwmGetColorizationColor.restype = ctypes.c_int  # HRESULT 是 int
            
            colorization_color = ctypes.c_uint32()
            colorization_opaque_blend = ctypes.c_bool()
            
            result = DwmGetColorizationColor(
                ctypes.byref(colorization_color),
                ctypes.byref(colorization_opaque_blend)
            )
            
            if result == 0:  # S_OK
                # 颜色值是 ARGB 格式
                color_value = colorization_color.value
                r = (color_value >> 16) & 0xFF
                g = (color_value >> 8) & 0xFF
                b = color_value & 0xFF
                return QColor(r, g, b)
        except (AttributeError, OSError, Exception):
            pass
        
    except Exception as e:
        print(f"获取Windows主题色失败: {e}")
    
    # 如果所有方法都失败，返回默认颜色
    return QColor("#009FAA")


def _get_linux_theme_color():
    """获取Linux系统主题色
    
    Returns:
        QColor: Linux系统主题色，如果无法获取则返回默认颜色
    """
    try:
        import subprocess
        import os
        
        # 方法1: 尝试从 GTK 主题获取
        # 检查是否在 GTK 环境中
        if os.environ.get("XDG_CURRENT_DESKTOP"):
            try:
                # 尝试使用 gsettings (GNOME)
                result = subprocess.run(
                    ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    # 如果成功，尝试获取主题色
                    # 注意：GTK主题色通常需要解析主题文件，这里简化处理
                    # 可以尝试读取 ~/.config/gtk-3.0/gtk.css 或类似文件
                    pass
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # 方法2: 尝试从 KDE 配置获取
        try:
            kde_config = os.path.expanduser("~/.config/kdeglobals")
            if os.path.exists(kde_config):
                # 可以解析 KDE 配置文件获取主题色
                # 这里简化处理，返回默认颜色
                pass
        except Exception:
            pass
        
        # 方法3: 尝试从环境变量获取
        # 某些桌面环境可能设置主题色相关的环境变量
        theme_color_env = os.environ.get("GTK_THEME_COLOR") or os.environ.get("QT_THEME_COLOR")
        if theme_color_env:
            try:
                return QColor(theme_color_env)
            except ValueError:
                pass
        
    except Exception as e:
        print(f"获取Linux主题色失败: {e}")
    
    # 如果所有方法都失败，返回默认颜色
    return QColor("#009FAA")

