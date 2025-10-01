import os
import glob
import re
from qfluentwidgets import MessageBox
from PyQt6.QtWidgets import QFileDialog


class PathDetector:
    """检测希沃白板启动图片路径"""
    
    @staticmethod
    def detect_banner_paths():
        """检测Banner.png路径"""
        paths = []
        users_dir = "C:\\Users"
        
        if os.path.exists(users_dir):
            for user_folder in os.listdir(users_dir):
                banner_path = os.path.join(
                    users_dir, 
                    user_folder, 
                    "AppData\\Roaming\\Seewo\\EasiNote5\\Resources\\Banner\\Banner.png"
                )
                if os.path.exists(banner_path):
                    paths.append(banner_path)
        
        return paths
    
    @staticmethod
    def detect_splashscreen_paths():
        """检测SplashScreen.png路径"""
        paths = []
        
        # 检测 Program Files (x86)
        base_path_x86 = "C:\\Program Files (x86)\\Seewo\\EasiNote5"
        if os.path.exists(base_path_x86):
            # 所有可能的路径组合
            patterns = [
                # 旧版路径格式
                os.path.join(base_path_x86, "EasiNote5*", "Main", "Assets", "SplashScreen.png"),
                # 新版路径格式
                os.path.join(base_path_x86, "EasiNote5_*", "Main", "Resources", "Startup", "SplashScreen.png"),
            ]
            
            for pattern in patterns:
                paths.extend(glob.glob(pattern))
        
        # 检测 Program Files
        base_path = "C:\\Program Files\\Seewo\\EasiNote5"
        if os.path.exists(base_path):
            # 所有可能的路径组合
            patterns = [
                # 旧版路径格式
                os.path.join(base_path, "EasiNote5*", "Main", "Assets", "SplashScreen.png"),
                # 新版路径格式
                os.path.join(base_path, "EasiNote5_*", "Main", "Resources", "Startup", "SplashScreen.png"),
            ]
            
            for pattern in patterns:
                paths.extend(glob.glob(pattern))
        
        return paths
    
    @staticmethod
    def detect_all_easinote_versions():
        """
        检测所有版本的希沃白板安装路径
        
        Returns:
            list: 包含版本信息的字典列表
        """
        versions = []
        
        # 检测 Program Files (x86)
        base_paths = [
            "C:\\Program Files (x86)\\Seewo\\EasiNote5",
            "C:\\Program Files\\Seewo\\EasiNote5"
        ]
        
        for base_path in base_paths:
            if os.path.exists(base_path):
                # 查找所有版本目录
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path) and item.startswith("EasiNote5"):
                        # 解析版本信息
                        version_info = PathDetector._parse_version_info(item)
                        if version_info:
                            version_info['base_path'] = base_path
                            version_info['full_path'] = item_path
                            versions.append(version_info)
        
        # 按版本号排序（新版本在前）
        versions.sort(key=lambda x: x['version_tuple'], reverse=True)
        return versions
    
    @staticmethod
    def _parse_version_info(folder_name):
        """
        解析版本信息
        
        Args:
            folder_name: 文件夹名称，如 "EasiNote5_5.2.4.9158"
            
        Returns:
            dict: 版本信息字典
        """
        # 匹配版本号模式
        patterns = [
            r'EasiNote5_(\d+\.\d+\.\d+\.\d+)',  # 新版: EasiNote5_5.2.4.9158
            r'EasiNote5\.(\d+\.\d+\.\d+)',      # 旧版: EasiNote5.5.2.3
            r'EasiNote5_(\d+\.\d+\.\d+)',       # 可能的格式: EasiNote5_5.2.3
            r'EasiNote5\.(\d+)',                # 更简单的格式: EasiNote5.5
        ]
        
        for pattern in patterns:
            match = re.search(pattern, folder_name)
            if match:
                version_str = match.group(1)
                version_parts = version_str.split('.')
                
                # 补齐版本号至4位
                while len(version_parts) < 4:
                    version_parts.append('0')
                
                try:
                    version_tuple = tuple(int(part) for part in version_parts[:4])
                    return {
                        'folder_name': folder_name,
                        'version_str': version_str,
                        'version_tuple': version_tuple,
                        'is_new_format': folder_name.startswith('EasiNote5_')
                    }
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def get_splash_paths_by_version():
        """
        按版本获取启动图路径
        
        Returns:
            list: 包含路径和版本信息的字典列表
        """
        splash_paths = []
        versions = PathDetector.detect_all_easinote_versions()
        
        for version in versions:
            # 尝试所有可能的路径组合
            possible_paths = [
                # 路径1: Main/Assets/SplashScreen.png (最常见)
                os.path.join(version['full_path'], "Main", "Assets", "SplashScreen.png"),
                # 路径2: Main/Resources/Startup/SplashScreen.png (新版可能路径)
                os.path.join(version['full_path'], "Main", "Resources", "Startup", "SplashScreen.png"),
            ]
            
            for splash_path in possible_paths:
                if os.path.exists(splash_path):
                    # 确定路径类型
                    if "Resources\\Startup" in splash_path:
                        path_type = "新版路径格式"
                    else:
                        path_type = "标准路径格式"
                    
                    splash_paths.append({
                        'path': splash_path,
                        'version': version['version_str'],
                        'folder_name': version['folder_name'],
                        'is_new_format': version['is_new_format'],
                        'path_type': path_type
                    })
                    break  # 找到一个有效路径就跳出
        
        return splash_paths
    
    @staticmethod
    def detect_all_paths():
        """检测所有可能的路径"""
        all_paths = []
        all_paths.extend(PathDetector.detect_banner_paths())
        all_paths.extend(PathDetector.detect_splashscreen_paths())
        return all_paths
    
    @staticmethod
    def get_all_paths_with_info():
        """
        获取所有路径及其详细信息
        
        Returns:
            list: 包含路径信息的字典列表
        """
        all_paths = []
        
        # Banner路径
        banner_paths = PathDetector.detect_banner_paths()
        for path in banner_paths:
            # 从路径中提取用户名
            user_name = path.split('\\')[2] if len(path.split('\\')) > 2 else 'Unknown'
            all_paths.append({
                'path': path,
'type': 'Banner',
                'description': f'Banner图片 (用户: {user_name})',
                'version': 'N/A'
            })
        
        # SplashScreen路径
        splash_paths = PathDetector.get_splash_paths_by_version()
        for info in splash_paths:
            folder_prefix = "新版" if info['is_new_format'] else "旧版"
            description = f'{folder_prefix}启动图 - {info["path_type"]} (版本: {info["version"]})'
            all_paths.append({
                'path': info['path'],
                'type': 'SplashScreen',
                'description': description,
                'version': info['version']
            })
        
        return all_paths
    
    @staticmethod
    def manual_select_target_image(parent=None):
        """
        手动选择目标图片
        
        Args:
            parent: 父窗口对象
            
        Returns:
            str: 选中的图片路径,如果取消则返回空字符串
        """
        # 创建自定义消息框
        content = (
            "无法自动检测到希沃白板的启动图片。\n\n"
            "您可以手动选择要替换的目标图片文件。\n"
            "目标图片通常位于以下位置之一:\n\n"
            "1. Banner.png:\n"
            "   C:\\Users\\[用户名]\\AppData\\Roaming\\Seewo\\EasiNote5\\Resources\\Banner\\Banner.png\n\n"
            "2. SplashScreen.png (旧版):\n"
            "   C:\\Program Files\\Seewo\\EasiNote5\\EasiNote5.xxx\\Main\\Assets\\SplashScreen.png\n\n"
            "3. SplashScreen.png (新版):\n"
            "   C:\\Program Files\\Seewo\\EasiNote5\\EasiNote5_x.x.x.xxxx\\Main\\Resources\\Startup\\SplashScreen.png\n\n"
            "是否现在手动选择目标图片?"
        )
        
        # 使用 MessageBox 创建询问对话框
        w = MessageBox("手动选择目标图片", content, parent)
        if not w.exec():
            return ""
        
        # 打开文件选择对话框
        file_dialog = QFileDialog(parent, "选择希沃白板启动图片")
        file_dialog.setNameFilter("PNG图片 (*.png);;所有文件 (*.*)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        # 设置初始目录为常见路径
        initial_dir = "C:\\Program Files\\Seewo\\EasiNote5"
        if not os.path.exists(initial_dir):
            initial_dir = "C:\\Program Files (x86)\\Seewo\\EasiNote5"
        if not os.path.exists(initial_dir):
            initial_dir = os.path.join(os.environ.get("APPDATA", "C:\\"), "Seewo")
        if not os.path.exists(initial_dir):
            initial_dir = "C:\\"
        
        file_dialog.setDirectory(initial_dir)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                selected_path = selected_files[0]
                
                # 验证选择的文件
                if not selected_path.lower().endswith('.png'):
                    w = MessageBox(
                        "文件类型错误",
                        "请选择PNG格式的图片文件。",
                        parent
                    )
                    w.exec()
                    return ""
                
                if not os.path.exists(selected_path):
                    w = MessageBox(
                        "文件不存在",
                        "选择的文件不存在,请重新选择。",
                        parent
                    )
                    w.exec()
                    return ""
                
                # 确认选择
                filename = os.path.basename(selected_path)
                confirm_content = (
                    f"您选择的目标图片是:\n\n{selected_path}\n\n"
                    f"文件名: {filename}\n\n"
                    "确认使用此图片作为替换目标吗?"
                )
                
                w = MessageBox("确认目标图片", confirm_content, parent)
                if w.exec():
                    return selected_path
        
        return ""
    
    @staticmethod
    def validate_target_path(path):
        """
        验证目标路径是否有效
        
        Args:
            path: 要验证的路径
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not path:
            return False, "路径为空"
        
        if not os.path.exists(path):
            return False, "文件不存在"
        
        if not path.lower().endswith('.png'):
            return False, "不是PNG文件"
        
        if not os.path.isfile(path):
            return False, "不是文件"
        
        # 检查是否有读写权限
        if not os.access(path, os.R_OK):
            return False, "没有读取权限"
        
        # 检查文件大小(启动图片通常不会太小)
        file_size = os.path.getsize(path)
        if file_size < 1024:  # 小于1KB
            return False, "文件太小,可能不是有效的启动图片"
        
        return True, "路径有效"
