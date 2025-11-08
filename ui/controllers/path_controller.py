"""路径管理控制器 - 处理所有路径相关的业务逻辑"""

from PyQt6.QtWidgets import QWidget
from qfluentwidgets import MessageBoxBase, SubtitleLabel, ComboBox, BodyLabel
from core.config_manager import ConfigManager
from utils.path_detector import PathDetector
import os

class TargetPathSelectionDialog(MessageBoxBase):
    """目标路径选择对话框"""
    
    def __init__(self, paths: list[str], parent=None):
        super().__init__(parent)
        self.paths = paths
        
        self.titleLabel = SubtitleLabel('选择目标路径')
        self.infoLabel = BodyLabel(
            f'检测到 {len(paths)} 个可能的启动图片路径\n'
            '请选择要使用的路径：'
        )
        self.pathComboBox = ComboBox()
        
        # 添加路径选项
        for i, path in enumerate(paths):
            display_text = f"{i+1}. {path}"
            self.pathComboBox.addItem(display_text, userData=path)
        
        # 默认选中第一个路径
        self.pathComboBox.setCurrentIndex(0)
        
        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.infoLabel)
        self.viewLayout.addWidget(self.pathComboBox)
        
        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(500)
    
    def get_selected_path(self) -> str:
        """获取选择的路径"""
        return self.pathComboBox.currentData()


class PathController:
    """路径管理控制器"""
    
    def __init__(self, parent: QWidget, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.target_path = ""
    
    def load_and_validate_target_path(self) -> tuple[bool, str]:
        """加载并验证目标路径（静默模式）
        
        Returns:
            (成功标志, 提示消息)
        """
        # 先尝试加载上次保存的路径
        saved_path = self.config_manager.get_target_path()
        
        if saved_path:
            is_valid, error_msg = PathDetector.validate_target_path(saved_path)
            if is_valid:
                self.target_path = saved_path
                return True, f"已加载上次使用的路径: {os.path.basename(saved_path)}"
        
        # 尝试从历史记录中查找有效路径
        history = self.config_manager.get_path_history()
        for historical_path in history:
            is_valid, _ = PathDetector.validate_target_path(historical_path)
            if is_valid:
                self.target_path = historical_path
                self.config_manager.set_target_path(historical_path)
                return True, f"已从历史记录恢复路径: {os.path.basename(historical_path)}"
        
        # 清理无效的历史记录
        self.config_manager.clear_invalid_history()
        
        # 如果启用了自动检测
        if self.config_manager.get_auto_detect_on_startup():
            return self._silent_detect()
        
        return False, ""
    
    def _silent_detect(self) -> tuple[bool, str]:
        """静默检测目标路径"""
        paths = PathDetector.detect_all_paths()
        
        if paths:
            self.target_path = paths[0]
            self.config_manager.set_target_path(self.target_path)
            return True, f"检测成功: {os.path.basename(self.target_path)}"
        
        return False, ""
    
    def detect_with_user_interaction(self) -> tuple[bool, str]:
        """检测目标路径（用户主动触发，可能需要用户选择）
        
        Returns:
            (成功标志, 提示消息)
        """
        paths = PathDetector.detect_all_paths()
        
        if not paths:
            # 手动选择
            self.target_path = PathDetector.manual_select_target_image(self.parent)
            if self.target_path:
                is_valid, error_msg = PathDetector.validate_target_path(self.target_path)
                if is_valid:
                    self.config_manager.set_target_path(self.target_path)
                    return True, f"路径设置成功: {os.path.basename(self.target_path)}"
                else:
                    return False, f"选择的路径无效:\n{error_msg}"
            return False, ""
        
        # 多个路径让用户选择
        if len(paths) > 1:
            dialog = TargetPathSelectionDialog(paths, self.parent)
            
            if dialog.exec():
                self.target_path = dialog.get_selected_path()
            else:
                return False, ""
        else:
            self.target_path = paths[0]
        
        self.config_manager.set_target_path(self.target_path)
        return True, f"检测成功: {os.path.basename(self.target_path)}"
    
    def select_from_history(self) -> tuple[bool, str, bool]:
        """从历史记录选择路径
        
        Returns:
            (成功标志, 路径或消息, 是否需要重新检测)
        """
        from ui.dialogs import PathHistoryDialog
        
        selected_path, success = PathHistoryDialog.show_and_select(
            self.parent,
            self.config_manager
        )
        
        if success and selected_path:
            self.target_path = selected_path
            self.config_manager.set_target_path(selected_path)
            return True, selected_path, False
        elif success and not selected_path:
            # 用户选择了重新检测
            return False, "", True
        
        return False, "", False
