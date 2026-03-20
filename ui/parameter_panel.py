"""
FPGA ISP Tuner - 参数面板
ISP 参数调节面板，动态生成参数控件
"""

from typing import Dict, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGroupBox,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

from .widgets.parameter_slider import ParameterSlider


class ParameterPanel(QWidget):
    """
    参数面板 - ISP 参数调节面板

    Signals:
        parameter_changed: 参数值变化 (name: str, value: float)
        reset_request: 重置参数请求 (name: str)
        apply_all_request: 批量应用请求
    """

    # Qt Signals
    parameter_changed = pyqtSignal(str, float)
    reset_request = pyqtSignal(str)
    apply_all_request = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parameter_sliders: Dict[str, ParameterSlider] = {}
        self._register_names: List[str] = []
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = QLabel("<h3>ISP 参数调节</h3>")
        layout.addWidget(title_label)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 滚动区域的内容容器
        scroll_content = QWidget()
        self._content_layout = QVBoxLayout(scroll_content)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._content_layout.setSpacing(10)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # 底部按钮
        btn_layout = QVBoxLayout()

        self._apply_all_btn = QPushButton("全部应用到 FPGA")
        self._apply_all_btn.setMinimumHeight(35)
        self._apply_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #107C10;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0B5C0B;
            }
        """)
        self._apply_all_btn.clicked.connect(self.apply_all_request.emit)

        self._reset_all_btn = QPushButton("重置所有参数")
        self._reset_all_btn.setMinimumHeight(35)
        self._reset_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #D83B01;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A3330B;
            }
        """)
        self._reset_all_btn.clicked.connect(self._on_reset_all_clicked)

        btn_layout.addWidget(self._apply_all_btn)
        btn_layout.addWidget(self._reset_all_btn)

        layout.addLayout(btn_layout)

    def _on_reset_all_clicked(self):
        """重置所有参数"""
        for name in self._register_names:
            self.reset_request.emit(name)

    # ==================== Public Methods ====================

    def add_parameter(
        self,
        name: str,
        address: int,
        min_value: float,
        max_value: float,
        default_value: float,
        data_type: str = "uint8",
        description: str = ""
    ):
        """
        添加一个参数控件

        Args:
            name: 参数名称
            address: 寄存器地址
            min_value: 最小值
            max_value: 最大值
            default_value: 默认值
            data_type: 数据类型 ("uint8", "float16")
            description: 参数描述
        """
        if name in self._parameter_sliders:
            return

        # 创建参数滑动控件
        slider = ParameterSlider(
            name=name,
            address=address,
            min_value=min_value,
            max_value=max_value,
            default_value=default_value,
            data_type=data_type,
            description=description
        )

        # 连接信号
        slider.value_changed.connect(self.parameter_changed.emit)
        slider.reset_clicked.connect(self.reset_request.emit)

        # 添加到布局
        self._content_layout.addWidget(slider)
        self._parameter_sliders[name] = slider
        self._register_names.append(name)

    def remove_parameter(self, name: str):
        """
        移除一个参数控件

        Args:
            name: 参数名称
        """
        if name not in self._parameter_sliders:
            return

        slider = self._parameter_sliders.pop(name)
        self._register_names.remove(name)
        self._content_layout.removeWidget(slider)
        slider.deleteLater()

    def clear_parameters(self):
        """清除所有参数控件"""
        for name in list(self._parameter_sliders.keys()):
            self.remove_parameter(name)

    def set_parameter(self, name: str, value: float):
        """
        设置参数值

        Args:
            name: 参数名称
            value: 参数值
        """
        if name in self._parameter_sliders:
            self._parameter_sliders[name].set_value(value)

    def get_parameter(self, name: str) -> float:
        """
        获取参数值

        Args:
            name: 参数名称

        Returns:
            float: 参数值
        """
        if name in self._parameter_sliders:
            return self._parameter_sliders[name].get_value()
        return 0.0

    def get_all_parameters(self) -> Dict[str, float]:
        """
        获取所有参数值

        Returns:
            Dict[str, float]: 参数名称到值的映射
        """
        return {
            name: slider.get_value()
            for name, slider in self._parameter_sliders.items()
        }

    def update_all_parameters(self, parameters: Dict[str, float]):
        """
        批量更新所有参数值

        Args:
            parameters: 参数名称到值的映射
        """
        for name, value in parameters.items():
            if name in self._parameter_sliders:
                self._parameter_sliders[name].set_value(value)

    def reset_parameter(self, name: str):
        """
        重置单个参数为默认值

        Args:
            name: 参数名称
        """
        if name in self._parameter_sliders:
            self._parameter_sliders[name].reset()

    def reset_all_parameters(self):
        """重置所有参数为默认值"""
        for slider in self._parameter_sliders.values():
            slider.reset()

    def set_enabled(self, enabled: bool):
        """
        设置所有控件启用/禁用状态

        Args:
            enabled: 是否启用
        """
        for slider in self._parameter_sliders.values():
            slider.set_enabled(enabled)
        self._apply_all_btn.setEnabled(enabled)
        self._reset_all_btn.setEnabled(enabled)

    def get_parameter_names(self) -> List[str]:
        """
        获取所有参数名称

        Returns:
            List[str]: 参数名称列表
        """
        return list(self._register_names)

    def __len__(self) -> int:
        """返回参数数量"""
        return len(self._parameter_sliders)

    def __getitem__(self, name: str) -> float:
        """支持下标访问 []"""
        return self.get_parameter(name)
