"""
FPGA ISP Tuner - 工具栏
工具栏按钮
"""

from PyQt6.QtWidgets import QToolBar, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction


class Toolbar(QToolBar):
    """
    工具栏 - 常用操作按钮

    Signals:
        connect_clicked: 连接按钮点击
        disconnect_clicked: 断开按钮点击
        import_clicked: 导入配置按钮点击
        export_clicked: 导出配置按钮点击
        refresh_clicked: 刷新按钮点击
    """

    # Qt Signals
    connect_clicked = pyqtSignal()
    disconnect_clicked = pyqtSignal()
    import_clicked = pyqtSignal()
    export_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connected = False

    def _setup_ui(self):
        """设置 UI"""
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(20, 20))

        # 连接按钮
        self._connect_btn = self._create_action_button(
            text="连接",
            tooltip="连接设备 (F6)",
            triggered=self._on_connect_clicked
        )
        self.addWidget(self._connect_btn)

        # 断开按钮
        self._disconnect_btn = self._create_action_button(
            text="断开",
            tooltip="断开设备 (F7)",
            triggered=self._on_disconnect_clicked
        )
        self._disconnect_btn.setEnabled(False)
        self.addWidget(self._disconnect_btn)

        self.addSeparator()

        # 刷新按钮
        self._refresh_btn = self._create_action_button(
            text="刷新",
            tooltip="刷新串口列表 (F5)",
            triggered=self._on_refresh_clicked
        )
        self.addWidget(self._refresh_btn)

        self.addSeparator()

        # 导入配置按钮
        self._import_btn = self._create_action_button(
            text="导入",
            tooltip="导入配置文件 (Ctrl+I)",
            triggered=self._on_import_clicked
        )
        self.addWidget(self._import_btn)

        # 导出配置按钮
        self._export_btn = self._create_action_button(
            text="导出",
            tooltip="导出配置文件 (Ctrl+E)",
            triggered=self._on_export_clicked
        )
        self.addWidget(self._export_btn)

        self.addSeparator()

        # FPS 标签（预留）
        self._fps_label = QLabel("FPS: --")
        self._fps_label.setStyleSheet("color: #808080; padding: 0 10px;")
        self.addWidget(self._fps_label)

        # 添加弹性空间
        spacer = QLabel("")
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

    def _create_action_button(self, text: str, tooltip: str, triggered) -> QPushButton:
        """
        创建工具栏按钮

        Args:
            text: 按钮文本
            tooltip: 提示文本
            triggered: 点击回调

        Returns:
            QPushButton: 创建的按钮
        """
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setMinimumHeight(30)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3C3C3C;
                color: #D4D4D4;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #2C2C2C;
            }
            QPushButton:disabled {
                background-color: #2C2C2C;
                color: #6B6B6B;
            }
        """)
        btn.clicked.connect(triggered)
        return btn

    def _on_connect_clicked(self):
        """连接按钮点击"""
        self.connect_clicked.emit()

    def _on_disconnect_clicked(self):
        """断开按钮点击"""
        self.disconnect_clicked.emit()

    def _on_refresh_clicked(self):
        """刷新按钮点击"""
        self.refresh_clicked.emit()

    def _on_import_clicked(self):
        """导入按钮点击"""
        self.import_clicked.emit()

    def _on_export_clicked(self):
        """导出按钮点击"""
        self.export_clicked.emit()

    # ==================== Public Methods ====================

    def set_connected(self, is_connected: bool):
        """
        设置连接状态

        Args:
            is_connected: 是否已连接
        """
        self._connected = is_connected

        if is_connected:
            self._connect_btn.setEnabled(False)
            self._disconnect_btn.setEnabled(True)
            self._refresh_btn.setEnabled(False)
        else:
            self._connect_btn.setEnabled(True)
            self._disconnect_btn.setEnabled(False)
            self._refresh_btn.setEnabled(True)

    def is_connected(self) -> bool:
        """
        获取连接状态

        Returns:
            bool: 是否已连接
        """
        return self._connected

    def set_fps(self, fps: float):
        """
        设置 FPS 显示

        Args:
            fps: 帧率
        """
        if fps > 0:
            self._fps_label.setText(f"FPS: {fps:.1f}")
            self._fps_label.setStyleSheet("color: #00FF00; padding: 0 10px;")
        else:
            self._fps_label.setText("FPS: --")
            self._fps_label.setStyleSheet("color: #808080; padding: 0 10px;")

    def set_enabled(self, enabled: bool):
        """
        设置所有按钮启用/禁用

        Args:
            enabled: 是否启用
        """
        if self._connected:
            self._disconnect_btn.setEnabled(enabled)
        else:
            self._connect_btn.setEnabled(enabled)
            self._refresh_btn.setEnabled(enabled)

        self._import_btn.setEnabled(enabled)
        self._export_btn.setEnabled(enabled)
