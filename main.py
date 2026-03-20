"""
FPGA ISP Tuner - 主程序入口
"""

import sys
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加当前目录到 sys.path
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from controller import MainController


def main():
    """应用程序主入口"""
    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("FPGA ISP Tuner")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ISP Tuning Team")

    # 设置全局字体
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    # 设置全局样式（深色主题）
    app.setStyle("Fusion")

    # 创建主控制器
    controller = MainController()

    # 运行应用
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
