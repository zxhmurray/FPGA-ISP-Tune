"""
FPGA ISP Tuner - 主窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QLabel, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal


class MainWindow(QMainWindow):
    """
    主窗口 - 应用程序主界面

    Signals:
        import_config_request: 请求导入配置
        export_config_request: 请求导出配置
        quit_request: 请求退出应用
    """

    # Qt Signals
    import_config_request = pyqtSignal()
    export_config_request = pyqtSignal()
    quit_request = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._create_menu_bar()
        self._create_status_bar()

    def _setup_ui(self):
        """设置 UI 布局"""
        self.setWindowTitle("FPGA ISP Tuner")
        self.setMinimumSize(1200, 800)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板容器（将在 Controller 中添加具体面板）
        self._left_panel = QWidget()
        self._left_layout = QVBoxLayout(self._left_panel)
        self._left_layout.setContentsMargins(0, 0, 0, 0)

        # 右侧面板容器（将在 Controller 中添加具体面板）
        self._right_panel = QWidget()
        self._right_layout = QVBoxLayout(self._right_panel)
        self._right_layout.setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(self._left_panel)
        splitter.addWidget(self._right_panel)
        splitter.setSizes([350, 850])

        main_layout.addWidget(splitter)

    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        import_action = file_menu.addAction("导入配置...")
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_config_request)

        export_action = file_menu.addAction("导出配置...")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_config_request)

        file_menu.addSeparator()

        quit_action = file_menu.addAction("退出")
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        quit_action.triggered.connect(self.quit_request.emit)

        # 通信菜单
        comm_menu = menubar.addMenu("通信(&S)")

        refresh_action = comm_menu.addAction("刷新串口")
        refresh_action.setShortcut("F5")

        comm_menu.addSeparator()

        connect_action = comm_menu.addAction("连接...")
        connect_action.setShortcut("F6")

        disconnect_action = comm_menu.addAction("断开")
        disconnect_action.setShortcut("F7")

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self._show_about)

    def _create_status_bar(self):
        """创建状态栏"""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        # 连接状态标签
        self._connection_label = QLabel("未连接")
        self._status_bar.addWidget(self._connection_label)

        # 分隔符
        self._status_bar.addWidget(QLabel("|"))

        # 端口标签
        self._port_label = QLabel("端口: --")
        self._status_bar.addWidget(self._port_label)

        # 分隔符
        self._status_bar.addWidget(QLabel("|"))

        # 波特率标签
        self._baudrate_label = QLabel("波特率: --")
        self._status_bar.addWidget(self._baudrate_label)

        # 分隔符
        self._status_bar.addWidget(QLabel("|"))

        # FPS 标签（预留）
        self._fps_label = QLabel("FPS: --")
        self._status_bar.addWidget(self._fps_label)

        # 右侧永久显示
        self._status_bar.addPermanentWidget(QLabel("v1.0.0"))

    def _show_about(self):
        """显示关于对话框"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "关于 FPGA ISP Tuner",
            "FPGA ISP Tuner v1.0.0\n\n"
            "FPGA Camera ISP 调参软件\n\n"
            "用于实时调整 FPGA 内部 ISP 算法模块的寄存器参数"
        )

    # ==================== Public Methods ====================

    def get_left_panel(self) -> QWidget:
        """获取左侧面板容器"""
        return self._left_panel

    def get_right_panel(self) -> QWidget:
        """获取右侧面板容器"""
        return self._right_panel

    def get_left_layout(self) -> QVBoxLayout:
        """获取左侧面板布局"""
        return self._left_layout

    def get_right_layout(self) -> QVBoxLayout:
        """获取右侧面板布局"""
        return self._right_layout

    def update_connection_status(self, is_connected: bool, port: str = "", baudrate: int = 0):
        """
        更新连接状态显示

        Args:
            is_connected: 是否已连接
            port: 端口名
            baudrate: 波特率
        """
        if is_connected:
            self._connection_label.setText(f"<span style='color: green;'>已连接</span>")
            self._port_label.setText(f"端口: {port}")
            self._baudrate_label.setText(f"波特率: {baudrate}")
        else:
            self._connection_label.setText("<span style='color: gray;'>未连接</span>")
            self._port_label.setText("端口: --")
            self._baudrate_label.setText("波特率: --")

    def update_fps(self, fps: float):
        """
        更新 FPS 显示（预留）

        Args:
            fps: 帧率
        """
        if fps > 0:
            self._fps_label.setText(f"FPS: {fps:.1f}")
        else:
            self._fps_label.setText("FPS: --")

    def append_log(self, level: str, message: str):
        """
        添加日志消息（便捷方法）

        Args:
            level: 日志级别
            message: 日志消息
        """
        # 实际日志输出由 LogPanel 处理
        # 此处仅在状态栏显示最新消息
        self.statusBar().showMessage(f"[{level}] {message}", 3000)
