"""设置界面 - 仅负责UI展示和事件分发"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import TitleLabel, ScrollArea, ExpandLayout, qconfig

from core.app_info import get_version, get_app_name
from .widgets.settings_widgets import (
    AppearanceSettingsGroup,
    BehaviorSettingsGroup,
    AboutSettingsGroup
)
from .controllers.settings_controller import SettingsController


class SettingsInterface(ScrollArea):
    """设置界面 - 负责UI展示和事件分发"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_window = parent
        
        # 创建控制器
        self.controller = SettingsController(parent)
        
        # 创建滚动容器
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        # 初始化UI
        self._init_ui()
        self._create_setting_groups()
        self._init_layout()
        
        # 绑定事件
        self._bind_events()
        
        # 加载保存的设置
        self._load_saved_settings()
    
    def _init_ui(self):
        """初始化UI基础设置"""
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
    
    def _create_setting_groups(self):
        """创建设置组"""
        # 外观设置组
        self.appearance_group = AppearanceSettingsGroup(self.scrollWidget)
        
        # 行为设置组
        self.behavior_group = BehaviorSettingsGroup(self.scrollWidget)
        
        # 关于设置组
        self.about_group = AboutSettingsGroup(
            get_app_name(),
            get_version(),
            self.scrollWidget
        )
    
    def _init_layout(self):
        """初始化布局"""
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        
        # 添加设置组到布局
        self.expandLayout.addWidget(self.appearance_group)
        self.expandLayout.addWidget(self.behavior_group)
        self.expandLayout.addWidget(self.about_group)
    
    def _bind_events(self):
        """绑定所有事件到控制器"""
        # 主题相关事件
        qconfig.themeChanged.connect(lambda theme: self.controller.apply_saved_theme())
        self.appearance_group.theme_card.optionChanged.connect(
            self.controller.handle_theme_changed
        )
        
        # 云母效果事件
        self.appearance_group.mica_card.checkedChanged.connect(
            self.controller.handle_mica_effect_changed
        )
        
        # 自动检测事件
        self.behavior_group.auto_detect_card.checkedChanged.connect(
            self.controller.handle_auto_detect_changed
        )
        
        # 文件保护事件
        self.behavior_group.prevent_restore_card.checkedChanged.connect(
            self.controller.handle_file_protection_changed
        )
        self.behavior_group.remove_all_protection_card.clicked.connect(
            self.controller.handle_remove_all_protection
        )
        
        # 关于事件
        self.about_group.about_card.clicked.connect(
            self.controller.handle_about_clicked
        )
    
    def _load_saved_settings(self):
        """加载保存的设置到UI"""
        settings = self.controller.load_saved_settings()
        
        # 设置UI状态
        self.behavior_group.auto_detect_card.setChecked(settings['auto_detect'])
        self.appearance_group.mica_card.setChecked(settings['mica_enabled'])
        self.behavior_group.prevent_restore_card.setChecked(settings['file_protection'])
    
    def apply_saved_theme(self):
        """应用保存的主题设置（供主窗口调用）"""
        settings = self.controller.apply_all_saved_settings()
        
        # 更新UI状态（不触发事件）
        self.behavior_group.auto_detect_card.setChecked(settings['auto_detect'])
        self.appearance_group.mica_card.setChecked(settings['mica_enabled'])
        self.behavior_group.prevent_restore_card.setChecked(settings['file_protection'])