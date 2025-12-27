from PyQt5.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition


class MessageHelper:
    """消息提示辅助类"""
    
    @staticmethod
    def show_success(parent, message: str, duration: int = 3000):
        """显示成功消息
        
        Args:
            parent: 父窗口
            message: 消息内容
            duration: 显示持续时间(毫秒)
        """
        InfoBar.success(
            title="",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=parent
        )
    
    @staticmethod
    def show_error(parent, title: str, message: str):
        """显示错误消息
        
        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容
        """
        InfoBar.error(
            title=title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=parent
        )
    
    @staticmethod
    def show_warning(parent, title: str, message: str):
        """显示警告消息
        
        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容
        """
        InfoBar.warning(
            title=title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=4000,
            parent=parent
        )
