"""
FPGA ISP Tuner - 日志面板
日志输出显示
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QTextCursor, QColor
from PyQt6.QtCore import Qt


class LogPanel(QWidget):
    """
    日志面板 - 显示通信日志和系统消息

    日志级别:
        DEBUG - 调试信息 (灰色)
        INFO  - 一般信息 (白色)
        WARNING - 警告信息 (黄色/橙色)
        ERROR - 错误信息 (红色)
    """

    # 日志级别定义
    LEVEL_DEBUG = "DEBUG"
    LEVEL_INFO = "INFO"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"

    # 日志级别颜色
    COLORS = {
        LEVEL_DEBUG: "#808080",   # 灰色
        LEVEL_INFO: "#FFFFFF",    # 白色
        LEVEL_WARNING: "#FFA500", # 橙色
        LEVEL_ERROR: "#FF4444",   # 红色
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._max_lines = 1000  # 最大日志行数
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        title_label = QLabel("<h3>日志输出</h3>")
        layout.addWidget(title_label)

        # 日志显示区域
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        # 限制最大行数 - 使用 document()
        self._log_text.document().setMaximumBlockCount(self._max_lines)
        self._log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self._log_text)

    def _format_message(self, level: str, message: str, timestamp: str = None) -> str:
        """
        格式化日志消息

        Args:
            level: 日志级别
            message: 日志消息
            timestamp: 时间戳（可选）

        Returns:
            str: HTML 格式的消息
        """
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        color = self.COLORS.get(level, self.COLORS[self.LEVEL_INFO])
        return f'<span style="color: #808080;">[{timestamp}]</span> <span style="color: {color};">[{level:8s}]</span> {message}'

    def append_log(self, level: str, message: str):
        """
        添加日志消息

        Args:
            level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
            message: 日志消息
        """
        # 验证级别
        if level not in self.COLORS:
            level = self.LEVEL_INFO

        # 格式化并追加
        formatted = self._format_message(level, message)
        self._log_text.append(formatted)

        # 滚动到最新
        cursor = self._log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log_text.setTextCursor(cursor)

    def debug(self, message: str):
        """添加调试日志"""
        self.append_log(self.LEVEL_DEBUG, message)

    def info(self, message: str):
        """添加信息日志"""
        self.append_log(self.LEVEL_INFO, message)

    def warning(self, message: str):
        """添加警告日志"""
        self.append_log(self.LEVEL_WARNING, message)

    def error(self, message: str):
        """添加错误日志"""
        self.append_log(self.LEVEL_ERROR, message)

    def clear_log(self):
        """清空日志"""
        self._log_text.clear()

    def get_log_count(self) -> int:
        """
        获取当前日志行数

        Returns:
            int: 日志行数
        """
        return self._log_text.document().blockCount()

    def set_max_lines(self, max_lines: int):
        """
        设置最大日志行数

        Args:
            max_lines: 最大行数
        """
        self._max_lines = max_lines
        self._log_text.setMaximumBlockCount(max_lines)

    def export_log(self, filepath: str) -> bool:
        """
        导出日志到文件

        Args:
            filepath: 文件路径

        Returns:
            bool: 是否成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._log_text.toPlainText())
            return True
        except Exception:
            return False

    def get_all_text(self) -> str:
        """
        获取所有日志文本

        Returns:
            str: 所有日志内容
        """
        return self._log_text.toPlainText()
