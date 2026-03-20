"""
FPGA ISP Tuner - 直方图面板（预留）
用于显示 RGB 直方图
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal


class HistogramPanel(QWidget):
    """
    直方图面板（预留）

    Signals:
        histogram_data_received: 直方图数据接收（预留）
    """

    # Qt Signals（预留）
    histogram_data_received = pyqtSignal(list, list, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = QLabel("<h3>RGB 直方图</h3>")
        layout.addWidget(title_label)

        # 直方图显示区域
        histo_layout = QHBoxLayout()

        # R 通道
        r_container = QWidget()
        r_layout = QVBoxLayout(r_container)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_label = QLabel("R")
        r_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_label.setStyleSheet("color: #FF4444; font-weight: bold;")
        r_layout.addWidget(r_label)
        self._r_histogram = QLabel()
        self._r_histogram.setMinimumSize(100, 80)
        self._r_histogram.setStyleSheet("""
            background-color: #2D2D2D;
            border: 1px solid #3C3C3C;
        """)
        self._set_placeholder_histogram(self._r_histogram, "#FF4444")
        r_layout.addWidget(self._r_histogram)
        histo_layout.addWidget(r_container)

        # G 通道
        g_container = QWidget()
        g_layout = QVBoxLayout(g_container)
        g_layout.setContentsMargins(0, 0, 0, 0)
        g_label = QLabel("G")
        g_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        g_label.setStyleSheet("color: #44FF44; font-weight: bold;")
        g_layout.addWidget(g_label)
        self._g_histogram = QLabel()
        self._g_histogram.setMinimumSize(100, 80)
        self._g_histogram.setStyleSheet("""
            background-color: #2D2D2D;
            border: 1px solid #3C3C3C;
        """)
        self._set_placeholder_histogram(self._g_histogram, "#44FF44")
        g_layout.addWidget(self._g_histogram)
        histo_layout.addWidget(g_container)

        # B 通道
        b_container = QWidget()
        b_layout = QVBoxLayout(b_container)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_label = QLabel("B")
        b_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        b_label.setStyleSheet("color: #4444FF; font-weight: bold;")
        b_layout.addWidget(b_label)
        self._b_histogram = QLabel()
        self._b_histogram.setMinimumSize(100, 80)
        self._b_histogram.setStyleSheet("""
            background-color: #2D2D2D;
            border: 1px solid #3C3C3C;
        """)
        self._set_placeholder_histogram(self._b_histogram, "#4444FF")
        b_layout.addWidget(self._b_histogram)
        histo_layout.addWidget(b_container)

        layout.addLayout(histo_layout)

        # 提示标签
        hint_label = QLabel("RGB 直方图（预留）")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #808080; font-size: 11px;")
        layout.addWidget(hint_label)

    def _set_placeholder_histogram(self, label: QLabel, color: str):
        """
        设置占位符直方图

        Args:
            label: 标签控件
            color: 颜色字符串
        """
        # 生成简单的占位直方图文本
        placeholder = "\n".join(["█" * 20 for _ in range(4)])
        label.setText(f'<span style="color: {color}; font-family: monospace; font-size: 6px;">{placeholder}</span>')
        label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

    # ==================== Public Methods（预留） ====================

    def update_histogram(self, r_data: list, g_data: list, b_data: list):
        """
        更新直方图显示（预留，暂不实现具体逻辑）

        Args:
            r_data: R 通道直方图数据 (256 bins)
            g_data: G 通道直方图数据 (256 bins)
            b_data: B 通道直方图数据 (256 bins)
        """
        # TODO: 使用 QCustomPlot 或自绘实现直方图
        # 目前仅作占位符保留
        self._r_histogram.setText("R 通道")
        self._g_histogram.setText("G 通道")
        self._b_histogram.setText("B 通道")

    def clear_histogram(self):
        """清除直方图显示"""
        self._set_placeholder_histogram(self._r_histogram, "#FF4444")
        self._set_placeholder_histogram(self._g_histogram, "#44FF44")
        self._set_placeholder_histogram(self._b_histogram, "#4444FF")
