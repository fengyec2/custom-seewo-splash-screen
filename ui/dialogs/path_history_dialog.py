import os

from qfluentwidgets import MessageBox, MessageBoxBase, SubtitleLabel, ComboBox, BodyLabel
from utils.path_detector import PathDetector


def _history_path_valid(path: str, page: str) -> tuple[bool, str]:
    """校验历史记录项：希沃为 PNG 文件路径，WPS 为 splash 目录路径。"""
    if page == "wps":
        if not path or not os.path.isdir(path):
            return False, "目录不存在或不是文件夹"
        if not PathDetector._validate_wps_splash_dir(path):
            return False, "不是有效的 WPS splash 目录"
        return True, ""
    return PathDetector.validate_target_path(path)


class PathSelectionDialog(MessageBoxBase):
    """历史路径选择对话框"""
    
    def __init__(self, history: list[str], valid_paths: list[str], parent=None, page: str = "home"):
        super().__init__(parent)
        self.history = history
        self.valid_paths = valid_paths
        self.page = page
        
        self.titleLabel = SubtitleLabel('选择历史路径')
        self.infoLabel = BodyLabel(
            f'共有 {len(history)} 条历史记录，其中 {len(valid_paths)} 条有效\n'
            '请选择要使用的路径：'
        )
        self.pathComboBox = ComboBox()
        
        # 添加路径选项
        for i, path in enumerate(history):
            is_valid, error_msg = _history_path_valid(path, page)
            status = "✓ 有效" if is_valid else f"✗ 无效 ({error_msg})"
            display_text = f"{i+1}. [{status}] {path}"
            self.pathComboBox.addItem(display_text, userData=path)
        
        # 默认选中第一个有效路径
        if valid_paths:
            first_valid_index = next(i for i, p in enumerate(history) if p in valid_paths)
            self.pathComboBox.setCurrentIndex(first_valid_index)
        
        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.infoLabel)
        self.viewLayout.addWidget(self.pathComboBox)
        
        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(500)
    
    def validate(self):
        """验证选择的路径是否有效"""
        selected_path = self.pathComboBox.currentData()
        is_valid, error_msg = _history_path_valid(selected_path, self.page)
        
        if not is_valid:
            w = MessageBox(
                "路径无效",
                f"选择的路径已失效：\n{error_msg}\n\n请选择其他路径或重新检测。",
                self.parent()
            )
            w.exec()
            return False
        
        return True
    
    def get_selected_path(self) -> str:
        """获取选择的路径"""
        return self.pathComboBox.currentData()


class PathHistoryDialog:
    """历史路径对话框辅助类"""
    
    @staticmethod
    def show_and_select(parent, config_manager, page="home") -> tuple[str, bool]:
        """显示历史路径对话框并选择路径
        
        Args:
            parent: 父窗口
            config_manager: 配置管理器实例
            page: 页面标识，"home" 或 "wps"
            
        Returns:
            tuple: (选择的路径, 是否成功选择)
        """
        history = config_manager.get_path_history(page)
        
        if not history:
            w = MessageBox(
                "无历史记录",
                "暂无历史路径记录。\n\n请点击'检测路径'按钮检测启动图片路径。",
                parent
            )
            w.exec()
            return "", False
        
        # 验证历史路径（WPS 为目录，希沃为 PNG 文件）
        valid_paths = []
        for path in history:
            is_valid, _ = _history_path_valid(path, page)
            if is_valid:
                valid_paths.append(path)
        
        if not valid_paths:
            w = MessageBox(
                "所有历史路径均无效",
                "历史记录中的所有路径都已失效。\n\n是否清理历史记录并重新检测?",
                parent
            )
            
            if w.exec():
                config_manager.clear_invalid_history(page)
            
            return "", False
        
        # 显示路径选择对话框
        dialog = PathSelectionDialog(history, valid_paths, parent, page)
        
        if dialog.exec():
            selected_path = dialog.get_selected_path()
            return selected_path, True
        
        return "", False
