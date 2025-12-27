import os
from PyQt5.QtWidgets import QHBoxLayout
from qfluentwidgets import CardWidget, StrongBodyLabel, PushButton, FluentIcon as FIF, ToolTipFilter, ToolTipPosition


class PathInfoCard(CardWidget):
    """路径信息卡片组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        
        # 路径标签
        self.path_label = StrongBodyLabel()
        self.path_label.setWordWrap(True)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.detect_button = PushButton(FIF.SEARCH, "检测路径")
        self.history_button = PushButton(FIF.HISTORY, "历史路径")
        
        # 设置按钮工具提示 - 使用官方最佳实践
        self._setup_button_tooltips()
        
        button_layout.addWidget(self.detect_button)
        button_layout.addWidget(self.history_button)
        
        layout.addWidget(self.path_label, 1)
        layout.addLayout(button_layout)
    
    def _setup_button_tooltips(self):
        """设置按钮工具提示 - 按照官方最佳实践"""
        # 检测按钮工具提示
        self.detect_button.setToolTip("自动检测希沃白板启动图片路径")
        detect_tooltip_filter = ToolTipFilter(self.detect_button, 500, ToolTipPosition.TOP)
        self.detect_button.installEventFilter(detect_tooltip_filter)
        
        # 历史按钮工具提示
        self.history_button.setToolTip("查看和选择历史路径")
        history_tooltip_filter = ToolTipFilter(self.history_button, 500, ToolTipPosition.TOP)
        self.history_button.installEventFilter(history_tooltip_filter)
    
    def _setup_path_label_tooltip(self, tooltip_text: str, position: ToolTipPosition = ToolTipPosition.BOTTOM):
        """设置路径标签的工具提示
        
        Args:
            tooltip_text: 工具提示文本
            position: 显示位置，默认在底部
        """
        # 移除之前的事件过滤器（如果存在）
        if hasattr(self, '_path_tooltip_filter'):
            self.path_label.removeEventFilter(self._path_tooltip_filter)
        
        # 设置新的工具提示
        self.path_label.setToolTip(tooltip_text)
        self._path_tooltip_filter = ToolTipFilter(self.path_label, 300, position)
        self.path_label.installEventFilter(self._path_tooltip_filter)
        
        # 设置较长的显示时间，因为路径信息可能较长
        self.path_label.setToolTipDuration(5000)  # 5秒后自动消失
    
    def update_path_display(self, path: str, file_count: int = None):
        """更新路径显示
        
        Args:
            path: 目标路径,空字符串表示未设置路径
            file_count: 可选的文件数量（用于WPS页面显示）
        """
        if path:
            # 缩短路径显示
            path_parts = path.split(os.sep)
            if len(path_parts) > 3:
                short_path = "..." + os.sep + os.sep.join(path_parts[-3:])
            else:
                short_path = path
            
            # 如果有文件数量信息，显示更详细的信息
            if file_count is not None:
                self.path_label.setText(f"✓ 当前路径: {short_path} ({file_count}个文件)")
            else:
                self.path_label.setText(f"✓ 当前路径: {short_path}")
            
            # 设置完整路径的工具提示
            if file_count is not None:
                full_path_tooltip = f"完整路径:\n{path}\n\n包含 {file_count} 个启动图文件"
            else:
                full_path_tooltip = f"完整路径:\n{path}"
            self._setup_path_label_tooltip(full_path_tooltip, ToolTipPosition.BOTTOM)
            
        else:
            self.path_label.setText("⚠ 未检测到启动图片路径 (点击右侧按钮进行检测)")
            
            # 设置提示信息的工具提示
            help_tooltip = "请点击'检测路径'或'历史路径'按��来设置启动图片路径"
            self._setup_path_label_tooltip(help_tooltip, ToolTipPosition.BOTTOM)
