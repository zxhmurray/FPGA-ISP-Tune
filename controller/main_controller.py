"""
FPGA ISP Tuner - 主控制器
协调 View 与 Model 之间的交互
"""

import os
from typing import Optional

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt6.QtCore import QTimer

from core import CommunicationModel, ISPParametersModel, ProtocolHandler
from ui import (
    MainWindow, ConnectionPanel, ParameterPanel,
    LogPanel, Toolbar, PreviewPanel, HistogramPanel
)
from utils import ConfigManager


class MainController:
    """
    主控制器 - 协调 View 与 Model 之间的交互

    职责:
        - 实例化所有 Model 和 View
        - 绑定信号槽
        - 管理应用生命周期
    """

    def __init__(self):
        # ========== Model 实例化 ==========
        self._comm_model = CommunicationModel()
        self._isp_model = ISPParametersModel()
        self._config_manager = ConfigManager()

        # ========== View 实例化 ==========
        self._main_window = MainWindow()
        self._connection_panel = ConnectionPanel()
        self._parameter_panel = ParameterPanel()
        self._log_panel = LogPanel()
        self._toolbar = Toolbar()
        self._preview_panel = PreviewPanel()   # 预留
        self._histogram_panel = HistogramPanel()  # 预留

        # ========== 布局设置 ==========
        self._setup_layout()

        # ========== 信号槽绑定 ==========
        self._setup_connections()

        # ========== 加载寄存器映射 ==========
        self._load_register_map()

        # ========== 显示主窗口 ==========
        self._main_window.show()

    # ==================== 布局设置 ====================

    def _setup_layout(self):
        """设置布局"""
        # 将工具栏添加到主窗口
        self._main_window.addToolBar(self._toolbar)

        # 左侧面板布局
        left_layout = self._main_window.get_left_layout()
        left_layout.addWidget(self._connection_panel)
        left_layout.addWidget(self._parameter_panel)

        # 右侧面板布局
        right_layout = self._main_window.get_right_layout()
        right_layout.addWidget(self._preview_panel)   # 预留
        right_layout.addWidget(self._histogram_panel)  # 预留
        right_layout.addWidget(self._log_panel)

        # 设置拉伸因子
        right_layout.setStretchFactor(self._preview_panel, 3)
        right_layout.setStretchFactor(self._histogram_panel, 2)
        right_layout.setStretchFactor(self._log_panel, 2)

    # ==================== 信号槽绑定 ====================

    def _setup_connections(self):
        """绑定所有信号槽"""

        # ========== ConnectionPanel -> Controller ==========
        self._connection_panel.connect_request.connect(self._on_connect)
        self._connection_panel.disconnect_request.connect(self._on_disconnect)
        self._connection_panel.refresh_request.connect(self._on_refresh_ports)

        # ========== ParameterPanel -> Controller ==========
        self._parameter_panel.parameter_changed.connect(self._on_parameter_changed)
        self._parameter_panel.reset_request.connect(self._on_reset_parameter)
        self._parameter_panel.apply_all_request.connect(self._on_apply_all_parameters)

        # ========== Toolbar -> Controller ==========
        self._toolbar.connect_clicked.connect(self._on_toolbar_connect)
        self._toolbar.disconnect_clicked.connect(self._on_disconnect)
        self._toolbar.refresh_clicked.connect(self._on_refresh_ports)
        self._toolbar.import_clicked.connect(self._on_import_config)
        self._toolbar.export_clicked.connect(self._on_export_config)

        # ========== MainWindow -> Controller ==========
        self._main_window.import_config_request.connect(self._on_import_config)
        self._main_window.export_config_request.connect(self._on_export_config)
        self._main_window.quit_request.connect(self._on_quit)

        # ========== CommunicationModel -> Controller -> View ==========
        self._comm_model.connection_status_changed.connect(self._on_connection_status_changed)
        self._comm_model.error_occurred.connect(self._on_comm_error)
        self._comm_model.log_message.connect(self._on_log_message)
        self._comm_model.register_read_response.connect(self._on_register_read_response)

        # ========== ISPParametersModel -> Controller ==========
        self._isp_model.parameter_changed.connect(self._on_model_parameter_changed)
        self._isp_model.register_map_loaded.connect(self._on_register_map_loaded)
        self._isp_model.batch_update.connect(self._on_batch_update)

    # ==================== 初始化 ====================

    def _load_register_map(self):
        """加载寄存器映射"""
        # 获取 config 目录路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "register_map.json")

        if os.path.exists(config_path):
            if self._isp_model.load_register_map(config_path):
                self._log_panel.info(f"寄存器映射表已加载: {config_path}")
                self._populate_parameter_panel()
            else:
                self._log_panel.error(f"寄存器映射表加载失败: {config_path}")
        else:
            self._log_panel.warning(f"寄存器映射表未找到: {config_path}")

    def _populate_parameter_panel(self):
        """填充参数面板"""
        self._parameter_panel.clear_parameters()

        for name in self._isp_model.get_all_register_names():
            entry = self._isp_model.get_register(name)
            if entry:
                self._parameter_panel.add_parameter(
                    name=entry.name,
                    address=entry.address,
                    min_value=entry.min_value,
                    max_value=entry.max_value,
                    default_value=entry.default_value,
                    data_type=entry.data_type,
                    description=entry.description
                )

        self._log_panel.info(f"已加载 {len(self._isp_model)} 个 ISP 参数")

    # ==================== 连接相关 ====================

    def _on_connect(self, port: str, baudrate: int, kwargs: dict):
        """
        处理连接请求

        Args:
            port: 端口名
            baudrate: 波特率
            kwargs: 其他参数
        """
        self._log_panel.info(f"正在连接 {port} @ {baudrate}...")

        if self._comm_model.connect(port, baudrate, **kwargs):
            # 连接成功
            self._connection_panel.set_connected(True)
            self._toolbar.set_connected(True)
            self._main_window.update_connection_status(True, port, baudrate)
        else:
            # 连接失败
            self._log_panel.error(f"连接失败: {port}")

    def _on_disconnect(self):
        """处理断开连接请求"""
        self._comm_model.disconnect()
        self._connection_panel.set_connected(False)
        self._toolbar.set_connected(False)
        self._main_window.update_connection_status(False)

    def _on_refresh_ports(self):
        """处理刷新串口请求"""
        ports = self._comm_model.list_available_ports()
        self._connection_panel.set_ports(ports)
        if ports:
            self._log_panel.info(f"找到 {len(ports)} 个可用串口: {', '.join(ports)}")
        else:
            self._log_panel.warning("未找到可用串口")

    def _on_toolbar_connect(self):
        """工具栏连接按钮点击"""
        port = self._connection_panel.get_current_port()
        baudrate = self._connection_panel.get_current_baudrate()
        if port and port != "-- 请刷新 --" and port != "-- 未找到串口 --":
            self._on_connect(port, baudrate, {})

    def _on_connection_status_changed(self, is_connected: bool, port: str):
        """
        连接状态变化

        Args:
            is_connected: 是否已连接
            port: 端口名
        """
        if is_connected:
            self._log_panel.info(f"已连接到 {port}")
        else:
            self._log_panel.info("已断开连接")
            self._connection_panel.set_connected(False)
            self._toolbar.set_connected(False)

    # ==================== 参数相关 ====================

    def _on_parameter_changed(self, name: str, value: float):
        """
        参数变化处理

        Args:
            name: 参数名
            value: 参数值
        """
        # 1. 更新 Model
        self._isp_model.set_parameter(name, value)

        # 2. 如果已连接，写入 FPGA
        if self._comm_model.is_connected:
            entry = self._isp_model.get_register(name)
            if entry:
                self._comm_model.write_register(entry.address, int(value))

        self._log_panel.debug(f"{name} = {value}")

    def _on_reset_parameter(self, name: str):
        """
        重置单个参数

        Args:
            name: 参数名
        """
        self._isp_model.reset_to_default_by_name(name)
        entry = self._isp_model.get_register(name)
        if entry:
            self._parameter_panel.set_parameter(name, entry.default_value)

            # 如果已连接，写入 FPGA
            if self._comm_model.is_connected:
                self._comm_model.write_register(entry.address, int(entry.default_value))

        self._log_panel.info(f"{name} 已重置为默认值")

    def _on_apply_all_parameters(self):
        """批量应用所有参数到 FPGA"""
        if not self._comm_model.is_connected:
            self._log_panel.warning("未连接设备，无法写入")
            return

        success_count = 0
        fail_count = 0

        for name in self._isp_model.get_all_register_names():
            entry = self._isp_model.get_register(name)
            if entry:
                if self._comm_model.write_register(entry.address, int(entry.current_value)):
                    success_count += 1
                else:
                    fail_count += 1

        if fail_count == 0:
            self._log_panel.info(f"已写入 {success_count} 个参数到 FPGA")
        else:
            self._log_panel.warning(f"写入完成: {success_count} 成功, {fail_count} 失败")

    def _on_model_parameter_changed(self, name: str, value: float):
        """
        Model 层参数变化（用于同步其他组件）

        Args:
            name: 参数名
            value: 参数值
        """
        # 可以在这里添加额外的同步逻辑
        pass

    def _on_register_map_loaded(self):
        """寄存器映射加载完成"""
        self._populate_parameter_panel()

    def _on_batch_update(self, parameters: dict):
        """
        批量更新参数

        Args:
            parameters: 参数字典
        """
        self._parameter_panel.update_all_parameters(parameters)

    def _on_register_read_response(self, address: int, value: int):
        """
        寄存器读响应

        Args:
            address: 地址
            value: 值
        """
        entry = self._isp_model.get_register_by_address(address)
        if entry:
            # 更新参数值
            if entry.data_type == "float16":
                display_value = value / 256.0  # 假设 float16 表示
            else:
                display_value = value

            self._isp_model.set_parameter(entry.name, float(display_value))
            self._parameter_panel.set_parameter(entry.name, float(display_value))
            self._log_panel.debug(f"读寄存器: {entry.name} = {display_value}")

    # ==================== 配置管理 ====================

    def _on_import_config(self):
        """处理导入配置请求"""
        filepath, _ = QFileDialog.getOpenFileName(
            self._main_window,
            "导入配置文件",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not filepath:
            return

        params = self._config_manager.import_config(filepath)
        if params:
            # 更新参数
            self._isp_model.set_parameters(params)
            self._parameter_panel.update_all_parameters(params)

            # 如果已连接，批量写入
            if self._comm_model.is_connected:
                results = self._config_manager.batch_write_to_fpga(
                    params, self._comm_model, self._isp_model
                )
                success = sum(1 for v in results.values() if v)
                self._log_panel.info(f"配置已导入并写入 {success}/{len(params)} 个参数")
            else:
                self._log_panel.info(f"配置已导入: {filepath}")

            QMessageBox.information(
                self._main_window,
                "导入成功",
                f"已导入 {len(params)} 个参数"
            )
        else:
            self._log_panel.error(f"配置导入失败: {filepath}")
            QMessageBox.critical(
                self._main_window,
                "导入失败",
                "配置文件格式错误或无效"
            )

    def _on_export_config(self):
        """处理导出配置请求"""
        filepath, _ = QFileDialog.getSaveFileName(
            self._main_window,
            "导出配置文件",
            "isp_config.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if not filepath:
            return

        params = self._isp_model.get_all_parameters()
        if self._config_manager.export_config(filepath, params):
            self._log_panel.info(f"配置已导出: {filepath}")
            QMessageBox.information(
                self._main_window,
                "导出成功",
                f"已导出 {len(params)} 个参数到 {filepath}"
            )
        else:
            self._log_panel.error(f"配置导出失败: {filepath}")
            QMessageBox.critical(
                self._main_window,
                "导出失败",
                "无法写入配置文件"
            )

    # ==================== 日志与错误 ====================

    def _on_comm_error(self, error_msg: str):
        """
        通信错误处理

        Args:
            error_msg: 错误消息
        """
        self._log_panel.error(error_msg)
        QMessageBox.warning(self._main_window, "通信错误", error_msg)

    def _on_log_message(self, level: str, message: str):
        """
        日志消息处理

        Args:
            level: 日志级别
            message: 日志消息
        """
        self._log_panel.append_log(level, message)

    # ==================== 退出 ====================

    def _on_quit(self):
        """处理退出请求"""
        # 断开连接
        if self._comm_model.is_connected:
            self._comm_model.disconnect()

        # 退出应用
        QApplication.quit()

    # ==================== 公共方法 ====================

    def run(self):
        """运行应用"""
        return QApplication.exec()

    def get_main_window(self) -> MainWindow:
        """获取主窗口"""
        return self._main_window

    def get_comm_model(self) -> CommunicationModel:
        """获取通信模型"""
        return self._comm_model

    def get_isp_model(self) -> ISPParametersModel:
        """获取 ISP 参数模型"""
        return self._isp_model
