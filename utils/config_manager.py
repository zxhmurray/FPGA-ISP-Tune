"""
FPGA ISP Tuner - 配置管理器
负责配置的导入/导出
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List


class ConfigManager:
    """
    配置管理器 - 负责配置的导入/导出

    Attributes:
        CONFIG_VERSION: 配置文件版本号
    """

    CONFIG_VERSION = "1.0"

    def __init__(self):
        pass

    def export_config(self, filepath: str, parameters: Dict[str, float]) -> bool:
        """
        导出配置到 JSON 文件

        Args:
            filepath: 文件路径
            parameters: 参数名称到值的映射

        Returns:
            bool: 导出是否成功
        """
        try:
            config_data = {
                "version": self.CONFIG_VERSION,
                "created_at": datetime.now().isoformat(),
                "parameters": parameters
            }

            # 确保目录存在
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"导出配置失败: {e}")
            return False

    def import_config(self, filepath: str) -> Optional[Dict[str, float]]:
        """
        从 JSON 文件导入配置

        Args:
            filepath: 文件路径

        Returns:
            Optional[Dict[str, float]]: 参数字典，失败返回 None
        """
        try:
            if not os.path.exists(filepath):
                print(f"配置文件不存在: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 验证配置格式
            if not self.validate_config_data(config_data):
                return None

            # 返回参数
            return config_data.get("parameters", {})

        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            return None
        except Exception as e:
            print(f"导入配置失败: {e}")
            return None

    def validate_config_file(self, filepath: str) -> bool:
        """
        验证配置文件是否有效

        Args:
            filepath: 文件路径

        Returns:
            bool: 配置文件是否有效
        """
        try:
            if not os.path.exists(filepath):
                return False

            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            return self.validate_config_data(config_data)

        except Exception:
            return False

    def validate_config_data(self, config_data: dict) -> bool:
        """
        验证配置数据格式

        Args:
            config_data: 配置数据字典

        Returns:
            bool: 配置数据是否有效
        """
        # 检查必要字段
        if "version" not in config_data:
            return False

        if "parameters" not in config_data:
            return False

        # 检查 parameters 是否为字典
        if not isinstance(config_data["parameters"], dict):
            return False

        # 检查参数值是否为数字
        for value in config_data["parameters"].values():
            if not isinstance(value, (int, float)):
                return False

        return True

    def batch_write_to_fpga(
        self,
        parameters: Dict[str, float],
        comm_model,
        isp_model
    ) -> Dict[str, bool]:
        """
        批量写入参数到 FPGA

        Args:
            parameters: 参数名称到值的映射
            comm_model: 通信模型
            isp_model: ISP 参数模型

        Returns:
            Dict[str, bool]: 每个参数的写入结果
        """
        results = {}

        for name, value in parameters.items():
            try:
                # 获取寄存器地址
                entry = isp_model.get_register(name)
                if not entry:
                    results[name] = False
                    continue

                # 写入 FPGA
                success = comm_model.write_register(entry.address, int(value))
                results[name] = success

            except Exception as e:
                print(f"写入参数 {name} 失败: {e}")
                results[name] = False

        return results

    def get_config_info(self, filepath: str) -> Optional[Dict]:
        """
        获取配置文件的元信息

        Args:
            filepath: 文件路径

        Returns:
            Optional[Dict]: 配置信息，失败返回 None
        """
        try:
            if not os.path.exists(filepath):
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            if not self.validate_config_data(config_data):
                return None

            return {
                "version": config_data.get("version"),
                "created_at": config_data.get("created_at"),
                "parameter_count": len(config_data.get("parameters", {})),
                "parameters": list(config_data.get("parameters", {}).keys())
            }

        except Exception:
            return None

    def merge_configs(
        self,
        base_config: Dict[str, float],
        override_config: Dict[str, float]
    ) -> Dict[str, float]:
        """
        合并两个配置（override 覆盖 base）

        Args:
            base_config: 基础配置
            override_config: 覆盖配置

        Returns:
            Dict[str, float]: 合并后的配置
        """
        result = base_config.copy()
        result.update(override_config)
        return result

    def filter_parameters(
        self,
        parameters: Dict[str, float],
        allowed_names: List[str]
    ) -> Dict[str, float]:
        """
        过滤参数（只保留允许的参数名）

        Args:
            parameters: 原始参数字典
            allowed_names: 允许的参数名列表

        Returns:
            Dict[str, float]: 过滤后的参数字典
        """
        return {
            name: value
            for name, value in parameters.items()
            if name in allowed_names
        }
