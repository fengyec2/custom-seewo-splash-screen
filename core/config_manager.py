# file core\config_manager.py

import json
import os
from utils.resource_path import get_app_data_path


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file="config/config.json"):
        # 配置文件保存在可执行文件目录（默认与 qfluentwidgets 保持一致：config/config.json）
        self.config_file = get_app_data_path(config_file)

        # 兼容性迁移：如果新位置不存在但根目录下存在旧的 config.json，则移动到新位置
        try:
            root_config = get_app_data_path(os.path.basename(config_file))
            if not os.path.exists(self.config_file) and os.path.exists(root_config):
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                os.replace(root_config, self.config_file)
        except Exception as e:
            # 不要中断启动，仅打印信息
            print(f"配置迁移失败: {e}")

        self.config = self.load()
    
    def load(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
                return self.default_config()
        return self.default_config()
    
    def save(self):
        """保存配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def default_config(self):
        """默认配置"""
        return {
            "target_path": "",
            "target_path_history": [],
            "wps_target_path": "",
            "wps_target_path_history": [],
            "last_selected_image": "",
            "wps_last_selected_image": "",
            "custom_images": [],
            "auto_detect_on_startup": True,
            "theme_mode": "auto",  # 主题模式: light, dark, auto
            "theme_color": "#009FAA",  # 默认主题色（QFluentWidgets 蓝色）
            "use_custom_theme_color": False,  # 是否使用自定义主题色（False表示使用默认颜色）
            "mica_effect": True,  # 云母效果（默认开启）
            "file_protection_enabled": False  # 文件保护功能（默认关闭）
            ,"protected_files": []
        }
    
    def get_target_path(self, page="home"):
        """获取目标路径
        
        Args:
            page: 页面标识，"home" 或 "wps"
        """
        if page == "wps":
            return self.config.get("wps_target_path", "")
        return self.config.get("target_path", "")
    
    def set_target_path(self, path, page="home"):
        """设置目标路径
        
        Args:
            path: 目标路径
            page: 页面标识，"home" 或 "wps"
        """
        if page == "wps":
            if path:
                self.config["wps_target_path"] = path
                self.add_to_path_history(path, page)
            else:
                self.config["wps_target_path"] = ""
        else:
            if path:
                self.config["target_path"] = path
                self.add_to_path_history(path, page)
            else:
                self.config["target_path"] = ""
        self.save()
    
    def add_to_path_history(self, path, page="home"):
        """添加路径到历史记录
        
        Args:
            path: 路径
            page: 页面标识，"home" 或 "wps"
        """
        history_key = "wps_target_path_history" if page == "wps" else "target_path_history"
        if history_key not in self.config:
            self.config[history_key] = []
        
        if path in self.config[history_key]:
            self.config[history_key].remove(path)
        
        self.config[history_key].insert(0, path)
        self.config[history_key] = self.config[history_key][:5]
        self.save()
    
    def get_path_history(self, page="home"):
        """获取路径历史记录
        
        Args:
            page: 页面标识，"home" 或 "wps"
        """
        history_key = "wps_target_path_history" if page == "wps" else "target_path_history"
        return self.config.get(history_key, [])
    
    def clear_invalid_history(self, page="home"):
        """清理无效的历史路径
        
        Args:
            page: 页面标识，"home" 或 "wps"
        """
        history_key = "wps_target_path_history" if page == "wps" else "target_path_history"
        if history_key not in self.config:
            return
        
        valid_paths = [
            path for path in self.config[history_key]
            if os.path.exists(path)
        ]
        self.config[history_key] = valid_paths
        self.save()
    
    def get_auto_detect_on_startup(self):
        """获取启动时是否自动检测"""
        return self.config.get("auto_detect_on_startup", True)
    
    def set_auto_detect_on_startup(self, enabled):
        """设置启动时是否自动检测"""
        self.config["auto_detect_on_startup"] = enabled
        self.save()
    
    def get_theme_mode(self):
        """获取主题模式"""
        return self.config.get("theme_mode", "auto")
    
    def set_theme_mode(self, theme_mode):
        """设置主题模式
        
        Args:
            theme_mode (str): 主题模式，可选值: light, dark, auto
        """
        if theme_mode in ["light", "dark", "auto"]:
            self.config["theme_mode"] = theme_mode
            self.save()
        else:
            print(f"无效的主题模式: {theme_mode}")
    
    def get_theme_color(self):
        """获取主题色
        
        Returns:
            str: 十六进制颜色值，如 "#0078D4"
        """
        return self.config.get("theme_color", "#009FAA")
    
    def set_theme_color(self, color, is_custom=True):
        """设置主题色
        
        Args:
            color (str): 十六进制颜色值，如 "#0078D4"
            is_custom (bool): 是否为自定义颜色（True表示自定义，False表示使用默认颜色）
        """
        if isinstance(color, str) and (color.startswith("#") and len(color) == 7):
            self.config["theme_color"] = color
            self.config["use_custom_theme_color"] = is_custom
            self.save()
        else:
            print(f"无效的颜色格式: {color}，应为十六进制格式如 #0078D4")
    
    def get_use_custom_theme_color(self):
        """获取是否使用自定义主题色
        
        Returns:
            bool: 是否使用自定义主题色
        """
        return self.config.get("use_custom_theme_color", False)
    
    def set_use_custom_theme_color(self, is_custom):
        """设置是否使用自定义主题色
        
        Args:
            is_custom (bool): 是否使用自定义主题色
        """
        self.config["use_custom_theme_color"] = is_custom
        self.save()
    
    def get_mica_effect(self):
        """获取云母效果设置
        
        Returns:
            bool: 是否启用云母效果
        """
        return self.config.get("mica_effect", False)
    
    def set_mica_effect(self, enabled):
        """设置云母效果
        
        Args:
            enabled (bool): 是否启用云母效果
        """
        if isinstance(enabled, bool):
            self.config["mica_effect"] = enabled
            self.save()
        else:
            print(f"云母效果设置必须为布尔值，收到: {type(enabled)}")
    
    def get_last_selected_image(self, page="home"):
        """获取最后选中的图片
        
        Args:
            page: 页面标识，"home" 或 "wps"
        """
        if page == "wps":
            return self.config.get("wps_last_selected_image", "")
        return self.config.get("last_selected_image", "")
    
    def set_last_selected_image(self, image_name, page="home"):
        """设置最后选中的图片
        
        Args:
            image_name: 图片名称
            page: 页面标识，"home" 或 "wps"
        """
        if page == "wps":
            self.config["wps_last_selected_image"] = image_name
        else:
            self.config["last_selected_image"] = image_name
        self.save()
    
    def get_custom_images(self):
        """获取自定义图片列表"""
        return self.config.get("custom_images", [])
    
    def add_custom_image(self, image_info):
        """添加自定义图片"""
        if "custom_images" not in self.config:
            self.config["custom_images"] = []
        self.config["custom_images"].append(image_info)
        self.save()
    
    def remove_custom_image(self, filename):
        """移除自定义图片"""
        if "custom_images" in self.config:
            self.config["custom_images"] = [
                img for img in self.config["custom_images"] 
                if img.get("filename") != filename
            ]
            self.save()
    
    def update_custom_image_name(self, old_filename, new_display_name, new_filename):
        """更新自定义图片信息"""
        if "custom_images" in self.config:
            for img in self.config["custom_images"]:
                if img.get("filename") == old_filename:
                    img["display_name"] = new_display_name
                    img["filename"] = new_filename
                    break
            self.save()

    def get_file_protection_enabled(self):
        """获取文件保护功能是否启用
        
        Returns:
            bool: 是否启用文件保护
        """
        return self.config.get("file_protection_enabled", False)

    def set_file_protection_enabled(self, enabled):
        """设置文件保护功能
        
        Args:
            enabled (bool): 是否启用文件保护
        """
        if isinstance(enabled, bool):
            self.config["file_protection_enabled"] = enabled
            self.save()
        else:
            print(f"文件保护设置必须为布尔值，收到: {type(enabled)}")
    
    def reset_appearance_settings(self):
        """重置外观设置到默认值"""
        default = self.default_config()
        self.config["theme_mode"] = default["theme_mode"]
        self.config["theme_color"] = default["theme_color"]
        self.config["mica_effect"] = default["mica_effect"]
        self.save()
    
    def export_settings(self):
        """导出设置（返回配置字典的副本）"""
        return self.config.copy()
    
    def import_settings(self, settings_dict):
        """导入设置
        
        Args:
            settings_dict (dict): 要导入的设置字典
        
        Returns:
            bool: 导入是否成功
        """
        try:
            # 验证必要的字段
            valid_keys = set(self.default_config().keys())
            imported_keys = set(settings_dict.keys())
            
            # 只导入有效的配置项
            for key in imported_keys.intersection(valid_keys):
                self.config[key] = settings_dict[key]
            
            return self.save()
        except Exception as e:
            print(f"导入设置失败: {e}")
            return False

    def get_protected_files(self):
        """获取已记录的受保护文件路径列表"""
        return self.config.get("protected_files", [])

    def add_protected_file(self, file_path: str):
        """将文件路径添加到已保护文件列表并保存"""
        if "protected_files" not in self.config:
            self.config["protected_files"] = []
        if file_path not in self.config["protected_files"]:
            self.config["protected_files"].append(file_path)
            self.save()

    def remove_protected_file(self, file_path: str):
        """从已保护文件列表中移除路径并保存"""
        if "protected_files" in self.config and file_path in self.config["protected_files"]:
            self.config["protected_files"].remove(file_path)
            self.save()
