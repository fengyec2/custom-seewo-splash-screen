"""设置界面"""

import webbrowser
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import (
    FluentIcon as FIF, SettingCardGroup, OptionsSettingCard, 
    SwitchSettingCard, PrimaryPushSettingCard, PushSettingCard,
    ExpandGroupSettingCard, qconfig, setTheme, Theme,
    TitleLabel, ScrollArea, ExpandLayout, setThemeColor
)

from core.config_manager import ConfigManager
from core.file_protector import FileProtector
from core.app_info import get_version, get_app_name, get_repository
from utils.system_theme import get_system_theme_color
from .dialogs import MessageHelper


class SettingsInterface(ScrollArea):
    """设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_window = parent
        self.config_manager = ConfigManager()
        self.file_protector = FileProtector()
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
        self.mica_card.checkedChanged.connect(self._on_mica_effect_changed)
        
        # 添加到设置组
        self.appearance_group.addSettingCard(self.theme_card)
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
        
        # 启动图保护设置 - 手风琴卡片
        self.protection_expand_card = ExpandGroupSettingCard(
            FIF.LIBRARY,
            "启动图保护",
            "保护已替换的启动图不被软件还原",
            parent=self.behavior_group
        )
        
        # 防止图片还原开关
        self.prevent_restore_card = SwitchSettingCard(
            FIF.REMOVE_FROM,
            "防止图片还原",
            "为替换的图片设置只读+系统+隐藏属性",
            parent=self.protection_expand_card
        )
        self.prevent_restore_card.setChecked(False)  # 默认关闭
        self.prevent_restore_card.checkedChanged.connect(self._on_prevent_restore_changed)
        
        # 立即移除所有保护按钮
        self.remove_all_protection_card = PushSettingCard(
            "立即移除",
            FIF.DELETE,
            "立即移除所有保护",
            "移除所有已经设置的文件保护属性",
            parent=self.protection_expand_card
        )
        self.remove_all_protection_card.clicked.connect(self._on_remove_all_protection)
        
        # 将子卡片添加到手风琴卡片中
        self.protection_expand_card.addGroupWidget(self.prevent_restore_card)
        self.protection_expand_card.addGroupWidget(self.remove_all_protection_card)
        
        # 将手风琴卡片添加到行为设置组
        self.behavior_group.addSettingCard(self.protection_expand_card)
    
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
        
        # 绑定文件保护设置
        protect_enabled = self.config_manager.get_file_protection_enabled()
        self.prevent_restore_card.setChecked(protect_enabled)
    
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
    
    def _on_prevent_restore_changed(self, enabled):
        """防止图片还原开关事件"""
        # 保存到配置文件
        self.config_manager.set_file_protection_enabled(enabled)
        
        # 显示成功消息（只在非应用保存设置时显示）
        if not self._is_applying_saved_settings:
            status = "已启用" if enabled else "已禁用"
            if self.parent_window:
                MessageHelper.show_success(
                    self.parent_window,
                    f"文件保护{status}",
                    2000
                )
    
    def _on_remove_all_protection(self):
        """移除所有保护按钮点击事件"""
        try:
            # 获取所有已保护的文件路径
            protected_files = self._get_all_protected_files()
            
            if not protected_files:
                MessageHelper.show_success(
                    self.parent_window,
                    "未发现受保护的文件",
                    2000
                )
                return
            
            # 逐个移除保护
            success_count = 0
            failed_count = 0
            
            for file_path in protected_files:
                success, msg = self.file_protector.unprotect_file(file_path)
                if success:
                    success_count += 1
                    try:
                        self.config_manager.remove_protected_file(file_path)
                    except Exception:
                        pass
                else:
                    failed_count += 1
            
            # 显示结果
            if success_count > 0 and failed_count == 0:
                MessageHelper.show_success(
                    self.parent_window,
                    f"成功移除 {success_count} 个文件的保护",
                    3000
                )
            elif success_count > 0:
                MessageHelper.show_warning(
                    self.parent_window,
                    f"成功移除 {success_count} 个文件的保护，{failed_count} 个失败",
                    3000
                )
            else:
                MessageHelper.show_error(
                    self.parent_window,
                    f"移除保护失败：所有 {len(protected_files)} 个文件都无法处理",
                    3000
                )
                
        except Exception as e:
            MessageHelper.show_error(
                self.parent_window,
                f"移除保护时出现错误: {str(e)}",
                3000
            )

    
    def _get_all_protected_files(self):
        """获取所有可能受保护的文件路径"""
        protected_files = []

        # 先从配置中读取已记录的受保护文件（兼容之前的实现）
        try:
            recorded = self.config_manager.get_protected_files()
            for p in recorded:
                if p and os.path.exists(p):
                    protected_files.append(p)
        except Exception:
            pass

        # 检查希沃白板路径（作为回退：检查常见文件名）
        seewo_path = self.config_manager.get_target_path("home")
        if seewo_path:
            splash_files = [
                "splash.png",
                "splash_screen.png", 
                "startup.png"
            ]
            for filename in splash_files:
                file_path = f"{seewo_path}\\{filename}"
                if os.path.exists(file_path) and self.file_protector.is_file_protected(file_path):
                    if file_path not in protected_files:
                        protected_files.append(file_path)
        
        # 检查WPS路径
        wps_path = self.config_manager.get_target_path("wps")
        if wps_path:
            splash_files = [
                "splash.png",
                "splash_screen.png",
                "startup.png"
            ]
            for filename in splash_files:
                file_path = f"{wps_path}\\{filename}"
                if os.path.exists(file_path) and self.file_protector.is_file_protected(file_path):
                    if file_path not in protected_files:
                        protected_files.append(file_path)
        
        return protected_files
    
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
            
            # 应用系统主题色
            system_color = get_system_theme_color()
            setThemeColor(system_color)
            
            # 应用云母效果（现在不会显示提示消息）
            try:
                mica_enabled = self.config_manager.get_mica_effect()
                # 先设置UI状态，再应用效果（这样会触发_on_mica_effect_changed但不显示消息）
                self.mica_card.setChecked(mica_enabled)
            except AttributeError:
                # 如果配置管理器不支持云母效果配置，跳过
                pass
            
            # 应用文件保护设置（不显示消息）
            protect_enabled = self.config_manager.get_file_protection_enabled()
            self.prevent_restore_card.setChecked(protect_enabled)
                
        finally:
            self._is_applying_saved_settings = False  # 重置标志