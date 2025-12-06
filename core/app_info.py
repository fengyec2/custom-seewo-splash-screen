# file core\app_info.py

"""应用信息配置

此文件包含应用的元信息，如版本号、作者等。
这些信息不会存储在 config.json 中。
"""

__version__ = "2.3.1"
__author__ = "fengyec2"
__app_name__ = "SeewoSplash"
__description__ = "SeewoSplash"
__license__ = "GPLv3"
__repository__ = "https://github.com/fengyec2/custom-seewo-splash-screen"

# 完整的应用信息字典
APP_INFO = {
    "version": __version__,
    "author": __author__,
    "app_name": __app_name__,
    "description": __description__,
    "license": __license__,
    "repository": __repository__,
}


def get_version():
    """获取版本号"""
    return __version__


def get_author():
    """获取作者"""
    return __author__


def get_app_name():
    """获取应用名称"""
    return __app_name__

def get_repository():
    """获取仓库名称"""
    return __repository__

def get_full_info():
    """获取完整的应用信息"""
    return APP_INFO.copy()


def get_version_string():
    """获取格式化的版本字符串"""
    return f"{__app_name__} v{__version__}"


def get_about_text():
    """获取关于信息文本"""
    return f"""{__app_name__} v{__version__}

{__description__}

作者: {__author__}
许可证: {__license__}
项目地址: {__repository__}
"""
