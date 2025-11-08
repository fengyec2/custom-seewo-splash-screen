import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from qfluentwidgets import FlowLayout, CardWidget, SingleDirectionScrollArea, CaptionLabel


class ImageCard(CardWidget):
    """图片卡片组件"""
    
    imageClicked = pyqtSignal(dict)  # 改名为 imageClicked，避免与父类的 clicked 冲突
    
    def __init__(self, img_info: dict, parent=None):
        super().__init__(parent)
        self.img_info = img_info
        self.is_selected = False
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 设置卡片固定大小
        self.setFixedSize(160, 180)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 图片标签
        self.image_label = CaptionLabel()
        self.image_label.setFixedSize(140, 140)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        
        # 加载图片
        if os.path.exists(self.img_info["path"]):
            pixmap = QPixmap(self.img_info["path"])
            if not pixmap.isNull():
                # 获取设备像素比例来支持高分屏
                from PyQt6.QtWidgets import QApplication
                dpr = QApplication.primaryScreen().devicePixelRatio()
                
                # 计算实际缩放尺寸
                target_size = int(140 * dpr)
                
                scaled_pixmap = pixmap.scaled(
                    target_size, target_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # 设置设备像素比例
                scaled_pixmap.setDevicePixelRatio(dpr)
                
                self.image_label.setPixmap(scaled_pixmap)
        
        # 文字标签
        self.text_label = CaptionLabel(self.img_info["display_name"])
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("font-size: 12px;")
        
        layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 设置工具提示
        img_type = '预设' if self.img_info['type'] == 'preset' else '自定义'
        self.setToolTip(f"类型: {img_type}\n文件名: {self.img_info['filename']}")
        
        # 设置鼠标光标
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 连接父类的 clicked 信号到我们的处理函数
        self.clicked.connect(self._on_clicked)
        
        # 更新样式
        self._update_style()
    
    def _on_clicked(self):
        """处理父类的 clicked 信号"""
        self.imageClicked.emit(self.img_info)
    
    def _update_style(self):
        """更新样式"""
        if self.is_selected:
            self.setStyleSheet("""
                ImageCard {
                    background-color: rgba(0, 120, 212, 0.1);
                    border: 2px solid rgb(0, 120, 212);
                    border-radius: 8px;
                }
                ImageCard:hover {
                    background-color: rgba(0, 120, 212, 0.15);
                }
            """)
        else:
            self.setStyleSheet("""
                ImageCard {
                    background-color: transparent;
                    border: 2px solid transparent;
                    border-radius: 8px;
                }
                ImageCard:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                    border: 2px solid rgba(0, 0, 0, 0.1);
                }
            """)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.is_selected = selected
        self._update_style()


class ImageListWidget(QWidget):
    """图片列表组件 - 使用带滚动的 FlowLayout"""
    
    imageSelected = pyqtSignal(dict)  # 发出选中图片信息的信号
    imagesDropped = pyqtSignal(list)  # 发出拖放的文件路径列表信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_cards = []  # 存储所有图片卡片
        self.selected_card = None  # 当前选中的卡片
        self._init_ui()
        self._setup_drag_drop()
    
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建滚动区域
        self.scroll_area = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        
        # 创建内容容器
        self.content_widget = QWidget()
        
        # 创建 FlowLayout
        self.flow_layout = FlowLayout(self.content_widget, needAni=True)
        
        # 自定义动画
        from PyQt6.QtCore import QEasingCurve
        self.flow_layout.setAnimation(250, QEasingCurve.Type.OutQuad)
        
        # 设置间距
        self.flow_layout.setContentsMargins(20, 20, 20, 20)
        self.flow_layout.setVerticalSpacing(15)
        self.flow_layout.setHorizontalSpacing(15)
        
        # 设置内容控件的样式和大小策略
        self.content_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding
        )
        
        # 将内容控件设置到滚动区域
        self.scroll_area.setWidget(self.content_widget)
        
        # 设置滚动区域属性
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 启用透明背景
        self.scroll_area.enableTransparentBackground()
        
        # 添加到主布局
        main_layout.addWidget(self.scroll_area)
        
        # 设置最小尺寸
        self.setMinimumHeight(240)
        self.setMinimumWidth(426)
        
        # 设置尺寸策略
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
    def _setup_drag_drop(self):
        """设置拖放功能"""
        self.setAcceptDrops(True)
        # 也要为滚动区域和内容控件启用拖放
        self.scroll_area.setAcceptDrops(True)
        self.content_widget.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            has_png = any(
                url.toLocalFile().lower().endswith('.png') 
                for url in urls if url.isLocalFile()
            )
            
            if has_png:
                event.accept()
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.accept()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = []
            ignored_files = []
            
            # 过滤出PNG文件
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.png'):
                        file_paths.append(file_path)
                    else:
                        ignored_files.append(os.path.basename(file_path))
            
            # 发出信号
            if file_paths or ignored_files:
                self.imagesDropped.emit([file_paths, ignored_files])
            
            event.accept()
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def load_images(self, preset_images: list, custom_images: list):
        """加载图片列表
        
        Args:
            preset_images: 预设图片列表
            custom_images: 自定义图片列表
        """
        # 清空现有卡片
        self._clear_layout()
        self.image_cards.clear()
        self.selected_card = None
        
        all_images = preset_images + custom_images
        
        for img_info in all_images:
            card = ImageCard(img_info, self.content_widget)
            card.imageClicked.connect(self._on_card_clicked)
            self.image_cards.append(card)
            self.flow_layout.addWidget(card)
        
        # 更新内容控件的高度以适应所有卡片
        self._update_content_height()
    
    def _update_content_height(self):
        """更新内容控件的高度"""
        # 让FlowLayout重新计算布局
        self.content_widget.updateGeometry()
        
        # 获取FlowLayout建议的最小高度
        min_height = self.flow_layout.minimumSize().height()
        if min_height > 0:
            self.content_widget.setMinimumHeight(min_height)
    
    def _clear_layout(self):
        """清空布局"""
        # FlowLayout 的 takeAt 直接返回 widget，不是 QLayoutItem
        while self.flow_layout.count():
            widget = self.flow_layout.takeAt(0)
            if widget:
                widget.deleteLater()
    
    def _on_card_clicked(self, img_info: dict):
        """卡片点击事件处理"""
        # 取消之前选中的卡片
        if self.selected_card:
            self.selected_card.set_selected(False)
        
        # 设置新选中的卡片
        for card in self.image_cards:
            if card.img_info == img_info:
                card.set_selected(True)
                self.selected_card = card
                break
        
        # 发出信号
        self.imageSelected.emit(img_info)
    
    def get_selected_image_info(self):
        """获取选中的图片信息
        
        Returns:
            dict or None: 选中的图片信息字典,未选中返回None
        """
        return self.selected_card.img_info if self.selected_card else None
    
    def select_image_by_filename(self, filename: str):
        """根据文件名选中图片
        
        Args:
            filename: 要选中的图片文件名
        """
        for card in self.image_cards:
            if card.img_info["filename"] == filename:
                self._on_card_clicked(card.img_info)
                break
    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 延迟更新内容高度，确保FlowLayout已经重新布局
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(10, self._update_content_height)
