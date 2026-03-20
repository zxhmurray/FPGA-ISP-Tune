"""
FPGA ISP Tuner - ISP 参数模型
管理寄存器地址映射表、参数读写和校验
"""

import json
from dataclasses import dataclass
from typing import Optional, Dict, List

from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class RegisterEntry:
    """
    寄存器条目

    Attributes:
        name: 参数名称
        address: 寄存器地址
        description: 参数描述
        data_type: 数据类型 ("uint8", "uint16", "float16")
        min_value: 最小值
        max_value: 最大值
        default_value: 默认值
        current_value: 当前值
    """
    name: str
    address: int
    description: str
    data_type: str
    min_value: float
    max_value: float
    default_value: float
    current_value: float = 0.0

    def __post_init__(self):
        """初始化后设置当前值为默认值"""
        self.current_value = self.default_value


class ISPParametersModel(QObject):
    """
    ISP 参数模型 - 负责管理所有 ISP 寄存器参数

    Signals:
        parameter_changed: 参数变化 (name: str, value: float)
        parameter_validated: 参数校验结果 (name: str, is_valid: bool)
        batch_update: 批量更新 (parameters: Dict[str, float])
        register_map_loaded: 寄存器映射表已加载
    """

    # Qt Signals
    parameter_changed = pyqtSignal(str, float)
    parameter_validated = pyqtSignal(str, bool)
    batch_update = pyqtSignal(dict)
    register_map_loaded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._register_map: Dict[str, RegisterEntry] = {}
        self._address_to_name: Dict[int, str] = {}
        self._register_map_path: str = ""

    # ==================== Register Map Loading ====================

    def load_register_map(self, filepath: str) -> bool:
        """
        从 JSON 文件加载寄存器映射表

        Args:
            filepath: JSON 文件路径

        Returns:
            bool: 加载是否成功
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            registers = data.get('registers', [])
            self._register_map.clear()
            self._address_to_name.clear()

            for reg_data in registers:
                entry = RegisterEntry(
                    name=reg_data['name'],
                    address=reg_data['address'],
                    description=reg_data.get('description', ''),
                    data_type=reg_data.get('data_type', 'uint8'),
                    min_value=float(reg_data['min_value']),
                    max_value=float(reg_data['max_value']),
                    default_value=float(reg_data['default_value']),
                    current_value=float(reg_data['default_value'])
                )
                self._register_map[entry.name] = entry
                self._address_to_name[entry.address] = entry.name

            self._register_map_path = filepath
            self.register_map_loaded.emit()
            return True

        except Exception as e:
            print(f"加载寄存器映射表失败: {e}")
            return False

    def get_register_map_path(self) -> str:
        """获取当前寄存器映射表路径"""
        return self._register_map_path

    # ==================== Register Access ====================

    def get_register(self, name: str) -> Optional[RegisterEntry]:
        """
        根据名称获取寄存器条目

        Args:
            name: 参数名称

        Returns:
            Optional[RegisterEntry]: 寄存器条目，未找到返回 None
        """
        return self._register_map.get(name)

    def get_register_by_address(self, address: int) -> Optional[RegisterEntry]:
        """
        根据地址获取寄存器条目

        Args:
            address: 寄存器地址

        Returns:
            Optional[RegisterEntry]: 寄存器条目，未找到返回 None
        """
        name = self._address_to_name.get(address)
        if name:
            return self._register_map.get(name)
        return None

    def get_all_register_names(self) -> List[str]:
        """
        获取所有寄存器名称列表

        Returns:
            List[str]: 寄存器名称列表
        """
        return list(self._register_map.keys())

    # ==================== Parameter Access ====================

    def set_parameter(self, name: str, value: float) -> bool:
        """
        设置参数值

        Args:
            name: 参数名称
            value: 参数值

        Returns:
            bool: 设置是否成功
        """
        entry = self._register_map.get(name)
        if not entry:
            return False

        # 验证值是否在有效范围内
        if not self.validate_value(name, value):
            return False

        # 更新当前值
        old_value = entry.current_value
        entry.current_value = value

        # 如果值发生变化，发出信号
        if old_value != value:
            self.parameter_changed.emit(name, value)

        return True

    def get_parameter(self, name: str) -> Optional[float]:
        """
        获取参数值

        Args:
            name: 参数名称

        Returns:
            Optional[float]: 参数值，未找到返回 None
        """
        entry = self._register_map.get(name)
        if entry:
            return entry.current_value
        return None

    def get_all_parameters(self) -> Dict[str, float]:
        """
        获取所有参数的当前值

        Returns:
            Dict[str, float]: 参数名称到值的映射
        """
        return {
            name: entry.current_value
            for name, entry in self._register_map.items()
        }

    def get_all_addresses(self) -> Dict[str, int]:
        """
        获取所有参数名称到地址的映射

        Returns:
            Dict[str, int]: 参数名称到地址的映射
        """
        return {
            name: entry.address
            for name, entry in self._register_map.items()
        }

    def get_all_defaults(self) -> Dict[str, float]:
        """
        获取所有参数的默认值

        Returns:
            Dict[str, float]: 参数名称到默认值的映射
        """
        return {
            name: entry.default_value
            for name, entry in self._register_map.items()
        }

    # ==================== Validation ====================

    def validate_value(self, name: str, value: float) -> bool:
        """
        验证参数值是否在有效范围内

        Args:
            name: 参数名称
            value: 参数值

        Returns:
            bool: 值是否有效
        """
        entry = self._register_map.get(name)
        if not entry:
            self.parameter_validated.emit(name, False)
            return False

        is_valid = entry.min_value <= value <= entry.max_value
        self.parameter_validated.emit(name, is_valid)
        return is_valid

    def is_valid_parameter(self, name: str) -> bool:
        """
        检查参数名称是否有效

        Args:
            name: 参数名称

        Returns:
            bool: 参数是否有效
        """
        return name in self._register_map

    # ==================== Reset ====================

    def reset_to_default(self):
        """重置所有参数为默认值"""
        for entry in self._register_map.values():
            entry.current_value = entry.default_value

        # 发出批量更新信号
        self.batch_update.emit(self.get_all_parameters())

    def reset_to_default_by_name(self, name: str) -> bool:
        """
        重置单个参数为默认值

        Args:
            name: 参数名称

        Returns:
            bool: 重置是否成功
        """
        entry = self._register_map.get(name)
        if not entry:
            return False

        entry.current_value = entry.default_value
        self.parameter_changed.emit(name, entry.default_value)
        return True

    # ==================== Batch Operations ====================

    def set_parameters(self, parameters: Dict[str, float]) -> Dict[str, bool]:
        """
        批量设置参数

        Args:
            parameters: 参数名称到值的映射

        Returns:
            Dict[str, bool]: 每个参数的设置结果
        """
        results = {}
        for name, value in parameters.items():
            results[name] = self.set_parameter(name, value)

        # 发出批量更新信号
        self.batch_update.emit(self.get_all_parameters())
        return results

    def get_parameters_by_addresses(self, addresses: List[int]) -> Dict[int, float]:
        """
        根据地址列表获取对应的参数值

        Args:
            addresses: 地址列表

        Returns:
            Dict[int, float]: 地址到值的映射
        """
        result = {}
        for addr in addresses:
            entry = self.get_register_by_address(addr)
            if entry:
                result[addr] = entry.current_value
        return result

    # ==================== Utility ====================

    def get_parameter_info(self, name: str) -> Optional[Dict]:
        """
        获取参数的详细信息

        Args:
            name: 参数名称

        Returns:
            Optional[Dict]: 参数信息，未找到返回 None
        """
        entry = self._register_map.get(name)
        if not entry:
            return None

        return {
            'name': entry.name,
            'address': entry.address,
            'address_hex': f"0x{entry.address:04X}",
            'description': entry.description,
            'data_type': entry.data_type,
            'min_value': entry.min_value,
            'max_value': entry.max_value,
            'default_value': entry.default_value,
            'current_value': entry.current_value
        }

    def __len__(self) -> int:
        """返回寄存器数量"""
        return len(self._register_map)

    def __contains__(self, name: str) -> bool:
        """检查参数是否存在"""
        return name in self._register_map

    def __getitem__(self, name: str) -> Optional[float]:
        """支持下标访问 []"""
        return self.get_parameter(name)
