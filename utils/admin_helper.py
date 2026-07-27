# file: utils/admin_helper.py

import ctypes
import sys
import os


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _run_as_admin():
    """请求以管理员权限重启程序（私有函数）"""
    try:
        if sys.argv[0].endswith('.py'):
            # 如果是Python脚本
            script_path = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable,
                f'"{script_path}" {params}',
                None, 
                1
            )
        else:
            # 如果是打包后的exe
            exe_path = sys.executable
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                exe_path,
                params,
                None,
                1
            )
        return True
    except Exception as e:
        print(f"请求管理员权限失败: {e}")
        return False


def request_admin_and_exit():
    """请求管理员权限并退出当前进程"""
    if _run_as_admin():
        sys.exit(0)
    return False
