"""权限处理控制器"""

from PyQt5.QtWidgets import QWidget
from qfluentwidgets import MessageBox
from utils.admin_helper import is_admin, request_admin_and_exit


class PermissionController:
    """权限处理控制器"""
    
    @staticmethod
    def handle_permission_error(parent: QWidget, error_message: str) -> bool:
        """处理权限错误
        
        Args:
            parent: 父窗口
            error_message: 错误消息
            
        Returns:
            是否成功请求权限
        """
        if is_admin():
            # 已经是管理员权限了
            w = MessageBox(
                "权限不足",
                f"{error_message}\n\n"
                "即使以管理员身份运行，仍然无法访问该文件。\n\n"
                "可能的原因：\n"
                "• 文件正在被希沃白板或其他程序使用\n"
                "• 文件被系统或杀毒软件保护\n"
                "• 磁盘权限配置问题\n\n"
                "建议：\n"
                "• 完全关闭希沃白板后重试\n"
                "• 检查文件是否被杀毒软件锁定\n"
                "• 尝试重启电脑后再操作",
                parent
            )
            w.exec()
            return False
        else:
            # 询问是否以管理员身份重启
            w = MessageBox(
                "需要管理员权限",
                f"{error_message}\n\n"
                "此操作需要管理员权限才能完成。\n\n"
                "是否以管理员身份重新启动程序？\n\n"
                "注意：程序将会关闭并重新启动。",
                parent
            )
            
            if w.exec():
                if request_admin_and_exit():
                    return True
                else:
                    w = MessageBox(
                        "启动失败",
                        "无法以管理员身份重新启动程序。\n\n"
                        "请尝试以下方法：\n"
                        "• 右键点击程序图标\n"
                        "• 选择以管理员身份运行\n\n"
                        "或者关闭希沃白板后再试。",
                        parent
                    )
                    w.exec()
            
            return False
