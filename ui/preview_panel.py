"""
FPGA ISP Tuner - 图像预览面板（预留）
用于显示 FPGA 传输的图像数据
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage


class PreviewPanel(QWidget):
    """
    图像预览面板（预留）

    Signals:
        image_data_received: 图像数据接收（预留）
    """

    # Qt Signals（预留）
    image_data_received = pyqtSignal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_image = None

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = QLabel("<h3>图像预览</h3>")
        layout.addWidget(title_label)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 图像显示标签
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setMinimumSize(320, 240)

        # 占位提示
        self._image_label.setStyleSheet("""
            QLabel {
                background-color: #2D2D2D;
                border: 1px dashed #5D5D5D;
                color: #808080;
            }
        """)
        self._set_placeholder_text()

        scroll_area.setWidget(self._image_label)
        layout.addWidget(scroll_area)

        # 尺寸标注
        size_label = QLabel("尺寸: --")
        size_label.setStyleSheet("color: #808080; font-size: 11px;")
        layout.addWidget(size_label)
        self._size_label = size_label

    def _set_placeholder_text(self):
        """设置占位符文本"""
        self._image_label.setText(
            "\n\n\n\n\n"
            "图像预览区域（预留）\n"
            "\n"
            "等待 FPGA 传输图像数据...\n"
            "\n\n\n\n"
        )

    # ==================== Public Methods（预留） ====================

    def set_image(self, image_data: bytes, width: int = 640, height: int = 480, format: str = "RGB888"):
        """
        设置显示图像（预留，暂不实现具体逻辑）

        Args:
            image_data: 原始图像数据
            width: 图像宽度
            height: 图像高度
            format: 图像格式（"RGB888", "BGR888", "YUV422", "Bayer"）
        """
        # TODO: 图像解码与显示逻辑
        # 目前仅作占位符保留
        self._image_label.setText(f"收到图像数据: {len(image_data)} bytes\n{width}x{height} {format}")
        self._size_label.setText(f"尺寸: {width} x {height}")

    def clear_image(self):
        """清除图像显示"""
        self._image_label.clear()
        self._set_placeholder_text()
        self._size_label.setText("尺寸: --")

    def get_current_image(self):
        """
        获取当前图像（预留）

        Returns:
            QPixmap: 当前图像
        """
        return self._current_image

    def save_image(self, filepath: str) -> bool:
        """
        保存当前图像到文件（预留）

        Args:
            filepath: 文件路径

        Returns:
            bool: 是否成功
        """
        if self._current_image:
            return self._current_image.save(filepath)
        return False
