"""
FPGA ISP Tuner - 日志工具
应用程序日志记录
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    """
    日志工具类

    提供统一的日志记录接口，支持控制台和文件输出
    """

    # 日志级别映射
    LEVEL_DEBUG = logging.DEBUG
    LEVEL_INFO = logging.INFO
    LEVEL_WARNING = logging.WARNING
    LEVEL_ERROR = logging.ERROR

    def __init__(self):
        self._logger = None
        self._log_file = None
        self._console_handler = None
        self._file_handler = None

    def setup_logger(
        self,
        name: str = "fpga_isp_tuner",
        level: int = logging.DEBUG,
        log_file: str = None
    ):
        """
        配置日志记录器

        Args:
            name: 日志记录器名称
            level: 日志级别
            log_file: 日志文件路径（可选）
        """
        # 创建 logger
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] [%(levelname)-8s] %(message)s',
            datefmt='%H:%M:%S'
        )

        # 控制台处理器
        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setLevel(level)
        self._console_handler.setFormatter(formatter)
        self._logger.addHandler(self._console_handler)

        # 文件处理器（可选）
        if log_file:
            self._setup_file_handler(log_file, level, formatter)

    def _setup_file_handler(
        self,
        log_file: str,
        level: int,
        formatter: logging.Formatter
    ):
        """
        设置文件处理器

        Args:
            log_file: 日志文件路径
            level: 日志级别
            formatter: 格式化器
        """
        try:
            # 确保目录存在
            directory = os.path.dirname(log_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # 使用 RotatingFileHandler 支持日志轮转
            # 单个文件最大 10MB，最多保留 5 个备份
            self._file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            self._file_handler.setLevel(level)
            self._file_handler.setFormatter(formatter)
            self._logger.addHandler(self._file_handler)
            self._log_file = log_file

        except Exception as e:
            print(f"创建日志文件处理器失败: {e}")

    def debug(self, message: str):
        """记录调试信息"""
        if self._logger:
            self._logger.debug(message)

    def info(self, message: str):
        """记录一般信息"""
        if self._logger:
            self._logger.info(message)

    def warning(self, message: str):
        """记录警告信息"""
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str):
        """记录错误信息"""
        if self._logger:
            self._logger.error(message)

    def critical(self, message: str):
        """记录严重错误信息"""
        if self._logger:
            self._logger.critical(message)

    def set_level(self, level: int):
        """
        设置日志级别

        Args:
            level: 日志级别
        """
        if self._logger:
            self._logger.setLevel(level)
            if self._console_handler:
                self._console_handler.setLevel(level)
            if self._file_handler:
                self._file_handler.setLevel(level)

    def get_log_file(self) -> str:
        """
        获取日志文件路径

        Returns:
            str: 日志文件路径
        """
        return self._log_file or ""

    def close(self):
        """关闭日志处理器"""
        if self._logger:
            for handler in self._logger.handlers[:]:
                handler.close()
                self._logger.removeHandler(handler)


# 全局日志实例
_global_logger = None


def get_logger() -> Logger:
    """
    获取全局日志实例

    Returns:
        Logger: 全局日志实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger


def setup_logging(
    name: str = "fpga_isp_tuner",
    level: int = logging.DEBUG,
    log_file: str = None
):
    """
    初始化全局日志

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径（可选）
    """
    global _global_logger
    _global_logger = Logger()
    _global_logger.setup_logger(name, level, log_file)
