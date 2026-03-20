"""
FPGA ISP Tuner - 通信模型
管理 UART 串口连接、协议收发、读写线程
"""

import queue
import threading
from typing import Optional, List, Dict

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

from .protocol import ProtocolHandler


class SerialReadThread(QThread):
    """
    独立串口读取线程
    避免阻塞主 UI 线程
    """

    # 信号：收到原始数据
    data_received = pyqtSignal(bytes)

    def __init__(self, serial_port: QSerialPort):
        super().__init__()
        self._serial_port = serial_port
        self._running = False
        self._buffer = bytearray()

    def run(self):
        """后台读取循环"""
        self._running = True
        while self._running:
            try:
                if self._serial_port and self._serial_port.isOpen():
                    # 读取所有可用数据
                    while self._serial_port.bytesAvailable() > 0:
                        data = self._serial_port.read(1024)
                        if data:
                            self._buffer.extend(data)

                    # 尝试解析完整帧
                    while len(self._buffer) >= ProtocolHandler.RESPONSE_FRAME_LEN:
                        # 查找帧头
                        header_idx = -1
                        for i in range(len(self._buffer)):
                            if self._buffer[i] == ProtocolHandler.FRAME_HEADER:
                                header_idx = i
                                break

                        if header_idx == -1:
                            # 没有帧头，清除所有数据
                            self._buffer.clear()
                            break

                        if header_idx > 0:
                            # 移除帧头前的垃圾数据
                            del self._buffer[:header_idx]

                        if len(self._buffer) < ProtocolHandler.RESPONSE_FRAME_LEN:
                            # 数据不完整，等待更多数据
                            break

                        # 查找帧尾
                        frame_end_idx = -1
                        for i in range(1, len(self._buffer)):
                            if self._buffer[i] == ProtocolHandler.FRAME_END:
                                frame_end_idx = i
                                break

                        if frame_end_idx == -1:
                            # 没有找到帧尾，等待更多数据
                            break

                        # 提取完整帧
                        frame = bytes(self._buffer[:frame_end_idx + 1])
                        del self._buffer[:frame_end_idx + 1]

                        # 发出数据信号
                        self.data_received.emit(frame)

                # 避免 CPU 占用过高
                self.msleep(10)

            except Exception as e:
                self._running = False
                break

    def stop(self):
        """停止读取线程"""
        self._running = False
        self.wait()


class SerialWriteQueue:
    """
    串口写入队列
    保证写入顺序，FIFO
    """

    def __init__(self, serial_port: QSerialPort):
        self._serial_port = serial_port
        self._queue = queue.Queue()
        self._running = True
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

    def enqueue(self, data: bytes):
        """加入写入队列"""
        self._queue.put(data)

    def _process_queue(self):
        """后台处理写入队列"""
        while self._running:
            try:
                data = self._queue.get(timeout=0.1)
                if self._serial_port and self._serial_port.isOpen():
                    self._serial_port.write(data)
            except queue.Empty:
                continue
            except Exception:
                pass

    def stop(self):
        """停止写入队列"""
        self._running = False
        self._thread.join(timeout=1.0)


class CommunicationModel(QObject):
    """
    通信模型 - 负责所有串口通信相关操作

    Signals:
        data_received: 收到原始数据 (bytes)
        register_read_response: 寄存器读响应 (address: int, value: int)
        connection_status_changed: 连接状态变化 (is_connected: bool, port_name: str)
        error_occurred: 错误发生 (error_msg: str)
        log_message: 日志消息 (level: str, message: str)
    """

    # Qt Signals
    data_received = pyqtSignal(bytes)
    register_read_response = pyqtSignal(int, int)
    connection_status_changed = pyqtSignal(bool, str)
    error_occurred = pyqtSignal(str)
    log_message = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._serial_port: Optional[QSerialPort] = None
        self._read_thread: Optional[SerialReadThread] = None
        self._write_queue: Optional[SerialWriteQueue] = None
        self._is_connected = False
        self._current_port = ""
        self._current_baudrate = 115200

    # ==================== Properties ====================

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._is_connected

    @property
    def current_port(self) -> str:
        """当前端口名"""
        return self._current_port

    @property
    def current_baudrate(self) -> int:
        """当前波特率"""
        return self._current_baudrate

    # ==================== Port Management ====================

    def list_available_ports(self) -> List[str]:
        """
        扫描并返回可用串口列表

        Returns:
            List[str]: 可用端口名列表
        """
        ports = []
        for info in QSerialPortInfo.availablePorts():
            ports.append(info.portName())
        return ports

    def connect(self, port: str, baudrate: int = 115200, **kwargs) -> bool:
        """
        连接到串口

        Args:
            port: 端口名（如 "COM1", "/dev/ttyUSB0"）
            baudrate: 波特率（默认 115200）
            **kwargs: 其他串口参数
                - data_bits: 数据位 (5, 6, 7, 8)
                - parity: 校验位 ("N", "E", "O")
                - stop_bits: 停止位 (1, 1.5, 2)

        Returns:
            bool: 连接是否成功
        """
        if self._is_connected:
            self.disconnect()

        try:
            # 创建串口对象
            self._serial_port = QSerialPort(port)
            self._serial_port.setBaudRate(baudrate)

            # 设置数据位
            data_bits = kwargs.get('data_bits', 8)
            self._serial_port.setDataBits(QSerialPort.DataBits.Data8)
            if data_bits == 7:
                self._serial_port.setDataBits(QSerialPort.DataBits.Data7)
            elif data_bits == 6:
                self._serial_port.setDataBits(QSerialPort.DataBits.Data6)
            elif data_bits == 5:
                self._serial_port.setDataBits(QSerialPort.DataBits.Data5)

            # 设置校验位
            parity = kwargs.get('parity', 'N')
            if parity == 'E':
                self._serial_port.setParity(QSerialPort.Parity.EvenParity)
            elif parity == 'O':
                self._serial_port.setParity(QSerialPort.Parity.OddParity)
            else:
                self._serial_port.setParity(QSerialPort.Parity.NoParity)

            # 设置停止位
            stop_bits = kwargs.get('stop_bits', 1)
            if stop_bits == 2:
                self._serial_port.setStopBits(QSerialPort.StopBits.TwoStop)
            elif stop_bits == 1.5:
                self._serial_port.setStopBits(QSerialPort.StopBits.OneAndHalfStop)
            else:
                self._serial_port.setStopBits(QSerialPort.StopBits.OneStop)

            # 设置流控制
            self._serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

            # 打开串口
            if not self._serial_port.open(QSerialPort.OpenModeFlag.ReadWrite):
                self.error_occurred.emit(f"无法打开端口 {port}")
                self.log_message.emit("ERROR", f"无法打开端口 {port}")
                return False

            # 启动读取线程
            self._read_thread = SerialReadThread(self._serial_port)
            self._read_thread.data_received.connect(self._on_data_received)
            self._read_thread.start()

            # 启动写入队列
            self._write_queue = SerialWriteQueue(self._serial_port)

            # 更新状态
            self._is_connected = True
            self._current_port = port
            self._current_baudrate = baudrate

            # 发出信号
            self.connection_status_changed.emit(True, port)
            self.log_message.emit("INFO", f"已连接到 {port} @ {baudrate}")

            return True

        except Exception as e:
            self.error_occurred.emit(f"连接失败: {str(e)}")
            self.log_message.emit("ERROR", f"连接失败: {str(e)}")
            self._cleanup()
            return False

    def disconnect(self):
        """断开串口连接"""
        self._cleanup()
        self.connection_status_changed.emit(False, "")
        self.log_message.emit("INFO", "已断开连接")

    def _cleanup(self):
        """清理资源"""
        # 停止读取线程
        if self._read_thread:
            self._read_thread.stop()
            self._read_thread = None

        # 停止写入队列
        if self._write_queue:
            self._write_queue.stop()
            self._write_queue = None

        # 关闭串口
        if self._serial_port:
            if self._serial_port.isOpen():
                self._serial_port.close()
            self._serial_port = None

        # 重置状态
        self._is_connected = False
        self._current_port = ""

    # ==================== Data Transmission ====================

    def write_register(self, address: int, value: int, timeout_ms: int = 1000) -> bool:
        """
        写入寄存器

        Args:
            address: 寄存器地址
            value: 写入值
            timeout_ms: 超时时间（毫秒）

        Returns:
            bool: 写入是否成功
        """
        if not self._is_connected or not self._serial_port:
            self.error_occurred.emit("未连接设备")
            return False

        try:
            # 编码数据包
            frame = ProtocolHandler.encode_write(address, value)

            # 发送到写入队列
            if self._write_queue:
                self._write_queue.enqueue(frame)

            self.log_message.emit("DEBUG", f"写入寄存器: ADDR=0x{address:04X}, VAL=0x{value:08X}")
            return True

        except Exception as e:
            self.error_occurred.emit(f"写入失败: {str(e)}")
            self.log_message.emit("ERROR", f"写入寄存器失败: {str(e)}")
            return False

    def read_register(self, address: int, timeout_ms: int = 1000) -> Optional[int]:
        """
        读取寄存器

        Args:
            address: 寄存器地址
            timeout_ms: 超时时间（毫秒）

        Returns:
            Optional[int]: 读取的值，超时返回 None
        """
        if not self._is_connected or not self._serial_port:
            self.error_occurred.emit("未连接设备")
            return None

        try:
            # 编码读请求
            frame = ProtocolHandler.encode_read(address)

            # 发送到写入队列
            if self._write_queue:
                self._write_queue.enqueue(frame)

            self.log_message.emit("DEBUG", f"读取寄存器: ADDR=0x{address:04X}")
            return None  # 异步读取，结果通过信号返回

        except Exception as e:
            self.error_occurred.emit(f"读取失败: {str(e)}")
            self.log_message.emit("ERROR", f"读取寄存器失败: {str(e)}")
            return None

    def send_raw_data(self, data: bytes) -> bool:
        """
        发送原始数据

        Args:
            data: 原始字节数据

        Returns:
            bool: 发送是否成功
        """
        if not self._is_connected or not self._write_queue:
            return False

        try:
            self._write_queue.enqueue(data)
            return True
        except Exception:
            return False

    # ==================== Private Methods ====================

    def _on_data_received(self, data: bytes):
        """
        处理收到的数据

        Args:
            data: 原始数据帧
        """
        # 发出原始数据信号
        self.data_received.emit(data)

        # 尝试解码
        decoded = ProtocolHandler.decode(data)
        if decoded:
            if decoded['flag'] == ProtocolHandler.FLAG_READ:
                # 读响应
                self.register_read_response.emit(decoded.get('address', 0), decoded['data'])
                self.log_message.emit(
                    "DEBUG",
                    f"读响应: DATA=0x{decoded['data']:08X}"
                )
