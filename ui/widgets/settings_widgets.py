"""设置界面的UI组件"""

from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (
    FluentIcon as FIF, SettingCardGroup, OptionsSettingCard,
    SwitchSettingCard, PrimaryPushSettingCard, PushSettingCard,
    ExpandGroupSettingCard, qconfig
)


class AppearanceSettingsGroup(SettingCardGroup):
    """外观设置组"""
    
    def __init__(self, parent=None):
        super().__init__("外观设置", parent)
        self._init_cards()
    
    def _init_cards(self):
        """初始化卡片"""
        # 主题切换卡片
        self.theme_card = OptionsSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self
        )
        
        # 云母效果卡片
        self.mica_card = SwitchSettingCard(
            FIF.TRANSPARENT,
            "云母效果",
            "应用半透明到窗口和表面",
            parent=self,
            configItem=None
        )
        
        # 添加到设置组
        self.addSettingCard(self.theme_card)
        self.addSettingCard(self.mica_card)


class BehaviorSettingsGroup(SettingCardGroup):
    """行为设置组"""
    
    def __init__(self, parent=None):
        super().__init__("行为设置", parent)
        self._init_cards()
    
    def _init_cards(self):
        """初始化卡片"""
        # 自动检测路径卡片
        self.auto_detect_card = SwitchSettingCard(
            FIF.SEARCH,
            "启动时自动检测路径",
            "应用启动时自动检测希沃启动图片路径",
            parent=self
        )
        self.addSettingCard(self.auto_detect_card)
        
        # 启动图保护设置 - 手风琴卡片
        self.protection_expand_card = ExpandGroupSettingCard(
            FIF.LIBRARY,
            "启动图保护",
            "保护已替换的启动图不被软件还原",
            parent=self
        )
        
        # 防止图片还原开关
        self.prevent_restore_card = SwitchSettingCard(
            FIF.REMOVE_FROM,
            "防止图片还原",
            "为替换的图片设置只读+系统+隐藏属性",
            parent=self.protection_expand_card
        )
        self.prevent_restore_card.setChecked(False)
        
        # 立即移除所有保护按钮
        self.remove_all_protection_card = PushSettingCard(
            "立即移除",
            FIF.DELETE,
            "立即移除所有保护",
            "移除所有已经设置的文件保护属性",
            parent=self.protection_expand_card
        )
        
        # 将子卡片添加到手风琴卡片中
        self.protection_expand_card.addGroupWidget(self.prevent_restore_card)
        self.protection_expand_card.addGroupWidget(self.remove_all_protection_card)
        
        # 将手风琴卡片添加到行为设置组
        self.addSettingCard(self.protection_expand_card)


class AboutSettingsGroup(SettingCardGroup):
    """关于设置组"""
    
    def __init__(self, app_name, version, parent=None):
        super().__init__("关于", parent)
        self.app_name = app_name
        self.version = version
        self._init_cards()
    
    def _init_cards(self):
        """初始化卡片"""
        # 关于卡片
        self.about_card = PrimaryPushSettingCard(
            "访问项目",
            FIF.GITHUB,
            f"关于 {self.app_name}",
            f"版本 {self.version}",
            self
        )
        self.addSettingCard(self.about_card)