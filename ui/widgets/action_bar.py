from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal
from qfluentwidgets import PushButton, PrimaryPushButton, FluentIcon as FIF


class ActionBar(QWidget):
    """操作按钮栏组件"""
    
    # 定义信号
    importClicked = pyqtSignal()
    renameClicked = pyqtSignal()
    deleteClicked = pyqtSignal()
    replaceClicked = pyqtSignal()
    restoreClicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建按钮
        self.import_btn = PushButton(FIF.ADD, "导入图片")
        self.rename_btn = PushButton(FIF.EDIT, "重命名")
        self.delete_btn = PushButton(FIF.DELETE, "删除")
        self.replace_btn = PrimaryPushButton(FIF.UPDATE, "替换启动图片")
        self.restore_btn = PushButton(FIF.SYNC, "从备份还原")
        
        # 添加到布局
        layout.addWidget(self.import_btn)
        layout.addWidget(self.rename_btn)
        layout.addWidget(self.delete_btn)
        layout.addStretch(1)
        layout.addWidget(self.restore_btn)
        layout.addWidget(self.replace_btn)
    
    def _connect_signals(self):
        """连接信号"""
        self.import_btn.clicked.connect(self.importClicked.emit)
        self.rename_btn.clicked.connect(self.renameClicked.emit)
        self.delete_btn.clicked.connect(self.deleteClicked.emit)
        self.replace_btn.clicked.connect(self.replaceClicked.emit)
        self.restore_btn.clicked.connect(self.restoreClicked.emit)
    
    def set_rename_delete_enabled(self, enabled: bool):
        """设置重命名和删除按钮的启用状态
        
        Args:
            enabled: True启用,False禁用
        """
        self.rename_btn.setEnabled(enabled)
        self.delete_btn.setEnabled(enabled)
