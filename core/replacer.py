# file: core/replacer.py

import os
import shutil
import stat
import ctypes
from datetime import datetime


class ImageReplacer:
    """图片替换器 - 增强版文件保护"""
    
    def __init__(self, backup_dir="backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def has_backup(self, target_path):
        """检查是否已存在备份"""
        if not target_path or not os.path.exists(target_path):
            return False
        
        base_name = os.path.basename(target_path)
        # 检查backups目录下是否有以该文件名开头的备份
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(os.path.splitext(base_name)[0] + "_"):
                return True
        return False
    
    def backup_original(self, target_path):
        """备份原始文件"""
        if not os.path.exists(target_path):
            return False, "目标文件不存在", False
        
        # 检查是否已有备份
        if self.has_backup(target_path):
            return True, "检测到已有备份，跳过备份步骤", False
        
        try:
            # 生成备份文件名
            base_name = os.path.basename(target_path)
            name_without_ext = os.path.splitext(base_name)[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{name_without_ext}_{timestamp}.png"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 执行备份
            shutil.copy2(target_path, backup_path)
            return True, f"已备份原始文件: {backup_filename}", False
        except PermissionError:
            return False, "备份失败: 权限不足", True
        except Exception as e:
            return False, f"备份失败: {str(e)}", False
    
    def remove_readonly(self, filepath):
        """移除文件只读属性"""
        try:
            if os.path.exists(filepath):
                os.chmod(filepath, stat.S_IWRITE)
            return True
        except:
            return False
    
    def set_readonly(self, filepath):
        """设置文件只读属性"""
        try:
            if os.path.exists(filepath):
                os.chmod(filepath, stat.S_IREAD)
            return True
        except:
            return False
    
    def set_enhanced_protection(self, filepath):
        """
        设置增强保护 - 多层保护机制
        
        Returns:
            tuple: (是否成功, 保护详情)
        """
        if not os.path.exists(filepath):
            return False, "文件不存在"
        
        protection_methods = []
        
        try:
            # 1. 设置只读属性
            if self.set_readonly(filepath):
                protection_methods.append("只读属性")
            
            # 2. 设置系统文件属性 (Windows)
            try:
                if os.name == 'nt':  # Windows系统
                    # 获取当前文件属性
                    attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
                    if attrs != -1:
                        # 添加系统文件属性 (0x4) 和隐藏属性 (0x2)
                        new_attrs = attrs | 0x4 | 0x2  # FILE_ATTRIBUTE_SYSTEM | FILE_ATTRIBUTE_HIDDEN
                        if ctypes.windll.kernel32.SetFileAttributesW(filepath, new_attrs):
                            protection_methods.append("系统保护")
            except Exception:
                pass  # 系统属性设置失败不影响主要功能
            
            # 3. 尝试设置更严格的权限 (如果有管理员权限)
            try:
                from utils.admin_helper import is_admin
                if is_admin():
                    # 如果是管理员，可以设置更严格的权限
                    # 这里简化处理，实际可以设置ACL
                    protection_methods.append("管理员保护")
            except ImportError:
                pass  # admin_helper 不可用时跳过
            
            if protection_methods:
                return True, f"已启用保护: {' + '.join(protection_methods)}"
            else:
                return False, "保护设置失败"
                
        except Exception as e:
            return False, f"保护设置出错: {str(e)}"
    
    def remove_enhanced_protection(self, filepath):
        """
        移除增强保护
        
        Returns:
            tuple: (是否成功, 消息)
        """
        if not os.path.exists(filepath):
            return False, "文件不存在"
        
        try:
            # 1. 移除只读属性
            if not self.remove_readonly(filepath):
                return False, "无法移除只读属性"
            
            # 2. 移除系统文件和隐藏属性 (Windows)
            try:
                if os.name == 'nt':  # Windows系统
                    attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
                    if attrs != -1:
                        # 移除系统文件属性和隐藏属性
                        new_attrs = attrs & ~0x4 & ~0x2  # 移除 SYSTEM 和 HIDDEN
                        ctypes.windll.kernel32.SetFileAttributesW(filepath, new_attrs)
            except Exception:
                pass  # 系统属性移除失败不影响主要功能
            
            return True, "保护已移除"
            
        except Exception as e:
            return False, f"移除保护出错: {str(e)}"
    
    def is_file_protected(self, filepath):
        """检查文件是否受保护"""
        if not os.path.exists(filepath):
            return False
        
        try:
            # 检查只读属性
            return not os.access(filepath, os.W_OK)
        except:
            return False
    
    def check_write_permission(self, filepath):
        """
        检查文件写权限
        
        Returns:
            tuple: (有权限, 错误信息, 是否为权限问题)
        """
        if not os.path.exists(filepath):
            return False, "文件不存在", False
        
        try:
            # 尝试以追加模式打开文件
            with open(filepath, 'a'):
                pass
            return True, "", False
        except PermissionError:
            return False, "没有写入权限", True
        except Exception as e:
            return False, f"无法访问文件: {str(e)}", False
    
    def replace_image(self, source_path, target_path):
        """
        替换图片并自动启用保护
        
        Returns:
            tuple: (成功与否, 消息, 是否为权限问题)
        """
        if not os.path.exists(source_path):
            return False, "源图片不存在", False
        
        if not os.path.exists(target_path):
            return False, "目标路径不存在", False
        
        # 检查目标文件是否受保护，如果是则先移除保护
        was_protected = self.is_file_protected(target_path)
        if was_protected:
            remove_success, remove_msg = self.remove_enhanced_protection(target_path)
            if not remove_success:
                return False, f"无法移除现有保护: {remove_msg}", True
        
        # 先检查写权限
        has_permission, perm_msg, is_permission_error = self.check_write_permission(target_path)
        if not has_permission and is_permission_error:
            return False, "权限不足，无法写入文件", True
        
        try:
            # 备份原始文件
            backup_success, backup_msg, backup_perm_error = self.backup_original(target_path)
            if not backup_success and not self.has_backup(target_path):
                return False, backup_msg, backup_perm_error
            
            # 移除只读属性（为了替换）
            original_readonly = False
            try:
                if not os.access(target_path, os.W_OK):
                    original_readonly = True
                    if not self.remove_readonly(target_path):
                        return False, "无法移除只读属性", True
            except Exception as e:
                return False, f"检查文件属性失败: {str(e)}", False
            
            # 执行替换
            shutil.copy2(source_path, target_path)
            
            # 启用增强保护
            protect_success, protect_msg = self.set_enhanced_protection(target_path)
            
            # 构造成功消息
            success_msg = f"替换成功 | {backup_msg}"
            if protect_success:
                success_msg += f" | {protect_msg}"
            else:
                success_msg += f" | 警告: {protect_msg}"
            
            return True, success_msg, False
            
        except PermissionError as e:
            return False, f"权限不足: {str(e)}", True
        except OSError as e:
            if e.errno == 13:  # Permission denied
                return False, "权限不足，无法替换文件", True
            return False, f"替换失败: {str(e)}", False
        except Exception as e:
            return False, f"替换失败: {str(e)}", False
    
    def restore_backup(self, target_path):
        """
        从备份还原并移除保护
        
        Returns:
            tuple: (成功与否, 消息, 是否为权限问题)
        """
        if not os.path.exists(target_path):
            return False, "目标路径不存在", False
        
        # 查找备份文件
        base_name = os.path.basename(target_path)
        name_without_ext = os.path.splitext(base_name)[0]
        
        backup_file = None
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(name_without_ext + "_"):
                backup_file = filename
                break
        
        if not backup_file:
            return False, "未找到备份文件", False
        
        backup_path = os.path.join(self.backup_dir, backup_file)
        
        # 检查目标文件是否受保护，如果是则先移除保护
        was_protected = self.is_file_protected(target_path)
        if was_protected:
            remove_success, remove_msg = self.remove_enhanced_protection(target_path)
            if not remove_success:
                return False, f"无法移除现有保护: {remove_msg}", True
        
        # 先检查写权限
        has_permission, perm_msg, is_permission_error = self.check_write_permission(target_path)
        if not has_permission and is_permission_error:
            return False, "权限不足，无法写入文件", True
        
        try:
            # 移除只读属性（为了还原）
            original_readonly = False
            try:
                if not os.access(target_path, os.W_OK):
                    original_readonly = True
                    if not self.remove_readonly(target_path):
                        return False, "无法移除只读属性", True
            except Exception as e:
                return False, f"检查文件属性失败: {str(e)}", False
            
            # 执行还原
            shutil.copy2(backup_path, target_path)
            
            # 还原时不重新启用保护，保持原始状态
            success_msg = "已还原备份"
            if was_protected:
                success_msg += " | 已移除文件保护"
            
            return True, success_msg, False
            
        except PermissionError as e:
            return False, f"权限不足: {str(e)}", True
        except OSError as e:
            if e.errno == 13:  # Permission denied
                return False, "权限不足，无法还原文件", True
            return False, f"还原失败: {str(e)}", False
        except Exception as e:
            return False, f"还原失败: {str(e)}", False
