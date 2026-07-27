import os
import sys

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    
    在开发环境中，直接使用相对路径
    在打包后的环境中，使用 _MEIPASS 路径
    
    Args:
        relative_path: 相对路径（如 "images/preset"）
    
    Returns:
        资源文件的绝对路径
    """
    try:
        # PyInstaller 创建临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境，使用项目根目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_app_data_path(relative_path=""):
    """
    获取应用数据路径（用于存储配置、自定义图片等）
    
    Args:
        relative_path: 相对路径
    
    Returns:
        应用数据的绝对路径
    """
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        app_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        app_dir = os.path.abspath(".")
    
    if relative_path:
        return os.path.join(app_dir, relative_path)
    return app_dir


def ensure_dir(path):
    """确保目录存在（薄封装）"""
    os.makedirs(path, exist_ok=True)
