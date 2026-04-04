import os
import sys
import glob
import re
from qfluentwidgets import MessageBox
from PyQt6.QtWidgets import QFileDialog


class PathDetector:
    """检测希沃白板启动图片路径"""
    
    @staticmethod
    def _get_available_drives():
        """
        获取所有可用的驱动器盘符
        
        Returns:
            list: 可用驱动器盘符列表，如 ['C', 'D', 'E']
        """
        drives = []
        for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_path = f"{drive_letter}:\\"
            if os.path.exists(drive_path):
                drives.append(drive_letter)
        
        # 如果没有找到驱动器，尝试从环境变量获取
        if not drives:
            userprofile = os.environ.get("USERPROFILE", "")
            if userprofile:
                drive = os.path.splitdrive(userprofile)[0]
                if drive:
                    drive_letter = drive[0]
                    if drive_letter not in drives:
                        drives.append(drive_letter)
        
        return drives
    
    @staticmethod
    def _collect_wps_splash_from_base_dirs(base_paths):
        """在给定的 WPS 安装根目录下查找已验证的 splash 目录。"""
        splash_dirs = []
        splash_dir_patterns = [
            "office6\\mui\\*\\resource\\splash",
            "office6\\mui\\*\\res\\splash",
            "office6\\res\\splash",
            "wps\\res\\splash",
        ]
        for base_path in base_paths:
            if not base_path or not os.path.exists(base_path):
                continue
            for pattern in splash_dir_patterns:
                full_pattern = os.path.join(base_path, pattern)
                for splash_dir in glob.glob(full_pattern):
                    if os.path.isdir(splash_dir) and PathDetector._validate_wps_splash_dir(splash_dir):
                        splash_dirs.append(splash_dir)
        return splash_dirs
    
    @staticmethod
    def _enum_uninstall_subkeys():
        """枚举卸载信息子键 (hkey, parent_path, subkey_name)。"""
        if sys.platform != "win32":
            return
        import winreg
        roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for hkey, parent_path in roots:
            try:
                with winreg.OpenKey(hkey, parent_path, 0, winreg.KEY_READ) as key:
                    i = 0
                    while True:
                        try:
                            subname = winreg.EnumKey(key, i)
                            i += 1
                            yield hkey, parent_path, subname
                        except OSError:
                            break
            except OSError:
                continue
    
    @staticmethod
    def _wps_install_roots_from_registry():
        """从注册表读取 WPS Office 安装根目录（用于解析 splash 路径）。"""
        if sys.platform != "win32":
            return []
        import winreg
        roots = []
        key_specs = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Kingsoft\Office\6.0\Common"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Kingsoft\Office\6.0\Common"),
            (winreg.HKEY_CURRENT_USER, r"Software\Kingsoft\Office\6.0\Common"),
        ]
        for hkey, subkey in key_specs:
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as k:
                    for name in ("InstallRoot", "Path"):
                        try:
                            val, _ = winreg.QueryValueEx(k, name)
                            if isinstance(val, str) and val.strip():
                                roots.append(val.strip().rstrip("\\/"))
                                break
                        except OSError:
                            continue
            except OSError:
                continue
        
        for hkey, parent_path, subname in PathDetector._enum_uninstall_subkeys():
            try:
                with winreg.OpenKey(hkey, f"{parent_path}\\{subname}", 0, winreg.KEY_READ) as k:
                    try:
                        display, _ = winreg.QueryValueEx(k, "DisplayName")
                    except OSError:
                        continue
                    if not isinstance(display, str):
                        continue
                    dn = display.lower()
                    if "wps" not in dn:
                        continue
                    if not ("office" in dn or "kingsoft" in dn or "金山" in dn):
                        continue
                    try:
                        loc, _ = winreg.QueryValueEx(k, "InstallLocation")
                        if isinstance(loc, str) and loc.strip():
                            roots.append(loc.strip().rstrip("\\/"))
                    except OSError:
                        pass
            except OSError:
                continue
        
        out, seen = [], set()
        for r in roots:
            if not r or not os.path.exists(r):
                continue
            key = os.path.normcase(os.path.normpath(r))
            if key not in seen:
                seen.add(key)
                out.append(r)
        return out
    
    @staticmethod
    def _seewo_install_bases_from_registry():
        """从注册表读取希沃白板 EasiNote5 相关安装目录。"""
        if sys.platform != "win32":
            return []
        import winreg
        bases = []
        seewo_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Seewo\EasiNote5"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Seewo\EasiNote5"),
            (winreg.HKEY_CURRENT_USER, r"Software\Seewo\EasiNote5"),
        ]
        for hkey, subkey in seewo_keys:
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ) as k:
                    for name in ("InstallPath", "Path", "InstallLocation", "InstallDir", "RootDir"):
                        try:
                            val, _ = winreg.QueryValueEx(k, name)
                            if isinstance(val, str) and val.strip():
                                bases.append(val.strip().rstrip("\\/"))
                                break
                        except OSError:
                            continue
            except OSError:
                continue
        
        for hkey, parent_path, subname in PathDetector._enum_uninstall_subkeys():
            try:
                with winreg.OpenKey(hkey, f"{parent_path}\\{subname}", 0, winreg.KEY_READ) as k:
                    try:
                        display, _ = winreg.QueryValueEx(k, "DisplayName")
                    except OSError:
                        continue
                    if not isinstance(display, str):
                        continue
                    dn = display.lower()
                    if not (
                        "easinote" in dn
                        or "希沃白板" in dn
                        or ("希沃" in dn and "白板" in dn)
                        or ("seewo" in dn and "easi" in dn)
                    ):
                        continue
                    try:
                        loc, _ = winreg.QueryValueEx(k, "InstallLocation")
                        if isinstance(loc, str) and loc.strip():
                            bases.append(loc.strip().rstrip("\\/"))
                    except OSError:
                        pass
            except OSError:
                continue
        
        out, seen = [], set()
        for b in bases:
            if not b or not os.path.exists(b):
                continue
            key = os.path.normcase(os.path.normpath(b))
            if key not in seen:
                seen.add(key)
                out.append(b)
        return out
    
    @staticmethod
    def _collect_seewo_splash_from_install_bases(base_dirs):
        """在给定的 EasiNote 安装目录下查找 SplashScreen.png。"""
        paths = []
        for base_path in base_dirs:
            if not base_path or not os.path.exists(base_path):
                continue
            base_path = base_path.rstrip("\\/")
            patterns = [
                os.path.join(base_path, "EasiNote5*", "Main", "Assets", "SplashScreen.png"),
                os.path.join(base_path, "EasiNote5_*", "Main", "Resources", "Startup", "SplashScreen.png"),
            ]
            for pattern in patterns:
                paths.extend(glob.glob(pattern))
            for direct in (
                os.path.join(base_path, "Main", "Assets", "SplashScreen.png"),
                os.path.join(base_path, "Main", "Resources", "Startup", "SplashScreen.png"),
            ):
                if os.path.exists(direct):
                    paths.append(direct)
        return paths
    
    @staticmethod
    def detect_banner_paths():
        """检测Banner.png路径（支持多驱动器）"""
        paths = []
        
        # 遍历所有可用驱动器
        for drive_letter in PathDetector._get_available_drives():
            users_dir = f"{drive_letter}:\\Users"
            
            if not os.path.exists(users_dir):
                continue
            
            try:
                for user_folder in os.listdir(users_dir):
                    user_dir = os.path.join(users_dir, user_folder)
                    if not os.path.isdir(user_dir):
                        continue
                    
                    banner_path = os.path.join(
                        user_dir, 
                        "AppData\\Roaming\\Seewo\\EasiNote5\\Resources\\Banner\\Banner.png"
                    )
                    if os.path.exists(banner_path):
                        paths.append(banner_path)
            except (PermissionError, OSError):
                continue
        
        return paths
    
    @staticmethod
    def detect_splashscreen_paths():
        """检测SplashScreen.png路径（支持多驱动器）"""
        paths = []
        
        # 遍历所有可用驱动器
        for drive_letter in PathDetector._get_available_drives():
            # 检测 Program Files (x86)
            base_path_x86 = f"{drive_letter}:\\Program Files (x86)\\Seewo\\EasiNote5"
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
            base_path = f"{drive_letter}:\\Program Files\\Seewo\\EasiNote5"
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
        检测所有版本的希沃白板安装路径（支持多驱动器）
        
        Returns:
            list: 包含版本信息的字典列表
        """
        versions = []
        
        # 遍历所有可用驱动器
        for drive_letter in PathDetector._get_available_drives():
            # 检测 Program Files (x86) 和 Program Files
            base_paths = [
                f"{drive_letter}:\\Program Files (x86)\\Seewo\\EasiNote5",
                f"{drive_letter}:\\Program Files\\Seewo\\EasiNote5"
            ]
            
            for base_path in base_paths:
                if not os.path.exists(base_path):
                    continue
                
                try:
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
                except (PermissionError, OSError):
                    continue
        
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
        """检测所有可能的路径（优先使用注册表中的安装目录解析 SplashScreen，其次为原有扫描逻辑）。"""
        all_paths = []
        seen = set()

        def _add(path):
            if not path:
                return
            key = os.path.normcase(os.path.normpath(path))
            if key not in seen:
                seen.add(key)
                all_paths.append(path)

        if sys.platform == "win32":
            for p in PathDetector._collect_seewo_splash_from_install_bases(
                PathDetector._seewo_install_bases_from_registry()
            ):
                _add(p)
        for p in PathDetector.detect_banner_paths():
            _add(p)
        for p in PathDetector.detect_splashscreen_paths():
            _add(p)
        return all_paths
    
    @staticmethod
    def detect_wps_paths():
        r"""检测WPS Office启动图片路径（splash目录结构）
        
        返回splash目录的路径，如果找到splash目录，则返回该目录路径
        如果找不到splash目录，则返回空列表
        
        支持的路径格式：
        1. 用户目录：C:\Users\[用户名]\AppData\Local\Kingsoft\WPS Office\[版本号]\office6\mui\[语言]\resource\splash\
        2. Program Files：C:\Program Files\Kingsoft\WPS Office\office6\mui\[语言]\res\splash\
        3. Program Files (x86)：C:\Program Files (x86)\Kingsoft\WPS Office\office6\mui\[语言]\res\splash\
        
        优先从注册表（InstallRoot / 卸载项 InstallLocation）解析安装根目录并查找 splash；
        若未找到则回退到原有的用户目录与盘符扫描逻辑。
        """
        splash_dirs = []
        
        if sys.platform == "win32":
            splash_dirs.extend(
                PathDetector._collect_wps_splash_from_base_dirs(PathDetector._wps_install_roots_from_registry())
            )
        splash_dirs.extend(PathDetector._detect_wps_user_paths())
        splash_dirs.extend(PathDetector._detect_wps_program_files_paths())
        
        seen = set()
        unique = []
        for s in splash_dirs:
            k = os.path.normcase(os.path.normpath(s))
            if k not in seen:
                seen.add(k)
                unique.append(s)
        if unique:
            return [unique[0]]
        return []
    
    @staticmethod
    def _detect_wps_user_paths():
        r"""检测用户目录下的WPS路径
        
        路径格式：C:\Users\[用户名]\AppData\Local\Kingsoft\WPS Office\[版本号]\office6\mui\[语言]\resource\splash\
        """
        splash_dirs = []
        
        # 获取所有可能的用户目录
        # 尝试常见的盘符（C、D、E等）
        possible_drives = []
        for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            users_path = f"{drive_letter}:\\Users"
            if os.path.exists(users_path):
                possible_drives.append(drive_letter)
        
        # 如果没有找到Users目录，尝试使用环境变量
        if not possible_drives:
            userprofile = os.environ.get("USERPROFILE", "")
            if userprofile:
                # 从USERPROFILE提取盘符，如 C:\Users\Luminary -> C
                drive = os.path.splitdrive(userprofile)[0]
                if drive:
                    possible_drives.append(drive[0])  # 提取盘符字母
        
        # 优先检查当前用户目录
        userprofile = os.environ.get("USERPROFILE", "")
        if userprofile:
            current_user_splash = PathDetector._check_user_wps_path(userprofile)
            if current_user_splash:
                splash_dirs.append(current_user_splash)
                # 如果找到当前用户的路径，直接返回（优先使用当前用户的）
                return splash_dirs
        
        # 遍历所有可能的用户目录（检查其他用户）
        for drive_letter in possible_drives:
            users_dir = f"{drive_letter}:\\Users"
            if not os.path.exists(users_dir):
                continue
            
            # 遍历所有用户目录
            try:
                for user_name in os.listdir(users_dir):
                    user_dir = os.path.join(users_dir, user_name)
                    if not os.path.isdir(user_dir):
                        continue
                    
                    # 跳过已经检查过的当前用户目录
                    if user_dir == userprofile:
                        continue
                    
                    user_splash = PathDetector._check_user_wps_path(user_dir)
                    if user_splash:
                        splash_dirs.append(user_splash)
            except (PermissionError, OSError):
                continue
        
        return splash_dirs
    
    @staticmethod
    def _check_user_wps_path(user_dir):
        r"""检查指定用户目录下的WPS路径
        
        Args:
            user_dir: 用户目录路径，如 C:\Users\Luminary
            
        Returns:
            str: 找到的splash目录路径，如果未找到则返回None
        """
        # 构建WPS路径
        wps_base = os.path.join(user_dir, "AppData", "Local", "Kingsoft", "WPS Office")
        if not os.path.exists(wps_base):
            return None
        
        # 查找所有版本号目录
        try:
            for version_dir in os.listdir(wps_base):
                version_path = os.path.join(wps_base, version_dir)
                if not os.path.isdir(version_path):
                    continue
                
                # 检查office6目录
                office6_path = os.path.join(version_path, "office6")
                if not os.path.exists(office6_path):
                    continue
                
                # 检查mui目录
                mui_path = os.path.join(office6_path, "mui")
                if not os.path.exists(mui_path):
                    continue
                
                # 遍历所有语言目录
                try:
                    for lang_dir in os.listdir(mui_path):
                        lang_path = os.path.join(mui_path, lang_dir)
                        if not os.path.isdir(lang_path):
                            continue
                        
                        # 检查resource目录（注意是resource不是res）
                        resource_path = os.path.join(lang_path, "resource")
                        if not os.path.exists(resource_path):
                            continue
                        
                        # 检查splash目录
                        splash_dir = os.path.join(resource_path, "splash")
                        if os.path.isdir(splash_dir):
                            # 验证splash目录是否包含必要的文件
                            if PathDetector._validate_wps_splash_dir(splash_dir):
                                return splash_dir
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError):
            pass
        
        return None
    
    @staticmethod
    def _detect_wps_program_files_paths():
        r"""检测Program Files下的WPS路径
        
        路径格式：C:\Program Files\Kingsoft\WPS Office\office6\mui\[语言]\res\splash\
        或：C:\Program Files\Kingsoft\WPS Office\office6\mui\[语言]\resource\splash\
        """
        possible_base_paths = [
            "C:\\Program Files\\Kingsoft\\WPS Office",
            "C:\\Program Files (x86)\\Kingsoft\\WPS Office",
            "C:\\Program Files\\WPS Office",
            "C:\\Program Files (x86)\\WPS Office",
        ]
        
        for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            possible_base_paths.extend([
                f"{drive_letter}:\\Program Files\\Kingsoft\\WPS Office",
                f"{drive_letter}:\\Program Files (x86)\\Kingsoft\\WPS Office",
                f"{drive_letter}:\\Program Files\\WPS Office",
                f"{drive_letter}:\\Program Files (x86)\\WPS Office",
            ])
        
        return PathDetector._collect_wps_splash_from_base_dirs(possible_base_paths)
    
    @staticmethod
    def _validate_wps_splash_dir(splash_dir):
        """验证WPS splash目录是否包含必要的启动图文件
        
        Args:
            splash_dir: splash目录路径
            
        Returns:
            bool: 如果目录包含必要的文件则返回True
        """
        required_files = [
            "splash_default_bg.png",
            "splash_sup_default_bg.png",
            "splash_wps365_default_bg.png",
        ]
        
        hdpi_required_files = [
            "hdpi/splash_default_bg.png",
            "hdpi/splash_sup_default_bg.png",
            "hdpi/splash_wps365_default_bg.png",
        ]
        
        # 检查根目录下的文件
        for filename in required_files:
            file_path = os.path.join(splash_dir, filename)
            if not os.path.exists(file_path):
                return False
        
        # 检查hdpi目录下的文件
        hdpi_dir = os.path.join(splash_dir, "hdpi")
        if os.path.isdir(hdpi_dir):
            for filename in hdpi_required_files:
                file_path = os.path.join(splash_dir, filename)
                if not os.path.exists(file_path):
                    return False
        else:
            # 如果hdpi目录不存在，也认为无效
            return False
        
        return True
    
    @staticmethod
    def get_wps_splash_files(splash_dir):
        """获取WPS splash目录下的所有启动图文件路径
        
        Args:
            splash_dir: splash目录路径
            
        Returns:
            list: 包含6个文件路径的列表
        """
        if not splash_dir or not os.path.exists(splash_dir):
            return []
        
        files = []
        
        # 根目录下的3个文件
        root_files = [
            "splash_default_bg.png",
            "splash_sup_default_bg.png",
            "splash_wps365_default_bg.png",
        ]
        
        # hdpi目录下的3个文件
        hdpi_files = [
            "hdpi/splash_default_bg.png",
            "hdpi/splash_sup_default_bg.png",
            "hdpi/splash_wps365_default_bg.png",
        ]
        
        # 添加根目录文件
        for filename in root_files:
            file_path = os.path.join(splash_dir, filename)
            if os.path.exists(file_path):
                files.append(file_path)
        
        # 添加hdpi目录文件
        for filename in hdpi_files:
            file_path = os.path.join(splash_dir, filename)
            if os.path.exists(file_path):
                files.append(file_path)
        
        return files
    
    @staticmethod
    def detect_all_wps_paths():
        """检测所有WPS路径（用于用户选择）"""
        return PathDetector.detect_wps_paths()
    
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
    def manual_select_target_image(parent=None, app_type="seewo"):
        """
        手动选择目标图片
        
        Args:
            parent: 父窗口对象
            app_type: 应用类型，"seewo" 或 "wps"
            
        Returns:
            str: 选中的图片路径,如果取消则返回空字符串
        """
        if app_type == "wps":
            content = (
                "无法自动检测到WPS Office的启动图片目录。\n\n"
                "您可以手动选择splash目录。\n"
                "splash目录通常位于以下位置之一:\n\n"
                "1. 用户目录（最常见）:\n"
                "   C:\\Users\\[用户名]\\AppData\\Local\\Kingsoft\\WPS Office\\[版本号]\\office6\\mui\\[语言]\\resource\\splash\\\n"
                "   示例: C:\\Users\\Luminary\\AppData\\Local\\Kingsoft\\WPS Office\\12.1.0.21171\\office6\\mui\\zh_CN\\resource\\splash\\\n\n"
                "2. Program Files:\n"
                "   C:\\Program Files\\Kingsoft\\WPS Office\\office6\\mui\\[语言]\\res\\splash\\\n"
                "   或: C:\\Program Files\\Kingsoft\\WPS Office\\office6\\mui\\[语言]\\resource\\splash\\\n\n"
                "3. Program Files (x86):\n"
                "   C:\\Program Files (x86)\\Kingsoft\\WPS Office\\office6\\mui\\[语言]\\res\\splash\\\n\n"
                "splash目录应包含以下文件:\n"
                "- splash_default_bg.png\n"
                "- splash_sup_default_bg.png\n"
                "- splash_wps365_default_bg.png\n"
                "- hdpi\\splash_default_bg.png\n"
                "- hdpi\\splash_sup_default_bg.png\n"
                "- hdpi\\splash_wps365_default_bg.png\n\n"
                "是否现在手动选择splash目录?"
            )
        else:
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
        title = "手动选择目标图片" if app_type == "seewo" else "手动选择WPS启动图片"
        w = MessageBox(title, content, parent)
        if not w.exec():
            return ""
        
        # 打开文件选择对话框
        dialog_title = "选择WPS Office启动图片" if app_type == "wps" else "选择希沃白板启动图片"
        file_dialog = QFileDialog(parent, dialog_title)
        file_dialog.setNameFilter("PNG图片 (*.png);;所有文件 (*.*)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        # 设置初始目录为常见路径
        if app_type == "wps":
            initial_dir = "C:\\Program Files\\Kingsoft\\WPS Office"
            if not os.path.exists(initial_dir):
                initial_dir = "C:\\Program Files (x86)\\Kingsoft\\WPS Office"
            if not os.path.exists(initial_dir):
                initial_dir = "C:\\Program Files\\WPS Office"
            if not os.path.exists(initial_dir):
                initial_dir = "C:\\"
        else:
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
