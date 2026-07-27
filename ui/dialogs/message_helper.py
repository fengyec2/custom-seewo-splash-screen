from PyQt6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition


class MessageHelper:
    """消息提示薄封装 — 直接委托给 InfoBar"""

    @staticmethod
    def show_success(parent, message: str, duration: int = 3000):
        InfoBar.success(title="", content=message, orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=duration, parent=parent)

    @staticmethod
    def show_error(parent, title: str, message: str):
        InfoBar.error(title=title, content=message, orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=5000, parent=parent)

    @staticmethod
    def show_warning(parent, title: str, message: str):
        InfoBar.warning(title=title, content=message, orient=Qt.Orientation.Horizontal, isClosable=True, position=InfoBarPosition.TOP, duration=4000, parent=parent)
