"""设置界面控制器 - 处理业务逻辑"""

import webbrowser
import os
from qfluentwidgets import Theme, setTheme, setThemeColor, qconfig

from core.config_manager import ConfigManager
from core.file_protector import FileProtector
from core.app_info import get_repository
from utils.system_theme import get_system_theme_color
from ui.dialogs import MessageHelper


class SettingsController:
    """设置控制器 - 负责处理设置相关的业务逻辑"""
    
    def __init__(self, parent_window=None):
        self.parent_window = parent_window
        self.config_manager = ConfigManager()
        self.file_protector = FileProtector()
        self._is_applying_saved_settings = False
    
    # ==================== 配置加载 ====================
    
    def load_saved_settings(self):
        """加载保存的设置"""
        return {
            'auto_detect': self.config_manager.get_auto_detect_on_startup(),
            'mica_enabled': self._get_mica_effect(),
            'file_protection': self.config_manager.get_file_protection_enabled()
        }
    
    def _get_mica_effect(self):
        """获取云母效果设置"""
        try:
            return self.config_manager.get_mica_effect()
        except AttributeError:
            return False
    
    # ==================== 主题管理 ====================
    
    def handle_theme_changed(self, theme_item):
        """处理主题切换"""
        selected_theme = theme_item.value
        
        # 主题映射
        theme_config_map = {
            Theme.LIGHT: ("浅色", "light"),
            Theme.DARK: ("深色", "dark"),
            Theme.AUTO: ("跟随系统设置", "auto")
        }
        
        theme_name, config_value = theme_config_map.get(selected_theme, ("未知", "auto"))
        
        # 保存到配置
        self.config_manager.set_theme_mode(config_value)
        
        # 显示成功消息
        if self.parent_window:
            MessageHelper.show_success(
                self.parent_window,
                f"已切换到{theme_name}模式",
                2000
            )
    
    def apply_saved_theme(self):
        """应用保存的主题设置"""
        self._is_applying_saved_settings = True
        
        try:
            # 应用主题模式
            theme_mode = self.config_manager.get_theme_mode()
            theme_map = {
                "light": Theme.LIGHT,
                "dark": Theme.DARK,
                "auto": Theme.AUTO
            }
            saved_theme = theme_map.get(theme_mode, Theme.AUTO)
            setTheme(saved_theme)
            
            # 应用系统主题色
            system_color = get_system_theme_color()
            setThemeColor(system_color)
            
            return saved_theme
        finally:
            self._is_applying_saved_settings = False
    
    # ==================== 云母效果管理 ====================
    
    def handle_mica_effect_changed(self, enabled):
        """处理云母效果切换"""
        # 保存到配置
        try:
            self.config_manager.set_mica_effect(enabled)
        except AttributeError:
            pass
        
        # 应用到主窗口
        if self.parent_window and hasattr(self.parent_window, 'setMicaEffectEnabled'):
            self.parent_window.setMicaEffectEnabled(enabled)
        
        # 显示消息（仅在用户主动操作时）
        if not self._is_applying_saved_settings:
            status = "已启用" if enabled else "已禁用"
            if self.parent_window:
                MessageHelper.show_success(
                    self.parent_window,
                    f"云母效果{status}",
                    2000
                )
    
    # ==================== 自动检测管理 ====================
    
    def handle_auto_detect_changed(self, enabled):
        """处理自动检测设置变更"""
        self.config_manager.set_auto_detect_on_startup(enabled)
    
    # ==================== 文件保护管理 ====================
    
    def handle_file_protection_changed(self, enabled):
        """处理文件保护开关变更"""
        # 保存到配置
        self.config_manager.set_file_protection_enabled(enabled)
        
        # 显示消息（仅在用户主动操作时）
        if not self._is_applying_saved_settings:
            status = "已启用" if enabled else "已禁用"
            if self.parent_window:
                MessageHelper.show_success(
                    self.parent_window,
                    f"文件保护{status}",
                    2000
                )
    
    def handle_remove_all_protection(self):
        """处理移除所有保护操作"""
        try:
            # 获取所有受保护的文件
            protected_files = self._get_all_protected_files()
            
            if not protected_files:
                MessageHelper.show_success(
                    self.parent_window,
                    "未发现受保护的文件",
                    2000
                )
                return
            
            # 移除保护
            success_count, failed_count = self._remove_protections(protected_files)
            
            # 显示结果
            self._show_removal_result(success_count, failed_count, len(protected_files))
            
        except Exception as e:
            MessageHelper.show_error(
                self.parent_window,
                f"移除保护时出现错误: {str(e)}",
                3000
            )
    
    def _get_all_protected_files(self):
        """获取所有受保护的文件路径"""
        protected_files = []
        
        # 从配置中读取已记录的受保护文件
        try:
            recorded = self.config_manager.get_protected_files()
            for p in recorded:
                if p and os.path.exists(p):
                    protected_files.append(p)
        except Exception:
            pass
        
        # 检查希沃白板路径
        protected_files.extend(self._check_path_for_protected_files("home"))
        
        # 检查WPS路径
        protected_files.extend(self._check_path_for_protected_files("wps"))
        
        return protected_files
    
    def _check_path_for_protected_files(self, path_type):
        """检查指定路径下的受保护文件"""
        protected = []
        target_path = self.config_manager.get_target_path(path_type)
        
        if not target_path:
            return protected
        
        splash_files = ["splash.png", "splash_screen.png", "startup.png"]
        
        for filename in splash_files:
            file_path = f"{target_path}\\{filename}"
            if os.path.exists(file_path) and self.file_protector.is_file_protected(file_path):
                if file_path not in protected:
                    protected.append(file_path)
        
        return protected
    
    def _remove_protections(self, protected_files):
        """移除文件保护"""
        success_count = 0
        failed_count = 0
        
        for file_path in protected_files:
            success, msg = self.file_protector.unprotect_file(file_path)
            if success:
                success_count += 1
                try:
                    self.config_manager.remove_protected_file(file_path)
                except Exception:
                    pass
            else:
                failed_count += 1
        
        return success_count, failed_count
    
    def _show_removal_result(self, success_count, failed_count, total_count):
        """显示移除保护的结果"""
        if success_count > 0 and failed_count == 0:
            MessageHelper.show_success(
                self.parent_window,
                f"成功移除 {success_count} 个文件的保护",
                3000
            )
        elif success_count > 0:
            MessageHelper.show_warning(
                self.parent_window,
                f"成功移除 {success_count} 个文件的保护，{failed_count} 个失败",
                3000
            )
        else:
            MessageHelper.show_error(
                self.parent_window,
                f"移除保护失败：所有 {total_count} 个文件都无法处理",
                3000
            )
    
    # ==================== 关于信息 ====================
    
    def handle_about_clicked(self):
        """处理关于按钮点击"""
        webbrowser.open(get_repository())
    
    # ==================== 启动时应用设置 ====================
    
    def apply_all_saved_settings(self):
        """应用所有保存的设置（启动时调用）"""
        self._is_applying_saved_settings = True
        
        try:
            # 应用主题
            self.apply_saved_theme()
            
            # 返回需要应用到UI的设置
            return self.load_saved_settings()
        finally:
            self._is_applying_saved_settings = False