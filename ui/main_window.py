"""主窗口 - 只负责UI组装和事件分发"""

import os
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from qfluentwidgets import FluentWindow, FluentIcon as FIF, IndeterminateProgressBar, NavigationItemPosition

from core.config_manager import ConfigManager
from core.image_manager import ImageManager
from core.replacer import ImageReplacer
from utils.admin_helper import is_admin

from .widgets import PathInfoCard, ImageListWidget, ActionBar
from .dialogs import MessageHelper
from .controllers import PathController, ImageController, PermissionController
from .settings import SettingsInterface


class MainWindow(FluentWindow):
    """主窗口 - 只负责UI和事件分发"""
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_managers()
        self._init_controllers()
        self._init_ui()
        self._init_settings_interface()
        self._connect_signals()
        
        # 应用保存的主题设置
        self.settings_interface.apply_saved_theme()
        
        self.show()
        
        # 延迟加载数据
        QTimer.singleShot(100, self._load_initial_data)
        QTimer.singleShot(200, self._check_admin_status)
    
    def _init_window(self):
        """初始化窗口属性"""
        from utils.resource_path import get_resource_path  # 确保导入路径处理模块

        self.setWindowTitle("SeewoSplash")
        self.setWindowIcon(QIcon(get_resource_path("assets/icon.ico")))
        self.resize(900, 650)
        self.center_window()
    
    def _init_managers(self):
        """初始化管理器"""
        self.config_manager = ConfigManager()
        self.image_manager = ImageManager()
        self.replacer = ImageReplacer()
    
    def _init_controllers(self):
        """初始化控制器"""
        # 主页控制器
        self.path_ctrl = PathController(self, self.config_manager, "home")
        self.image_ctrl = ImageController(self, self.config_manager, self.image_manager)
        self.permission_ctrl = PermissionController()
        
        # WPS页面控制器
        self.wps_path_ctrl = PathController(self, self.config_manager, "wps")
        self.wps_image_ctrl = ImageController(self, self.config_manager, self.image_manager)
    
    def _init_ui(self):
        """初始化主界面UI"""
        # 主页
        self.homeInterface = QWidget()
        self.homeInterface.setObjectName("homeInterface")
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页')
        
        layout = QVBoxLayout(self.homeInterface)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        self.path_card = PathInfoCard(self.homeInterface)
        self.image_list = ImageListWidget(self.homeInterface)
        self.action_bar = ActionBar(self.homeInterface)
        self.progress_bar = IndeterminateProgressBar(self.homeInterface)
        self.progress_bar.setVisible(False)
        
        layout.addWidget(self.path_card)
        layout.addWidget(self.image_list, 1)
        layout.addWidget(self.action_bar)
        layout.addWidget(self.progress_bar)
        
        # WPS页面
        self.wpsInterface = QWidget()
        self.wpsInterface.setObjectName("wpsInterface")
        self.addSubInterface(self.wpsInterface, FIF.DOCUMENT, 'WPS')
        
        wps_layout = QVBoxLayout(self.wpsInterface)
        wps_layout.setContentsMargins(20, 20, 20, 20)
        wps_layout.setSpacing(15)
        
        self.wps_path_card = PathInfoCard(self.wpsInterface)
        self.wps_image_list = ImageListWidget(self.wpsInterface)
        self.wps_action_bar = ActionBar(self.wpsInterface)
        self.wps_progress_bar = IndeterminateProgressBar(self.wpsInterface)
        self.wps_progress_bar.setVisible(False)
        
        wps_layout.addWidget(self.wps_path_card)
        wps_layout.addWidget(self.wps_image_list, 1)
        wps_layout.addWidget(self.wps_action_bar)
        wps_layout.addWidget(self.wps_progress_bar)
    
    def _init_settings_interface(self):
        """初始化设置界面"""
        self.settings_interface = SettingsInterface(self)
        
        # 添加到导航栏底部
        self.addSubInterface(
            self.settings_interface,
            FIF.SETTING,
            '设置',
            position=NavigationItemPosition.BOTTOM
        )

    def _connect_signals(self):
        """连接信号槽"""
        # 主页信号
        self.path_card.detect_button.clicked.connect(self._on_detect_path)
        self.path_card.history_button.clicked.connect(self._on_show_history)
        self.image_list.imageSelected.connect(self._on_image_selected)
        self.image_list.imagesDropped.connect(self._on_images_dropped)
        self.action_bar.importClicked.connect(self._on_import_image)
        self.action_bar.renameClicked.connect(self._on_rename_image)
        self.action_bar.deleteClicked.connect(self._on_delete_image)
        self.action_bar.replaceClicked.connect(self._on_replace_image)
        self.action_bar.restoreClicked.connect(self._on_restore_backup)
        
        # WPS页面信号
        self.wps_path_card.detect_button.clicked.connect(self._on_wps_detect_path)
        self.wps_path_card.history_button.clicked.connect(self._on_wps_show_history)
        self.wps_image_list.imageSelected.connect(self._on_wps_image_selected)
        self.wps_image_list.imagesDropped.connect(self._on_wps_images_dropped)
        self.wps_action_bar.importClicked.connect(self._on_wps_import_image)
        self.wps_action_bar.renameClicked.connect(self._on_wps_rename_image)
        self.wps_action_bar.deleteClicked.connect(self._on_wps_delete_image)
        self.wps_action_bar.replaceClicked.connect(self._on_wps_replace_image)
        self.wps_action_bar.restoreClicked.connect(self._on_wps_restore_backup)
    
    def _load_initial_data(self):
        """加载初始数据"""
        # 加载主页数据
        self.load_images()
        success, message = self.path_ctrl.load_and_validate_target_path()
        if success:
            self.path_card.update_path_display(self.path_ctrl.target_path)
            MessageHelper.show_success(self, message, 3000)
        else:
            self.path_card.update_path_display("")
        
        # 加载WPS页面数据
        self.load_wps_images()
        wps_success, wps_message = self.wps_path_ctrl.load_and_validate_target_path()
        if wps_success:
            self.wps_path_card.update_path_display(self.wps_path_ctrl.target_path)
            MessageHelper.show_success(self, wps_message, 3000)
        else:
            self.wps_path_card.update_path_display("")
    
    def _check_admin_status(self):
        """检查管理员权限状态"""
        if is_admin():
            current_title = self.windowTitle()
            self.setWindowTitle(f"{current_title} [管理员]")
    
    # === 事件处理方法 (简洁的分发逻辑) ===
    
    def _on_image_selected(self, image_info: dict):
        """图片选中事件"""
        self.config_manager.set_last_selected_image(image_info["filename"], "home")
        is_custom = image_info["type"] == "custom"
        self.action_bar.set_rename_delete_enabled(is_custom)
    
    def _on_wps_image_selected(self, image_info: dict):
        """WPS页面图片选中事件"""
        self.config_manager.set_last_selected_image(image_info["filename"], "wps")
        is_custom = image_info["type"] == "custom"
        self.wps_action_bar.set_rename_delete_enabled(is_custom)
    
    def _on_images_dropped(self, drop_data):
        """图片拖放事件"""
        file_paths, ignored_files = drop_data
        
        if ignored_files:
            ignored_str = "、".join(ignored_files[:3])
            if len(ignored_files) > 3:
                ignored_str += f" 等{len(ignored_files)}个文件"
            MessageHelper.show_warning(
                self, "文件格式错误",
                f"以下文件不是PNG格式，已忽略：\n{ignored_str}"
            )
        
        if not file_paths:
            return
        
        self.show_progress(f"正在导入 {len(file_paths)} 个文件...")
        success_count, failed_files = self.image_ctrl.import_multiple_images(file_paths)
        self.hide_progress()
        
        if success_count > 0:
            MessageHelper.show_success(
                self,
                f"成功导入 {success_count} 个图片" + 
                (f"，{len(failed_files)} 个失败" if failed_files else ""),
                3000
            )
            self.load_images()
        
        if failed_files:
            error_details = "\n".join([f"• {name}: {msg}" for name, msg in failed_files[:5]])
            if len(failed_files) > 5:
                error_details += f"\n... 还有 {len(failed_files) - 5} 个文件失败"
            MessageHelper.show_error(self, "部分文件导入失败", error_details)
    
    def _on_detect_path(self):
        """检测路径事件"""
        self.show_progress("正在检测路径...")
        success, message = self.path_ctrl.detect_with_user_interaction()
        self.hide_progress()
        
        self.path_card.update_path_display(self.path_ctrl.target_path)
        if success:
            MessageHelper.show_success(self, message, 5000)
        elif message:
            MessageHelper.show_error(self, "检测失败", message)
    
    def _on_show_history(self):
        """显示历史路径事件"""
        success, result, need_detect = self.path_ctrl.select_from_history()
        if success:
            self.path_card.update_path_display(result)
            MessageHelper.show_success(self, f"已设置目标路径: {os.path.basename(result)}", 5000)
        elif need_detect:
            self._on_detect_path()
    
    def _on_import_image(self):
        """导入图片事件"""
        self.show_progress("正在导入...")
        success, msg, source_path = self.image_ctrl.import_single_image(allow_multiple=True)
        self.hide_progress()
        
        if success:
            MessageHelper.show_success(self, f"图片导入成功: {os.path.basename(source_path)}", 3000)
            self.load_images()
        elif msg:
            MessageHelper.show_error(self, "导入失败", msg)
    
    def _on_rename_image(self):
        """重命名图片事件"""
        image_info = self.image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要重命名的图片")
            return
        
        success, msg = self.image_ctrl.rename_image(image_info)
        if success:
            MessageHelper.show_success(self, msg, 2000)
            self.load_images()
        elif msg:
            MessageHelper.show_warning(self, "重命名失败", msg)
    
    def _on_delete_image(self):
        """删除图片事件"""
        image_info = self.image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要删除的图片")
            return
        
        success, msg = self.image_ctrl.delete_image(image_info)
        if success:
            MessageHelper.show_success(self, msg, 2000)
            self.load_images()
        else:
            MessageHelper.show_error(self, "删除失败", msg)
    
    def _on_replace_image(self):
        """替换启动图片事件"""
        if not self.path_ctrl.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return
        
        image_info = self.image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先从列表中选择要替换的图片")
            return
        
        self.show_progress("正在替换...")
        success, msg, is_permission_error = self.replacer.replace_image(
            image_info["path"],
            self.path_ctrl.target_path
        )
        self.hide_progress()
        
        if success:
            MessageHelper.show_success(self, f"启动图片已替换为: {image_info['display_name']}", 3000)
        elif is_permission_error:
            self.permission_ctrl.handle_permission_error(self, msg)
        else:
            MessageHelper.show_error(self, "替换失败", msg)
    
    def _on_restore_backup(self):
        """从备份还原事件"""
        if not self.path_ctrl.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return
        
        self.show_progress("正在还原...")
        success, msg, is_permission_error = self.replacer.restore_backup(self.path_ctrl.target_path)
        self.hide_progress()
        
        if success:
            MessageHelper.show_success(self, "已从备份还原启动图片", 3000)
        elif is_permission_error:
            self.permission_ctrl.handle_permission_error(self, msg)
        else:
            MessageHelper.show_error(self, "还原失败", msg)
    
    # === WPS页面事件处理方法 ===
    
    def _on_wps_images_dropped(self, drop_data):
        """WPS页面图片拖放事件"""
        file_paths, ignored_files = drop_data
        
        if ignored_files:
            ignored_str = "、".join(ignored_files[:3])
            if len(ignored_files) > 3:
                ignored_str += f" 等{len(ignored_files)}个文件"
            MessageHelper.show_warning(
                self, "文件格式错误",
                f"以下文件不是PNG格式，已忽略：\n{ignored_str}"
            )
        
        if not file_paths:
            return
        
        self.show_progress(f"正在导入 {len(file_paths)} 个文件...", "wps")
        success_count, failed_files = self.wps_image_ctrl.import_multiple_images(file_paths)
        self.hide_progress("wps")
        
        if success_count > 0:
            MessageHelper.show_success(
                self,
                f"成功导入 {success_count} 个图片" + 
                (f"，{len(failed_files)} 个失败" if failed_files else ""),
                3000
            )
            self.load_wps_images()
        
        if failed_files:
            error_details = "\n".join([f"• {name}: {msg}" for name, msg in failed_files[:5]])
            if len(failed_files) > 5:
                error_details += f"\n... 还有 {len(failed_files) - 5} 个文件失败"
            MessageHelper.show_error(self, "部分文件导入失败", error_details)
    
    def _on_wps_detect_path(self):
        """WPS页面检测路径事件"""
        self.show_progress("正在检测路径...", "wps")
        success, message = self.wps_path_ctrl.detect_with_user_interaction()
        self.hide_progress("wps")
        
        self.wps_path_card.update_path_display(self.wps_path_ctrl.target_path)
        if success:
            MessageHelper.show_success(self, message, 5000)
        elif message:
            MessageHelper.show_error(self, "检测失败", message)
    
    def _on_wps_show_history(self):
        """WPS页面显示历史路径事件"""
        success, result, need_detect = self.wps_path_ctrl.select_from_history()
        if success:
            self.wps_path_card.update_path_display(result)
            MessageHelper.show_success(self, f"已设置目标路径: {os.path.basename(result)}", 5000)
        elif need_detect:
            self._on_wps_detect_path()
    
    def _on_wps_import_image(self):
        """WPS页面导入图片事件"""
        self.show_progress("正在导入...", "wps")
        success, msg, source_path = self.wps_image_ctrl.import_single_image(allow_multiple=True)
        self.hide_progress("wps")
        
        if success:
            MessageHelper.show_success(self, f"图片导入成功: {os.path.basename(source_path)}", 3000)
            self.load_wps_images()
        elif msg:
            MessageHelper.show_error(self, "导入失败", msg)
    
    def _on_wps_rename_image(self):
        """WPS页面重命名图片事件"""
        image_info = self.wps_image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要重命名的图片")
            return
        
        success, msg = self.wps_image_ctrl.rename_image(image_info)
        if success:
            MessageHelper.show_success(self, msg, 2000)
            self.load_wps_images()
        elif msg:
            MessageHelper.show_warning(self, "重命名失败", msg)
    
    def _on_wps_delete_image(self):
        """WPS页面删除图片事件"""
        image_info = self.wps_image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要删除的图片")
            return
        
        success, msg = self.wps_image_ctrl.delete_image(image_info)
        if success:
            MessageHelper.show_success(self, msg, 2000)
            self.load_wps_images()
        else:
            MessageHelper.show_error(self, "删除失败", msg)
    
    def _on_wps_replace_image(self):
        """WPS页面替换启动图片事件"""
        if not self.wps_path_ctrl.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return
        
        image_info = self.wps_image_list.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先从列表中选择要替换的图片")
            return
        
        self.show_progress("正在替换...", "wps")
        success, msg, is_permission_error = self.replacer.replace_image(
            image_info["path"],
            self.wps_path_ctrl.target_path
        )
        self.hide_progress("wps")
        
        if success:
            MessageHelper.show_success(self, f"启动图片已替换为: {image_info['display_name']}", 3000)
        elif is_permission_error:
            self.permission_ctrl.handle_permission_error(self, msg)
        else:
            MessageHelper.show_error(self, "替换失败", msg)
    
    def _on_wps_restore_backup(self):
        """WPS页面从备份还原事件"""
        if not self.wps_path_ctrl.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return
        
        self.show_progress("正在还原...", "wps")
        success, msg, is_permission_error = self.replacer.restore_backup(self.wps_path_ctrl.target_path)
        self.hide_progress("wps")
        
        if success:
            MessageHelper.show_success(self, "已从备份还原启动图片", 3000)
        elif is_permission_error:
            self.permission_ctrl.handle_permission_error(self, msg)
        else:
            MessageHelper.show_error(self, "还原失败", msg)
    
    # === 辅助方法 ===
    
    def show_progress(self, message: str, page="home"):
        """显示进度"""
        if page == "wps":
            self.wps_progress_bar.setVisible(True)
            self.wps_progress_bar.start()
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.start()
        MessageHelper.show_success(self, message, 2000)

    def hide_progress(self, page="home"):
        """隐藏进度"""
        if page == "wps":
            self.wps_progress_bar.stop()
            self.wps_progress_bar.setVisible(False)
        else:
            self.progress_bar.stop()
            self.progress_bar.setVisible(False)
    
    def load_images(self):
        """加载图片列表"""
        preset_images = self.image_manager.get_preset_images("home")
        custom_images = self.image_manager.get_custom_images()
        self.image_list.load_images(preset_images, custom_images)
        
        last_selected = self.config_manager.get_last_selected_image("home")
        if last_selected:
            self.image_list.select_image_by_filename(last_selected)
    
    def load_wps_images(self):
        """加载WPS页面图片列表"""
        preset_images = self.image_manager.get_preset_images("wps")
        custom_images = self.image_manager.get_custom_images()
        self.wps_image_list.load_images(preset_images, custom_images)
        
        last_selected = self.config_manager.get_last_selected_image("wps")
        if last_selected:
            self.wps_image_list.select_image_by_filename(last_selected)

    def center_window(self):
        """将窗口移动到屏幕中心"""
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())
