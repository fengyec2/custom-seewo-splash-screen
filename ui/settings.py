"""设置界面"""

import webbrowser
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import (
    FluentIcon as FIF, SettingCardGroup, OptionsSettingCard, 
    SwitchSettingCard, PrimaryPushSettingCard, qconfig, setTheme, Theme,
    TitleLabel, ScrollArea, ExpandLayout, ColorSettingCard, setThemeColor,
    CustomColorSettingCard
)

from core.config_manager import ConfigManager
from core.app_info import get_version, get_app_name, get_repository
from .dialogs import MessageHelper


class SettingsInterface(ScrollArea):
    """设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_window = parent
        self.config_manager = ConfigManager()
        self._is_applying_saved_settings = False  # 添加标志
        
        # 创建滚动容器
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        self._init_ui()
        self._bind_settings_to_config()
    
    def _init_ui(self):
        """初始化设置界面UI"""
        # 设置滚动区域属性
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingsInterface")
        self.enableTransparentBackground()
        
        # 设置滚动容器对象名
        self.scrollWidget.setObjectName('scrollWidget')
        
        # 标题 - 使用绝对定位
        self.settingLabel = TitleLabel("设置", self)
        self.settingLabel.setObjectName('settingLabel')
        self.settingLabel.move(36, 30)
        
        # 创建设置卡片组
        self._create_appearance_group()
        self._create_behavior_group()
        self._create_about_group()
        
        # 初始化布局
        self._init_layout()
    
    def _init_layout(self):
        """初始化布局"""
        # 设置布局参数
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        
        # 添加设置组到布局
        self.expandLayout.addWidget(self.appearance_group)
        self.expandLayout.addWidget(self.behavior_group)
        self.expandLayout.addWidget(self.about_group)
    
    def _create_appearance_group(self):
        """创建外观设置组"""
        self.appearance_group = SettingCardGroup("外观设置", self.scrollWidget)
        
        # 主题切换卡片 - 直接绑定配置项
        self.theme_card = OptionsSettingCard(
            qconfig.themeMode,
            FIF.BRUSH,
            "应用主题",
            "调整你的应用外观",
            texts=["浅色", "深色", "跟随系统设置"],
            parent=self.appearance_group
        )
        
        # 自定义主题色卡片
        self.custom_color_card = CustomColorSettingCard(
            qconfig.themeColor,
            FIF.BRUSH,
            "自定义主题色",
            "选择你喜欢的主题色",
            parent=self.appearance_group
        )
        
        # 云母效果卡片 - 仅在Windows 11上可用
        self.mica_card = SwitchSettingCard(
            FIF.TRANSPARENT,
            "云母效果",
            "应用半透明到窗口和表面",
            parent=self.appearance_group,
            configItem=None  # 不使用自动绑定
        )
        
        # 绑定信号
        qconfig.themeChanged.connect(setTheme)
        self.theme_card.optionChanged.connect(self._on_theme_changed)
        self.custom_color_card.colorChanged.connect(self._on_custom_color_changed)
        self.mica_card.checkedChanged.connect(self._on_mica_effect_changed)
        
        # 添加到设置组
        self.appearance_group.addSettingCard(self.theme_card)
        self.appearance_group.addSettingCard(self.custom_color_card)
        self.appearance_group.addSettingCard(self.mica_card)
    
    def _create_behavior_group(self):
        """创建行为设置组"""
        self.behavior_group = SettingCardGroup("行为设置", self.scrollWidget)
        
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
        self.about_group = SettingCardGroup("关于", self.scrollWidget)
        
        # 关于卡片
        self.about_card = PrimaryPushSettingCard(
            "访问项目",
            FIF.GITHUB,
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
        
        # 绑定云母效果设置（如果配置管理器支持）
        try:
            mica_enabled = self.config_manager.get_mica_effect()
            self.mica_card.setChecked(mica_enabled)
        except AttributeError:
            # 如果配置管理器不支持云母效果，使用默认值
            self.mica_card.setChecked(False)
    
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
        
        # 保存到配置文件
        self.config_manager.set_theme_mode(config_value)
        
        # 显示成功消息
        if self.parent_window:
            MessageHelper.show_success(
                self.parent_window,
                f"已切换到{theme_name}模式",
                2000
            )
    
    def _on_theme_color_changed(self, color):
        """主题色变化事件"""
        # 设置全局主题色
        setThemeColor(color)
        
        # 保存到配置文件（如果配置管理器支持）
        try:
            self.config_manager.set_theme_color(color.name())
        except AttributeError:
            # 如果配置管理器不支持主题色配置，跳过
            pass
        
        # 显示成功消息
        if self.parent_window:
            MessageHelper.show_success(
                self.parent_window,
                "主题色已更新",
                2000
            )
    
    def _on_custom_color_changed(self, color):
        """自定义主题色变化事件"""
        # 设置全局主题色
        setThemeColor(color)
        
        # 保存到配置文件（如果配置管理器支持）
        try:
            self.config_manager.set_theme_color(color.name())
        except AttributeError:
            # 如果配置管理器不支持主题色配置，跳过
            pass
        
        # 显示成功消息
        if self.parent_window:
            MessageHelper.show_success(
                self.parent_window,
                f"自定义主题色已设置为 {color.name()}",
                2000
            )
    
    def _on_mica_effect_changed(self, enabled):
        """云母效果切换事件"""
        # 保存到配置文件（如果配置管理器支持）
        try:
            self.config_manager.set_mica_effect(enabled)
        except AttributeError:
            # 如果配置管理器不支持云母效果配置，跳过
            pass
        
        # 应用云母效果到主窗口
        if self.parent_window and hasattr(self.parent_window, 'setMicaEffectEnabled'):
            self.parent_window.setMicaEffectEnabled(enabled)
        
        # 只在非应用保存设置时显示消息
        if not self._is_applying_saved_settings:
            status = "已启用" if enabled else "已禁用"
            if self.parent_window:
                MessageHelper.show_success(
                    self.parent_window,
                    f"云母效果{status}",
                    2000
                )
    
    def _on_about_clicked(self):
        """关于按钮点击事件 - 跳转到GitHub"""
        webbrowser.open(get_repository())
    
    def apply_saved_theme(self):
        """应用保存的主题设置"""
        self._is_applying_saved_settings = True  # 设置标志
        
        try:
            # 应用主题模式
            theme_mode = self.config_manager.get_theme_mode()
            theme_map = {
                "light": Theme.LIGHT,
                "dark": Theme.DARK,
                "auto": Theme.AUTO
            }
            saved_theme = theme_map.get(theme_mode, Theme.AUTO)
            setTheme(saved_theme)
            
            # 应用主题色（如果配置管理器支持）
            try:
                theme_color = self.config_manager.get_theme_color()
                if theme_color:
                    from PyQt6.QtGui import QColor
                    setThemeColor(QColor(theme_color))
            except AttributeError:
                # 如果配置管理器不支持主题色配置，跳过
                pass
            
            # 应用云母效果（现在不会显示提示消息）
            try:
                mica_enabled = self.config_manager.get_mica_effect()
                # 先设置UI状态，再应用效果（这样会触发_on_mica_effect_changed但不显示消息）
                self.mica_card.setChecked(mica_enabled)
            except AttributeError:
                # 如果配置管理器不支持云母效果配置，跳过
                pass
                
        finally:
            self._is_applying_saved_settings = False  # 重置标志