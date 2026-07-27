"""主窗口 - 只负责UI组装和事件分发"""

import os
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, QSize
from qfluentwidgets import FluentWindow, FluentIcon as FIF, IndeterminateProgressBar, NavigationItemPosition, SystemThemeListener, SplashScreen

from core.config_manager import ConfigManager
from core.image_manager import ImageManager
from core.replacer import ImageReplacer
from utils.admin_helper import is_admin

from .widgets import PathInfoCard, ImageListWidget, ActionBar
from .dialogs import MessageHelper
from .controllers import PathController, ImageController, PermissionController
from .settings import SettingsInterface, apply_saved_appearance_from_config


# 页面配置：[icon, label, page_key]
PAGES = [
    {"icon": FIF.HOME, "label": "希沃白板", "key": "home"},
    {"icon": FIF.DOCUMENT, "label": "WPS Office", "key": "wps"},
]


class MainWindow(FluentWindow):
    """主窗口 - 只负责UI和事件分发"""

    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_managers()
        apply_saved_appearance_from_config(self.config_manager)
        self._init_controllers()
        self._init_ui()
        self._init_settings_interface()
        self._connect_signals()

        self.themeListener = SystemThemeListener(self)
        self.settings_interface.apply_saved_theme()

        self.splashScreen.raise_()
        self.show()

        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        self.themeListener.start()
        QTimer.singleShot(100, self._load_initial_data)
        QTimer.singleShot(200, self._check_admin_status)

    # --- init ---

    def _init_window(self):
        from utils.resource_path import get_resource_path
        self.setWindowTitle("SeewoSplash")
        self.setWindowIcon(QIcon(get_resource_path("assets/icon.ico")))
        self.resize(900, 650)
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.center_window()

    def _init_managers(self):
        self.config_manager = ConfigManager()
        self.image_manager = ImageManager()
        self.replacer = ImageReplacer(self.config_manager)
        self.permission_ctrl = PermissionController()

    def _init_controllers(self):
        for pg in PAGES:
            setattr(self, f"{pg['key']}_path_ctrl", PathController(self, self.config_manager, pg["key"]))
            setattr(self, f"{pg['key']}_image_ctrl", ImageController(self, self.config_manager, self.image_manager))

    def _init_ui(self):
        # 共享布局参数
        layout_params = {"margins": (20, 20, 20, 20), "spacing": 15}

        for pg in PAGES:
            key = pg["key"]
            interface = QWidget()
            interface.setObjectName(f"{key}Interface")
            self.addSubInterface(interface, pg["icon"], pg["label"])

            layout = QVBoxLayout(interface)
            layout.setContentsMargins(*layout_params["margins"])
            layout.setSpacing(layout_params["spacing"])

            path_card = PathInfoCard(interface)
            image_list = ImageListWidget(interface)
            action_bar = ActionBar(interface)
            progress_bar = IndeterminateProgressBar(interface)
            progress_bar.setVisible(False)

            layout.addWidget(path_card)
            layout.addWidget(image_list, 1)
            layout.addWidget(action_bar)
            layout.addWidget(progress_bar)

            setattr(self, f"{key}_Interface", interface)
            setattr(self, f"{key}_path_card", path_card)
            setattr(self, f"{key}_image_list", image_list)
            setattr(self, f"{key}_action_bar", action_bar)
            setattr(self, f"{key}_progress_bar", progress_bar)

    def _init_settings_interface(self):
        self.settings_interface = SettingsInterface(self, self.config_manager)
        self.addSubInterface(
            self.settings_interface, FIF.SETTING, '设置',
            position=NavigationItemPosition.BOTTOM
        )

    def _connect_signals(self):
        # 构建页面对象映射表，避免 lambda 闭包陷阱
        pages = {}
        for pg in PAGES:
            key = pg["key"]
            pages[key] = {
                "card": getattr(self, f"{key}_path_card"),
                "ilist": getattr(self, f"{key}_image_list"),
                "abar": getattr(self, f"{key}_action_bar"),
            }

        for key, els in pages.items():
            card = els["card"]
            ilist = els["ilist"]
            abar = els["abar"]

            # 按钮信号无参数，用 functools.partial 避免闭包陷阱
            from functools import partial
            card.detect_button.clicked.connect(partial(self._on_detect_path, key))
            card.history_button.clicked.connect(partial(self._on_show_history, key))
            abar.importClicked.connect(partial(self._on_import_image, key))
            abar.renameClicked.connect(partial(self._on_rename_image, key))
            abar.deleteClicked.connect(partial(self._on_delete_image, key))
            abar.replaceClicked.connect(partial(self._on_replace_image, key))
            abar.restoreClicked.connect(partial(self._on_restore_backup, key))
            # imageSelected 发射 dict → 需要保留 info 参数
            ilist.imageSelected.connect(lambda info, k=key: self._on_image_selected(info, k))
            ilist.imagesDropped.connect(lambda data, k=key: self._on_images_dropped(data, k))

    # --- initial load ---

    def _load_initial_data(self):
        for pg in PAGES:
            self.load_images(pg["key"])
            success, message = getattr(self, f"{pg['key']}_path_ctrl").load_and_validate_target_path()
            card = getattr(self, f"{pg['key']}_path_card")
            if success:
                ctrl = getattr(self, f"{pg['key']}_path_ctrl")
                tp = ctrl.get_target_paths()
                file_count = len(tp) if tp else None
                card.update_path_display(ctrl.target_path, file_count)
                MessageHelper.show_success(self, message, 3000)
            else:
                card.update_path_display("")

        if hasattr(self, 'splashScreen'):
            self.splashScreen.finish()

    # --- event handlers (unified per-page) ---

    def _on_image_selected(self, image_info, page="home"):
        self.config_manager.set_last_selected_image(image_info["filename"], page)
        is_custom = image_info["type"] == "custom"
        getattr(self, f"{page}_action_bar").set_rename_delete_enabled(is_custom)

    def _on_images_dropped(self, drop_data, page="home"):
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

        ctrl = getattr(self, f"{page}_image_ctrl")
        self.show_progress(f"正在导入 {len(file_paths)} 个文件...", page)
        success_count, failed_files = ctrl.import_multiple_images(file_paths)
        self.hide_progress(page)

        if success_count > 0:
            msg = f"成功导入 {success_count} 个图片"
            if failed_files:
                msg += f"，{len(failed_files)} 个失败"
            MessageHelper.show_success(self, msg, 3000)
            self.load_images(page)

        if failed_files:
            error_details = "\n".join(f"• {name}: {msg}" for name, msg in failed_files[:5])
            if len(failed_files) > 5:
                error_details += f"\n... 还有 {len(failed_files) - 5} 个文件失败"
            MessageHelper.show_error(self, "部分文件导入失败", error_details)

    def _on_detect_path(self, page="home"):
        ctrl = getattr(self, f"{page}_path_ctrl")
        card = getattr(self, f"{page}_path_card")

        self.show_progress("正在检测路径...", page)
        success, message = ctrl.detect_with_user_interaction()
        self.hide_progress(page)

        tp = ctrl.get_target_paths()
        file_count = len(tp) if tp else None
        card.update_path_display(ctrl.target_path, file_count)
        if success:
            MessageHelper.show_success(self, message, 5000)
        elif message:
            MessageHelper.show_error(self, "检测失败", message)

    def _on_show_history(self, page="home"):
        ctrl = getattr(self, f"{page}_path_ctrl")
        card = getattr(self, f"{page}_path_card")

        success, result, need_detect = ctrl.select_from_history()
        if success:
            tp = ctrl.get_target_paths()
            file_count = len(tp) if tp else None
            card.update_path_display(result, file_count)
            MessageHelper.show_success(self, f"已设置目标路径: {os.path.basename(result)}", 5000)
        elif need_detect:
            self._on_detect_path(page)

    def _on_import_image(self, page="home"):
        ctrl = getattr(self, f"{page}_image_ctrl")
        self.show_progress("正在导入...", page)
        success, msg, source_path = ctrl.import_single_image(allow_multiple=True)
        self.hide_progress(page)

        if success:
            MessageHelper.show_success(self, f"图片导入成功: {os.path.basename(source_path)}", 3000)
            self.load_images(page)
        elif msg:
            MessageHelper.show_error(self, "导入失败", msg)

    def _on_rename_image(self, page="home"):
        ilist = getattr(self, f"{page}_image_list")
        image_info = ilist.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要重命名的图片")
            return

        ctrl = getattr(self, f"{page}_image_ctrl")
        success, msg = ctrl.rename_image(image_info)
        if success:
            MessageHelper.show_success(self, msg, 2000)
            self.load_images(page)
        elif msg:
            MessageHelper.show_warning(self, "重命名失败", msg)

    def _on_delete_image(self, page="home"):
        ilist = getattr(self, f"{page}_image_list")
        image_info = ilist.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先选择要删除的图片")
            return

        ctrl = getattr(self, f"{page}_image_ctrl")
        success, msg = ctrl.delete_image(image_info)
        if success:
            MessageHelper.show_success(self, msg, 2000)
            self.load_images(page)
        else:
            MessageHelper.show_error(self, "删除失败", msg)

    def _on_replace_image(self, page="home"):
        ctrl = getattr(self, f"{page}_path_ctrl")
        ilist = getattr(self, f"{page}_image_list")
        replacer = self.replacer

        if not ctrl.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return

        image_info = ilist.get_selected_image_info()
        if not image_info:
            MessageHelper.show_warning(self, "未选择图片", "请先从列表中选择要替换的图片")
            return

        target_paths = ctrl.get_target_paths()
        if not target_paths:
            MessageHelper.show_warning(self, "未找到启动图文件", "请确保splash目录包含所有必要的启动图文件")
            return

        # WPS 用批量，希沃走单文件
        if page == "wps":
            self.show_progress(f"正在替换 {len(target_paths)} 个文件...", page)
            success, msg, is_perm_error, sc, fc = replacer.replace_multiple_images(
                image_info["path"], target_paths, self.config_manager
            )
            self.hide_progress(page)

            if success:
                if sc == len(target_paths):
                    MessageHelper.show_success(self, f"启动图片已替换为: {image_info['display_name']}\n成功替换 {sc} 个文件", 4000)
                else:
                    MessageHelper.show_warning(self, f"部分替换成功\n{msg}", 5000)
            elif is_perm_error:
                self.permission_ctrl.handle_permission_error(self, msg)
            else:
                MessageHelper.show_error(self, "替换失败", msg)
        else:
            self.show_progress("正在替换...", page)
            success, msg, is_perm_error = replacer.replace_image(
                image_info["path"], ctrl.target_path, self.config_manager
            )
            self.hide_progress(page)

            if success:
                MessageHelper.show_success(self, f"启动图片已替换为: {image_info['display_name']}", 3000)
            elif is_perm_error:
                self.permission_ctrl.handle_permission_error(self, msg)
            else:
                MessageHelper.show_error(self, "替换失败", msg)

    def _on_restore_backup(self, page="home"):
        ctrl = getattr(self, f"{page}_path_ctrl")
        replacer = self.replacer

        if not ctrl.target_path:
            MessageHelper.show_warning(self, "未检测到路径", "请先点击'检测路径'按钮")
            return

        target_paths = ctrl.get_target_paths()
        if not target_paths:
            MessageHelper.show_warning(self, "未找到启动图文件", "请确保splash目录包含所有必要的启动图文件")
            return

        if page == "wps":
            self.show_progress(f"正在还原 {len(target_paths)} 个文件...", page)
            success, msg, is_perm_error, sc, fc = replacer.restore_multiple_backups(target_paths)
            self.hide_progress(page)

            if success:
                if sc == len(target_paths):
                    MessageHelper.show_success(self, f"已从备份还原启动图片\n成功还原 {sc} 个文件", 4000)
                else:
                    MessageHelper.show_warning(self, f"部分还原成功\n{msg}", 5000)
            elif is_perm_error:
                self.permission_ctrl.handle_permission_error(self, msg)
            else:
                MessageHelper.show_error(self, "还原失败", msg)
        else:
            self.show_progress("正在还原...", page)
            success, msg, is_perm_error = replacer.restore_backup(ctrl.target_path)
            self.hide_progress(page)

            if success:
                MessageHelper.show_success(self, "已从备份还原启动图片", 3000)
            elif is_perm_error:
                self.permission_ctrl.handle_permission_error(self, msg)
            else:
                MessageHelper.show_error(self, "还原失败", msg)

    # --- helpers ---

    def show_progress(self, message: str, page="home"):
        getattr(self, f"{page}_progress_bar").setVisible(True)
        getattr(self, f"{page}_progress_bar").start()
        MessageHelper.show_success(self, message, 2000)

    def hide_progress(self, page="home"):
        getattr(self, f"{page}_progress_bar").stop()
        getattr(self, f"{page}_progress_bar").setVisible(False)

    def load_images(self, page="home"):
        preset_images = self.image_manager.get_preset_images(page)
        custom_images = self.image_manager.get_custom_images()
        getattr(self, f"{page}_image_list").load_images(preset_images, custom_images)

        last_selected = self.config_manager.get_last_selected_image(page)
        if last_selected:
            getattr(self, f"{page}_image_list").select_image_by_filename(last_selected)

    def _check_admin_status(self):
        if is_admin():
            current_title = self.windowTitle()
            self.setWindowTitle(f"{current_title} [管理员]")

    def center_window(self):
        screen = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        if hasattr(self, 'themeListener'):
            self.themeListener.terminate()
            self.themeListener.deleteLater()
        super().closeEvent(e)
