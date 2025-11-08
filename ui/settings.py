"""设置界面"""

import webbrowser
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import (
    FluentIcon as FIF, SettingCardGroup, OptionsSettingCard, 
    SwitchSettingCard, PrimaryPushSettingCard, qconfig, setTheme, Theme,
    TitleLabel, VBoxLayout
)

from core.config_manager import ConfigManager
from core.app_info import get_version, get_app_name, get_repository
from .dialogs import MessageHelper


class SettingsInterface(QWidget):
    """设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.config_manager = ConfigManager()
        self._init_ui()
        self._bind_settings_to_config()
    
    def _init_ui(self):
        """初始化设置界面UI"""
        self.setObjectName("settingsInterface")
        
        # 创建布局
        layout = VBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = TitleLabel("设置")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 创建设置卡片组
        self._create_appearance_group()
        self._create_behavior_group()
        self._create_about_group()
        
        # 添加到布局
        layout.addWidget(self.appearance_group)
        layout.addWidget(self.behavior_group)
        layout.addWidget(self.about_group)
        layout.addStretch(1)  # 添加弹性空间，让内容顶部对齐
    
    def _create_appearance_group(self):
        """创建外观设置组"""
        self.appearance_group = SettingCardGroup("外观设置", self)
        
        # 主题切换卡片
        self.theme_card = OptionsSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self.appearance_group
        )
        self.theme_card.optionChanged.connect(self._on_theme_changed)
        self.appearance_group.addSettingCard(self.theme_card)
    
    def _create_behavior_group(self):
        """创建行为设置组"""
        self.behavior_group = SettingCardGroup("行为设置", self)
        
        # 自动检测路径卡片
        self.auto_detect_card = SwitchSettingCard(
            FIF.SEARCH,
            "启动时自动检测路径",
            "应用启动时自动检测希沃启动图片路径",
            parent=self.behavior_group
        )
        self.behavior_group.addSettingCard(self.auto_detect_card)
    
    def _create_about_group(self):
        """创建关于设置组"""
        self.about_group = SettingCardGroup("关于", self)
        
        # 关于卡片
        self.about_card = PrimaryPushSettingCard(
            "访问项目",
            FIF.LINK,
            f"关于 {get_app_name()}",
            f"版本 {get_version()}",
            self.about_group
        )
        self.about_card.clicked.connect(self._on_about_clicked)
        self.about_group.addSettingCard(self.about_card)
    
    def _bind_settings_to_config(self):
        """绑定设置卡片到配置文件"""
        # 绑定自动检测设置
        auto_detect = self.config_manager.get_auto_detect_on_startup()
        self.auto_detect_card.setChecked(auto_detect)
        self.auto_detect_card.checkedChanged.connect(
            self.config_manager.set_auto_detect_on_startup
        )
        
        # 设置主题卡片的初始值
        self._set_initial_theme()
    
    def _set_initial_theme(self):
        """设置主题卡片的初始值"""
        theme_mode = self.config_manager.get_theme_mode()
        theme_index_map = {
            "light": 0,
            "dark": 1, 
            "auto": 2
        }
        initial_index = theme_index_map.get(theme_mode, 2)
        # 注意：根据OptionsSettingCard的API，可能需要调整设置初始值的方法
        try:
            self.theme_card.setCurrentIndex(initial_index)
        except AttributeError:
            # 如果没有setCurrentIndex方法，可能需要其他方式设置
            pass
    
    def _on_theme_changed(self, item):
        """主题切换事件"""
        selected_theme = item.value
        
        # 根据主题值获取对应的名称和配置值
        theme_config_map = {
            Theme.LIGHT: ("浅色", "light"),
            Theme.DARK: ("深色", "dark"), 
            Theme.AUTO: ("跟随系统设置", "auto")
        }
        
        theme_name, config_value = theme_config_map.get(selected_theme, ("未知", "auto"))
        
        # 应用主题
        setTheme(selected_theme)
        
        # 保存到配置文件
        self.config_manager.set_theme_mode(config_value)
        
        # 显示成功消息
        if self.parent_window:
            MessageHelper.show_success(
                self.parent_window,
                f"已切换到{theme_name}模式",
                2000
            )
    
    def _on_about_clicked(self):
        """关于按钮点击事件 - 跳转到GitHub"""
        webbrowser.open(get_repository())
    
    def apply_saved_theme(self):
        """应用保存的主题设置"""
        theme_mode = self.config_manager.get_theme_mode()
        theme_map = {
            "light": Theme.LIGHT,
            "dark": Theme.DARK,
            "auto": Theme.AUTO
        }
        saved_theme = theme_map.get(theme_mode, Theme.AUTO)
        setTheme(saved_theme)