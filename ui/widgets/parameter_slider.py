"""
FPGA ISP Tuner - 参数滑动控件
单个 ISP 参数的滑动调节控件
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QSlider, QDoubleSpinBox, QSpinBox, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtBoundSignal


class ParameterSlider(QWidget):
    """
    参数滑动控件 - 单个 ISP 参数的调节控件

    Signals:
        value_changed: 参数值变化 (name: str, value: float)
        reset_clicked: 重置按钮点击 (name: str)
    """

    # Qt Signals
    value_changed: pyqtBoundSignal = pyqtSignal(str, float)
    reset_clicked: pyqtBoundSignal = pyqtSignal(str)

    def __init__(
        self,
        name: str,
        address: int,
        min_value: float,
        max_value: float,
        default_value: float,
        data_type: str = "uint8",
        description: str = "",
        parent=None
    ):
        """
        初始化参数滑动控件

        Args:
            name: 参数名称
            address: 寄存器地址
            min_value: 最小值
            max_value: 最大值
            default_value: 默认值
            data_type: 数据类型 ("uint8", "float16")
            description: 参数描述
            parent: 父控件
        """
        super().__init__(parent)
        self._name = name
        self._address = address
        self._min_value = min_value
        self._max_value = max_value
        self._default_value = default_value
        self._data_type = data_type
        self._description = description
        self._current_value = default_value

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # 标题行
        header_layout = QHBoxLayout()

        # 参数名称和描述
        title_label = QLabel(f"<b>{self._name}</b>")
        if self._description:
            title_label.setToolTip(self._description)
        header_layout.addWidget(title_label)

        # 地址标签
        address_label = QLabel(f"<span style='color: gray;'>[0x{self._address:04X}]</span>")
        address_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(address_label)

        layout.addLayout(header_layout)

        # 滑动行
        slider_layout = QHBoxLayout()

        # 左侧最小值标签
        min_label = QLabel(str(self._min_value))
        min_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        min_label.setMinimumWidth(40)
        slider_layout.addWidget(min_label)

        # 根据数据类型选择滑动条和输入框
        if self._data_type == "float16":
            # 浮点类型
            self._slider = QSlider(Qt.Orientation.Horizontal)
            self._slider.setMinimum(int(self._min_value * 100))
            self._slider.setMaximum(int(self._max_value * 100))
            self._slider.setValue(int(self._default_value * 100))
            self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            self._slider.setTickInterval(50)

            slider_layout.addWidget(self._slider)

            self._input = QDoubleSpinBox()
            self._input.setMinimum(self._min_value)
            self._input.setMaximum(self._max_value)
            self._input.setValue(self._default_value)
            self._input.setSingleStep(0.1)
            self._input.setDecimals(1)
        else:
            # 整数类型
            self._slider = QSlider(Qt.Orientation.Horizontal)
            self._slider.setMinimum(int(self._min_value))
            self._slider.setMaximum(int(self._max_value))
            self._slider.setValue(int(self._default_value))
            self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            self._slider.setTickInterval(int((self._max_value - self._min_value) / 10) or 1)

            slider_layout.addWidget(self._slider)

            self._input = QSpinBox()
            self._input.setMinimum(int(self._min_value))
            self._input.setMaximum(int(self._max_value))
            self._input.setValue(int(self._default_value))

        self._input.setMinimumWidth(70)
        self._input.setMaximumWidth(80)
        slider_layout.addWidget(self._input)

        # 右侧最大值标签
        max_label = QLabel(str(self._max_value))
        max_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        max_label.setMinimumWidth(40)
        slider_layout.addWidget(max_label)

        layout.addLayout(slider_layout)

        # 底部按钮行
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._reset_btn = QPushButton("重置")
        self._reset_btn.setMaximumWidth(60)
        self._reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self._reset_btn)

        layout.addLayout(btn_layout)

    def _setup_connections(self):
        """设置信号连接"""
        self._slider.valueChanged.connect(self._on_slider_changed)
        self._input.valueChanged.connect(self._on_input_changed)
        self._reset_btn.clicked.connect(self._on_reset_clicked)

    def _on_slider_changed(self, value):
        """滑动条值变化"""
        if self._data_type == "float16":
            actual_value = value / 100.0
        else:
            actual_value = value

        # 同步更新输入框（避免循环触发）
        self._input.blockSignals(True)
        if self._data_type == "float16":
            self._input.setValue(actual_value)
        else:
            self._input.setValue(int(actual_value))
        self._input.blockSignals(False)

        self._current_value = actual_value
        self.value_changed.emit(self._name, actual_value)

    def _on_input_changed(self, value):
        """输入框值变化"""
        # 同步更新滑动条
        if self._data_type == "float16":
            slider_value = int(value * 100)
        else:
            slider_value = int(value)

        self._slider.blockSignals(True)
        self._slider.setValue(slider_value)
        self._slider.blockSignals(False)

        self._current_value = value
        self.value_changed.emit(self._name, float(value))

    def _on_reset_clicked(self):
        """重置按钮点击"""
        self.reset_clicked.emit(self._name)

    # ==================== Public Methods ====================

    def set_value(self, value: float):
        """
        设置参数值

        Args:
            value: 参数值
        """
        # 根据数据类型转换为正确的类型
        if self._data_type == "float16":
            self._input.setValue(float(value))
        else:
            self._input.setValue(int(value))
        self._current_value = value

    def get_value(self) -> float:
        """
        获取当前参数值

        Returns:
            float: 当前值
        """
        return self._current_value

    def get_name(self) -> str:
        """
        获取参数名称

        Returns:
            str: 参数名称
        """
        return self._name

    def get_address(self) -> int:
        """
        获取寄存器地址

        Returns:
            int: 寄存器地址
        """
        return self._address

    def reset(self):
        """重置为默认值"""
        self.set_value(self._default_value)

    def set_enabled(self, enabled: bool):
        """
        设置控件启用/禁用状态

        Args:
            enabled: 是否启用
        """
        self._slider.setEnabled(enabled)
        self._input.setEnabled(enabled)
        self._reset_btn.setEnabled(enabled)

    def set_readonly(self, readonly: bool):
        """
        设置只读模式

        Args:
            readonly: 是否只读
        """
        self._slider.setEnabled(not readonly)
        self._input.setReadOnly(readonly)
        self._reset_btn.setEnabled(not readonly)
