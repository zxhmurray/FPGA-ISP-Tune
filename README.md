# FPGA ISP Tuner

<!-- 徽章区域 -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20|%20Windows%20|%20Linux-green.svg)]()

---

## 1. 项目简介 (Project Overview)

### 1.1 是什么？
FPGA ISP Tuner 是一款跨平台桌面应用程序，用于通过 UART 串口实时调整 FPGA 内部 ISP（Image Signal Processing）算法模块的寄存器参数。

### 1.2 能做什么？
- **串口通信**: 通过 UART 连接 FPGA 开发板，支持自动重连
- **参数调节**: 支持调节 BLC、AWB、Gamma、Contrast、Saturation、Sharpness 等 ISP 参数
- **实时预览**: 实时显示图像直方图和预览画面
- **配置管理**: 支持导入/导出 JSON 格式配置文件
- **日志记录**: 完整记录通信数据和系统操作日志

### 1.3 截图
<!-- 插入软件截图 -->

---

## 2. 架构 (Architecture)

### 2.1 技术栈
| 层级 | 技术 |
|------|------|
| GUI 框架 | PyQt6 |
| 编程语言 | Python 3.10+ |
| 通信协议 | UART (pyserial) |
| 图像处理 | OpenCV |

### 2.2 MVC 架构
```
┌─────────────────────────────────────────────────────────────┐
│                         View (UI)                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │
│  │Toolbar  │ │Connection│ │Parameter│ │Preview  │ │ Hist  │ │
│  │         │ │ Panel    │ │ Panel   │ │ Panel   │ │ Panel │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Controller                              │
│                   MainController                             │
│  - 处理 UI 事件                                              │
│  - 协调 Model 层                                             │
│  - 管理应用状态                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Model                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │CommunicationModel│  │ISPParametersModel│  │ConfigManager│
│  │ - Serial I/O     │  │ - Register Map   │  │ - JSON I/O │ │
│  │ - Protocol       │  │ - Parameter CRUD │  │            │ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 模块说明
- **core/** - 核心业务逻辑 (通信、协议、参数模型)
- **ui/** - 用户界面
- **controller/** - 控制器
- **utils/** - 工具模块

---

## 3. 快速开始 (Quick Start)

### 3.1 环境要求
- Python 3.10+
- macOS / Windows / Linux

### 3.2 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/FPGA-ISP-Tuner-GUI.git
cd FPGA-ISP-Tuner-GUI

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3.3 运行

```bash
python main.py
```

---

## 4. 使用指南 (Usage)

### 4.1 连接设备
1. 选择正确的串口号
2. 设置波特率（默认 115200）
3. 点击"连接"按钮

### 4.2 调节参数
1. 在参数面板中选择要调节的 ISP 模块
2. 拖动滑动条或直接输入数值
3. 参数会实时发送到 FPGA

### 4.3 配置管理
- **导入**: 点击"导入"加载 JSON 配置文件
- **导出**: 点击"导出"保存当前参数到 JSON 文件

---

## 5. 通信协议 (Protocol)

### 5.1 数据包格式
```
[0x5A] + [R/W] + [Address 2B] + [Data 4B] + [Checksum] + [0xA5]
```

### 5.2 寄存器映射
| 参数 | 地址 | 说明 |
|------|------|------|
| BLC | 0x0000 | 黑电平校正 |
| AWB R/G/B | 0x0010-0x0012 | 白平衡增益 |
| Gamma | 0x0020 | Gamma 校正 |

---

## 6. 项目结构 (Project Structure)

```
FPGA-ISP-Tuner-GUI/
├── main.py                 # 入口
├── requirements.txt        # 依赖
├── config/
│   └── register_map.json   # 寄存器映射
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── communication.py
│   ├── isp_parameters.py
│   └── protocol.py
├── controller/             # 控制器
│   ├── __init__.py
│   └── main_controller.py
├── ui/                    # UI 模块
│   ├── __init__.py
│   ├── connection_panel.py
│   ├── histogram_panel.py
│   ├── log_panel.py
│   ├── main_window.py
│   ├── parameter_panel.py
│   ├── preview_panel.py
│   ├── toolbar.py
│   └── widgets/
│       ├── __init__.py
│       └── parameter_slider.py
└── utils/                 # 工具模块
    ├── __init__.py
    ├── config_manager.py
    └── logger.py
```

---

## 7. 贡献指南 (Contributing)

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 8. 开源协议 (License)

本项目基于 [MIT License](LICENSE) 开源。

---

## 9. 联系方式 (Contact)

- 项目主页: https://github.com/YOUR_USERNAME/FPGA-ISP-Tuner-GUI
- 问题反馈: [Issues](https://github.com/YOUR_USERNAME/FPGA-ISP-Tuner-GUI/issues)

---

## 10. 致谢 (Acknowledgments)

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- [OpenCV](https://opencv.org/)
- [pyserial](https://github.com/pyserial/pyserial)