import shutil
from pathlib import Path
from utils.resource_path import get_resource_path, get_app_data_path, ensure_dir


class ImageManager:
    """图片管理器"""
    
    def __init__(self):
        # 预设图片目录（打包后在 _internal/assets/presets 中）
        self.preset_dir = Path(get_resource_path("assets/presets"))
        
        # WPS预设图片目录（打包后在 _internal/assets/presets/wps 中）
        self.wps_preset_dir = Path(get_resource_path("assets/presets/wps"))
        
        # 自定义图片目录（在可执行文件目录的 images/custom 中）
        self.custom_dir = Path(get_app_data_path("images/custom"))
        
        # 确保自定义目录存在
        ensure_dir(self.custom_dir)
        
        print(f"[DEBUG] 预设图片目录: {self.preset_dir}")
        print(f"[DEBUG] 预设图片目录存在: {self.preset_dir.exists()}")
        print(f"[DEBUG] WPS预设图片目录: {self.wps_preset_dir}")
        print(f"[DEBUG] WPS预设图片目录存在: {self.wps_preset_dir.exists()}")
        print(f"[DEBUG] 自定义图片目录: {self.custom_dir}")
        print(f"[DEBUG] 自定义图片目录存在: {self.custom_dir.exists()}")
        
        # 从配置加载自定义图片信息
        from core.config_manager import ConfigManager
        self.config_manager = ConfigManager()
    
    def get_preset_images(self, page="home"):
        """获取预设图片列表
        
        Args:
            page: 页面标识，"home" 或 "wps"
        """
        preset_images = []
        
        # 根据页面选择预设目录
        preset_dir = self.wps_preset_dir if page == "wps" else self.preset_dir
        
        if not preset_dir.exists():
            print(f"警告: 预设图片目录不存在: {preset_dir}")
            return preset_images
        
        # 预设图片的显示名称映射
        if page == "wps":
            preset_names = {
                "default.png": "默认图片",
                "minimal.png": "简约风格",
                "colorful.png": "彩色风格",
                "professional.png": "专业风格",
            }
        else:
            preset_names = {
                "default.png": "默认图片",
                "minimal.png": "简约风格",
                "colorful.png": "彩色风格",
                "professional.png": "专业风格",
            }
        
        for img_file in preset_dir.glob("*.png"):
            display_name = preset_names.get(img_file.name, img_file.stem)
            preset_images.append({
                "filename": img_file.name,
                "display_name": display_name,
                "path": str(img_file),
                "type": "preset"
            })
            print(f"[DEBUG] 找到预设图片: {img_file.name}")
        
        return sorted(preset_images, key=lambda x: x["filename"])
    
    def get_custom_images(self):
        """获取自定义图片列表"""
        custom_images = []
        
        if not self.custom_dir.exists():
            print(f"[DEBUG] 自定义图片目录不存在，创建中...")
            ensure_dir(self.custom_dir)
            return custom_images
        
        # 从配置读取自定义图片的显示名称
        config_custom_images = self.config_manager.get_custom_images()
        name_map = {img["filename"]: img["display_name"] for img in config_custom_images}
        
        for img_file in self.custom_dir.glob("*.png"):
            display_name = name_map.get(img_file.name, img_file.stem)
            custom_images.append({
                "filename": img_file.name,
                "display_name": display_name,
                "path": str(img_file),
                "type": "custom"
            })
            print(f"[DEBUG] 找到自定义图片: {img_file.name}")
        
        return sorted(custom_images, key=lambda x: x["filename"])
    
    def import_image(self, source_path):
        """
        导入图片到自定义目录
        
        Args:
            source_path: 源图片路径
        
        Returns:
            (success, message)
        """
        try:
            source_path = Path(source_path)
            
            # 验证文件
            if not source_path.exists():
                return False, "源文件不存在"
            
            if source_path.suffix.lower() != ".png":
                return False, "只支持PNG格式图片"
            
            # 确保自定义目录存在
            ensure_dir(self.custom_dir)
            
            # 生成目标文件名
            dest_filename = source_path.name
            dest_path = self.custom_dir / dest_filename
            
            # 如果文件已存在，添加序号
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                dest_filename = f"{stem}_{counter}.png"
                dest_path = self.custom_dir / dest_filename
                counter += 1
            
            # 复制文件
            shutil.copy2(source_path, dest_path)
            
            # 添加到配置
            display_name = source_path.stem
            self.config_manager.add_custom_image({
                "filename": dest_filename,
                "display_name": display_name
            })
            
            return True, str(dest_path)
            
        except Exception as e:
            return False, f"导入失败: {str(e)}"
    
    def delete_custom_image(self, filename):
        """
        删除自定义图片
        
        Args:
            filename: 文件名
        
        Returns:
            success
        """
        try:
            file_path = self.custom_dir / filename
            if file_path.exists():
                file_path.unlink()
            
            # 从配置中移除
            self.config_manager.remove_custom_image(filename)
            return True
        except Exception as e:
            print(f"删除图片失败: {e}")
            return False
    
    def rename_custom_image(self, old_filename, new_display_name):
        """
        重命名自定义图片（同时修改文件名和显示名称）
        
        Args:
            old_filename: 原文件名
            new_display_name: 新的显示名称
        
        Returns:
            (success, message, new_filename)
        """
        try:
            old_file_path = self.custom_dir / old_filename
            if not old_file_path.exists():
                return False, "文件不存在", old_filename
            
            # 获取原文件扩展名
            old_extension = old_file_path.suffix
            
            # 构建新文件名（显示名称 + 原扩展名）
            new_filename = new_display_name + old_extension
            new_file_path = self.custom_dir / new_filename
            
            # 检查文件名冲突
            if new_file_path.exists() and new_filename != old_filename:
                return False, f"文件名已存在: {new_filename}", old_filename
            
            # 重命名文件
            if new_filename != old_filename:
                old_file_path.rename(new_file_path)
            
            return True, "重命名成功", new_filename
            
        except Exception as e:
            return False, f"重命名失败: {str(e)}", old_filename

