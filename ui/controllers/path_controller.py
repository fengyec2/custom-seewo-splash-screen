"""路径管理控制器 - 处理所有路径相关的业务逻辑"""

from PyQt5.QtWidgets import QWidget
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
    
    def __init__(self, parent: QWidget, config_manager: ConfigManager, page="home"):
        self.parent = parent
        self.config_manager = config_manager
        self.page = page  # "home" 或 "wps"
        self.target_path = ""  # 对于WPS，这是splash目录路径；对于希沃，这是单个文件路径
    
    def get_target_paths(self):
        """获取目标路径列表
        
        对于WPS页面，返回所有需要替换的文件路径列表
        对于希沃页面，返回单个文件路径的列表
        
        Returns:
            list: 目标文件路径列表
        """
        if self.page == "wps":
            # WPS页面：target_path是splash目录，需要获取所有文件
            if self.target_path and os.path.isdir(self.target_path):
                return PathDetector.get_wps_splash_files(self.target_path)
            return []
        else:
            # 希沃页面：target_path是单个文件
            if self.target_path and os.path.isfile(self.target_path):
                return [self.target_path]
            return []
    
    def load_and_validate_target_path(self) -> tuple[bool, str]:
        """加载并验证目标路径（静默模式）
        
        Returns:
            (成功标志, 提示消息)
        """
        # 先尝试加载上次保存的路径
        saved_path = self.config_manager.get_target_path(self.page)
        
        if saved_path:
            if self.page == "wps":
                # WPS页面：验证splash目录
                if os.path.isdir(saved_path) and PathDetector._validate_wps_splash_dir(saved_path):
                    self.target_path = saved_path
                    file_count = len(PathDetector.get_wps_splash_files(saved_path))
                    return True, f"已加载WPS启动图目录 ({file_count}个文件)"
            else:
                # 希沃页面：验证单个文件
                is_valid, error_msg = PathDetector.validate_target_path(saved_path)
                if is_valid:
                    self.target_path = saved_path
                    return True, f"已加载上次使用的路径: {os.path.basename(saved_path)}"
        
        # 尝试从历史记录中查找有效路径
        history = self.config_manager.get_path_history(self.page)
        for historical_path in history:
            if self.page == "wps":
                if os.path.isdir(historical_path) and PathDetector._validate_wps_splash_dir(historical_path):
                    self.target_path = historical_path
                    self.config_manager.set_target_path(historical_path, self.page)
                    file_count = len(PathDetector.get_wps_splash_files(historical_path))
                    return True, f"已从历史记录恢复WPS启动图目录 ({file_count}个文件)"
            else:
                is_valid, _ = PathDetector.validate_target_path(historical_path)
                if is_valid:
                    self.target_path = historical_path
                    self.config_manager.set_target_path(historical_path, self.page)
                    return True, f"已从历史记录恢复路径: {os.path.basename(historical_path)}"
        
        # 清理无效的历史记录
        self.config_manager.clear_invalid_history(self.page)
        
        # 如果启用了自动检测
        if self.config_manager.get_auto_detect_on_startup():
            return self._silent_detect()
        
        return False, ""
    
    def _silent_detect(self) -> tuple[bool, str]:
        """静默检测目标路径"""
        if self.page == "wps":
            paths = PathDetector.detect_wps_paths()
            if paths:
                self.target_path = paths[0]  # splash目录路径
                self.config_manager.set_target_path(self.target_path, self.page)
                file_count = len(PathDetector.get_wps_splash_files(self.target_path))
                return True, f"检测到WPS启动图目录 ({file_count}个文件)"
        else:
            paths = PathDetector.detect_all_paths()
            if paths:
                self.target_path = paths[0]
                self.config_manager.set_target_path(self.target_path, self.page)
                return True, f"检测成功: {os.path.basename(self.target_path)}"
        
        return False, ""
    
    def detect_with_user_interaction(self) -> tuple[bool, str]:
        """检测目标路径（用户主动触发，可能需要用户选择）
        
        Returns:
            (成功标志, 提示消息)
        """
        if self.page == "wps":
            paths = PathDetector.detect_wps_paths()
            app_type = "wps"
        else:
            paths = PathDetector.detect_all_paths()
            app_type = "seewo"
        
        if not paths:
            # 手动选择
            if self.page == "wps":
                # WPS页面：手动选择splash目录
                from PyQt5.QtWidgets import QFileDialog
                dialog = QFileDialog(self.parent, "选择WPS splash目录")
                dialog.setFileMode(QFileDialog.FileMode.Directory)
                
                # 优先检查用户目录
                initial_dir = None
                userprofile = os.environ.get("USERPROFILE", "")
                if userprofile:
                    wps_user_path = os.path.join(userprofile, "AppData", "Local", "Kingsoft", "WPS Office")
                    if os.path.exists(wps_user_path):
                        initial_dir = wps_user_path
                
                # 如果用户目录不存在，尝试Program Files
                if not initial_dir:
                    possible_paths = [
                        "C:\\Program Files\\Kingsoft\\WPS Office",
                        "C:\\Program Files (x86)\\Kingsoft\\WPS Office",
                        "D:\\Program Files\\Kingsoft\\WPS Office",
                        "D:\\Program Files (x86)\\Kingsoft\\WPS Office",
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            initial_dir = path
                            break
                
                # 如果都不存在，使用用户目录或C盘根目录
                if not initial_dir:
                    initial_dir = userprofile if userprofile else "C:\\"
                
                dialog.setDirectory(initial_dir)
                
                if dialog.exec():
                    selected_dirs = dialog.selectedFiles()
                    if selected_dirs:
                        selected_dir = selected_dirs[0]
                        if PathDetector._validate_wps_splash_dir(selected_dir):
                            self.target_path = selected_dir
                            self.config_manager.set_target_path(self.target_path, self.page)
                            file_count = len(PathDetector.get_wps_splash_files(self.target_path))
                            return True, f"路径设置成功: WPS启动图目录 ({file_count}个文件)"
                        else:
                            return False, "选择的目录不是有效的WPS splash目录\n请选择包含启动图文件的splash目录"
                return False, ""
            else:
                # 希沃页面：手动选择文件
                self.target_path = PathDetector.manual_select_target_image(self.parent, app_type)
                if self.target_path:
                    is_valid, error_msg = PathDetector.validate_target_path(self.target_path)
                    if is_valid:
                        self.config_manager.set_target_path(self.target_path, self.page)
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
        
        self.config_manager.set_target_path(self.target_path, self.page)
        if self.page == "wps":
            file_count = len(PathDetector.get_wps_splash_files(self.target_path))
            return True, f"检测成功: WPS启动图目录 ({file_count}个文件)"
        else:
            return True, f"检测成功: {os.path.basename(self.target_path)}"
    
    def select_from_history(self) -> tuple[bool, str, bool]:
        """从历史记录选择路径
        
        Returns:
            (成功标志, 路径或消息, 是否需要重新检测)
        """
        from ui.dialogs import PathHistoryDialog
        
        selected_path, success = PathHistoryDialog.show_and_select(
            self.parent,
            self.config_manager,
            self.page
        )
        
        if success and selected_path:
            self.target_path = selected_path
            self.config_manager.set_target_path(selected_path, self.page)
            return True, selected_path, False
        elif success and not selected_path:
            # 用户选择了重新检测
            return False, "", True
        
        return False, "", False
