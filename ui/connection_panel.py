"""
FPGA ISP Tuner - 连接面板
串口设置与连接控制
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QPushButton, QLabel, QFormLayout
)
from PyQt6.QtCore import pyqtSignal, Qt


class ConnectionPanel(QWidget):
    """
    连接面板 - 串口设置与连接控制

    Signals:
        connect_request: 连接请求 (port: str, baudrate: int, kwargs: dict)
        disconnect_request: 断开连接请求
        refresh_request: 刷新串口列表请求
    """

    # Qt Signals
    connect_request = pyqtSignal(str, int, dict)
    disconnect_request = pyqtSignal()
    refresh_request = pyqtSignal()

    # 常用波特率
    BAUDRATES = [
        9600, 19200, 38400, 57600,
        115200, 230400, 460800, 921600
    ]

    # 数据位选项
    DATABITS = ["5", "6", "7", "8"]

    # 校验位选项
    PARITIES = ["None", "Even", "Odd"]

    # 停止位选项
    STOPBITS = ["1", "1.5", "2"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._refresh_ports()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)

        # 串口设置组
        group = QGroupBox("串口设置")
        form_layout = QFormLayout()

        # 端口选择
        port_layout = QHBoxLayout()
        self._port_combo = QComboBox()
        self._port_combo.setMinimumWidth(150)
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.setMaximumWidth(60)
        self._refresh_btn.clicked.connect(self._on_refresh_clicked)
        port_layout.addWidget(self._port_combo)
        port_layout.addWidget(self._refresh_btn)
        form_layout.addRow("端口:", port_layout)

        # 波特率选择
        self._baudrate_combo = QComboBox()
        for baud in self.BAUDRATES:
            self._baudrate_combo.addItem(str(baud))
        # 默认选择 115200
        index = self._baudrate_combo.findText("115200")
        if index >= 0:
            self._baudrate_combo.setCurrentIndex(index)
        form_layout.addRow("波特率:", self._baudrate_combo)

        # 数据位选择
        self._databits_combo = QComboBox()
        self._databits_combo.addItems(self.DATABITS)
        self._databits_combo.setCurrentText("8")
        form_layout.addRow("数据位:", self._databits_combo)

        # 校验位选择
        self._parity_combo = QComboBox()
        self._parity_combo.addItems(self.PARITIES)
        form_layout.addRow("校验位:", self._parity_combo)

        # 停止位选择
        self._stopbits_combo = QComboBox()
        self._stopbits_combo.addItems(self.STOPBITS)
        self._stopbits_combo.setCurrentText("1")
        form_layout.addRow("停止位:", self._stopbits_combo)

        group.setLayout(form_layout)
        layout.addWidget(group)

        # 连接/断开按钮
        btn_layout = QHBoxLayout()
        self._connect_btn = QPushButton("连接")
        self._connect_btn.setMinimumHeight(40)
        self._connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
        """)
        self._connect_btn.clicked.connect(self._on_connect_clicked)

        self._disconnect_btn = QPushButton("断开")
        self._disconnect_btn.setMinimumHeight(40)
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B6B6B;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #A0A0A0;
            }
        """)
        self._disconnect_btn.clicked.connect(self._on_disconnect_clicked)

        btn_layout.addWidget(self._connect_btn)
        btn_layout.addWidget(self._disconnect_btn)
        layout.addLayout(btn_layout)

        # 添加弹性空间
        layout.addStretch()

    def _refresh_ports(self):
        """刷新可用串口列表"""
        self._port_combo.clear()
        # 预留的端口列表，实际串口扫描由 Controller 调用 list_available_ports() 获取
        # 这里添加占位符提示
        self._port_combo.addItem("-- 请刷新 --")

    def _on_refresh_clicked(self):
        """刷新按钮点击"""
        self.refresh_request.emit()

    def _on_connect_clicked(self):
        """连接按钮点击"""
        port = self._port_combo.currentText()
        if not port or port == "-- 请刷新 --":
            return

        baudrate = int(self._baudrate_combo.currentText())

        # 获取其他参数
        databits = int(self._databits_combo.currentText())
        parity_text = self._parity_combo.currentText()
        parity_map = {"None": "N", "Even": "E", "Odd": "O"}
        parity = parity_map.get(parity_text, "N")

        stopbits_text = self._stopbits_combo.currentText()
        stopbits_map = {"1": 1, "1.5": 1.5, "2": 2}
        stopbits = stopbits_map.get(stopbits_text, 1)

        kwargs = {
            "data_bits": databits,
            "parity": parity,
            "stop_bits": stopbits
        }

        self.connect_request.emit(port, baudrate, kwargs)

    def _on_disconnect_clicked(self):
        """断开按钮点击"""
        self.disconnect_request.emit()

    # ==================== Public Methods ====================

    def set_ports(self, ports: list):
        """
        设置可用端口列表

        Args:
            ports: 端口名列表
        """
        self._port_combo.clear()
        if ports:
            self._port_combo.addItems(ports)
        else:
            self._port_combo.addItem("-- 未找到串口 --")

    def set_connected(self, is_connected: bool):
        """
        设置连接状态

        Args:
            is_connected: 是否已连接
        """
        if is_connected:
            self._connect_btn.setEnabled(False)
            self._disconnect_btn.setEnabled(True)
            self._port_combo.setEnabled(False)
            self._baudrate_combo.setEnabled(False)
            self._databits_combo.setEnabled(False)
            self._parity_combo.setEnabled(False)
            self._stopbits_combo.setEnabled(False)
            self._refresh_btn.setEnabled(False)
        else:
            self._connect_btn.setEnabled(True)
            self._disconnect_btn.setEnabled(False)
            self._port_combo.setEnabled(True)
            self._baudrate_combo.setEnabled(True)
            self._databits_combo.setEnabled(True)
            self._parity_combo.setEnabled(True)
            self._stopbits_combo.setEnabled(True)
            self._refresh_btn.setEnabled(True)

    def get_current_port(self) -> str:
        """获取当前选择的端口"""
        return self._port_combo.currentText()

    def get_current_baudrate(self) -> int:
        """获取当前选择的波特率"""
        return int(self._baudrate_combo.currentText())
