"""图片操作控制器 - 处理所有图片相关的业务逻辑"""

import os
from PyQt5.QtWidgets import QWidget, QFileDialog
from core.config_manager import ConfigManager
from core.image_manager import ImageManager
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit
from ui.dialogs.message_helper import MessageHelper

class ImageController:
    """图片操作控制器"""
    
    def __init__(self, parent: QWidget, config_manager: ConfigManager, 
                 image_manager: ImageManager):
        self.parent = parent
        self.config_manager = config_manager
        self.image_manager = image_manager
    
    def import_single_image(self, allow_multiple: bool = False) -> tuple[bool, str, str]:
        """导入图片
        
        Args:
            allow_multiple: 是否允许选择多个文件
            
        Returns:
            (成功标志, 消息, 文件路径)
        """
        file_dialog = QFileDialog(self.parent, "选择PNG图片", os.path.expanduser("~"))
        file_dialog.setNameFilter("PNG图片 (*.png)")
        
        # 根据参数设置文件选择模式
        if allow_multiple:
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        else:
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                if allow_multiple:
                    # 使用现有的批量导入逻辑
                    success_count, failed_files = self.import_multiple_images(selected_files)
                    if success_count > 0:
                        if failed_files:
                            msg = f"成功导入 {success_count} 个图片，{len(failed_files)} 个失败"
                        else:
                            msg = f"成功导入 {success_count} 个图片"
                        return True, msg, selected_files[0]  # 返回第一个文件路径保持接口一致
                    else:
                        return False, "所有图片导入失败", ""
                else:
                    # 原有的单个导入逻辑
                    source_path = selected_files[0]
                    success, msg = self.image_manager.import_image(source_path)
                    return success, msg, source_path
        
        return False, "", ""
    
    def import_multiple_images(self, file_paths: list[str]) -> tuple[int, list]:
        """批量导入图片
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            (成功数量, 失败文件列表[(文件名, 错误信息)])
        """
        success_count = 0
        failed_files = []
        
        for file_path in file_paths:
            success, msg = self.image_manager.import_image(file_path)
            if success:
                success_count += 1
            else:
                failed_files.append((os.path.basename(file_path), msg))
        
        return success_count, failed_files
    
    def rename_image(self, image_info: dict) -> tuple[bool, str]:
        """重命名图片
        
        Args:
            image_info: 图片信息
            
        Returns:
            (成功标志, 消息)
        """
        if image_info["type"] != "custom":
            return False, "只能重命名自定义图片"
        
        # 创建并显示重命名对话框
        dialog = RenameImageDialog(image_info["display_name"], self.parent)
        
        if dialog.exec():
            new_name = dialog.nameLineEdit.text().strip()
            
            success, msg, new_filename = self.image_manager.rename_custom_image(
                image_info["filename"],
                new_name
            )
            
            if success:
                # 更新配置
                self.config_manager.update_custom_image_name(
                    image_info["filename"],
                    new_name,
                    new_filename
                )
                return True, f"已重命名为: {new_name}"
            else:
                MessageHelper.show_error(self.parent, "重命名失败", msg)
                return False, msg
        
        return False, ""
    
    def delete_image(self, image_info: dict) -> tuple[bool, str]:
        """删除图片
        
        Args:
            image_info: 图片信息
            
        Returns:
            (成功标志, 消息)
        """
        if image_info["type"] != "custom":
            return False, "只能删除自定义图片"
        
        success = self.image_manager.delete_custom_image(image_info["filename"])
        if success:
            self.config_manager.remove_custom_image(image_info["filename"])
            return True, f"已删除图片: {image_info['display_name']}"
        
        return False, "无法删除图片,请检查文件权限"

class RenameImageDialog(MessageBoxBase):
        """重命名图片对话框"""
        
        def __init__(self, current_name: str, parent=None):
            super().__init__(parent)
            self.titleLabel = SubtitleLabel('重命名图片')
            self.nameLineEdit = LineEdit()
            
            self.nameLineEdit.setPlaceholderText('请输入新的显示名称')
            self.nameLineEdit.setText(current_name)
            self.nameLineEdit.setClearButtonEnabled(True)
            
            # 将组件添加到布局中
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.nameLineEdit)
            
            # 设置对话框的最小宽度
            self.widget.setMinimumWidth(350)
        
        def validate(self):
            """验证输入是否为空"""
            return bool(self.nameLineEdit.text().strip())