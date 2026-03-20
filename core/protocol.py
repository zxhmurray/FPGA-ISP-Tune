"""
FPGA ISP Tuner - 通信协议处理器
实现帧格式: [0x5A] + [R/W Flag] + [Address 2B] + [Data 4B] + [Checksum] + [0xA5]
"""

from typing import Optional, Dict


class ProtocolHandler:
    """
    协议处理器 - 负责数据包的装包和解包
    """

    # 帧定界符
    FRAME_HEADER = 0x5A
    FRAME_END = 0xA5

    # 操作标志
    FLAG_WRITE = 0x01
    FLAG_READ = 0x02

    # 帧长度
    WRITE_FRAME_LEN = 9  # 帧头(1) + 标志(1) + 地址(2) + 数据(4) + 校验(1)
    READ_FRAME_LEN = 6   # 帧头(1) + 标志(1) + 地址(2) + 校验(1) + 帧尾(1)
    RESPONSE_FRAME_LEN = 9  # 帧头(1) + 标志(1) + 数据(4) + 校验(1) + 帧尾(1)

    @staticmethod
    def encode_write(address: int, data: int) -> bytes:
        """
        编码写寄存器数据包

        Args:
            address: 寄存器地址 (0x0000 ~ 0xFFFF)
            data: 写入数据 (32位整数)

        Returns:
            bytes: 编码后的数据包
        """
        # 构建帧（不含校验和）
        frame = bytes([
            ProtocolHandler.FRAME_HEADER,
            ProtocolHandler.FLAG_WRITE,
            (address >> 8) & 0xFF,   # Address High
            address & 0xFF,          # Address Low
            (data >> 24) & 0xFF,     # Data Byte 3
            (data >> 16) & 0xFF,     # Data Byte 2
            (data >> 8) & 0xFF,      # Data Byte 1
            data & 0xFF,              # Data Byte 0
        ])

        # 计算校验和（从 R/W Flag 到 Data 的 XOR）
        checksum = ProtocolHandler._calculate_checksum(frame[1:])

        # 添加校验和和帧尾
        return frame + bytes([checksum, ProtocolHandler.FRAME_END])

    @staticmethod
    def encode_read(address: int) -> bytes:
        """
        编码读寄存器数据包

        Args:
            address: 寄存器地址 (0x0000 ~ 0xFFFF)

        Returns:
            bytes: 编码后的数据包
        """
        # 构建帧（不含校验和）
        frame = bytes([
            ProtocolHandler.FRAME_HEADER,
            ProtocolHandler.FLAG_READ,
            (address >> 8) & 0xFF,   # Address High
            address & 0xFF,          # Address Low
        ])

        # 计算校验和（从 R/W Flag 到 Address 的 XOR）
        checksum = ProtocolHandler._calculate_checksum(frame[1:])

        # 添加校验和和帧尾
        return frame + bytes([checksum, ProtocolHandler.FRAME_END])

    @staticmethod
    def decode(data: bytes) -> Optional[Dict]:
        """
        解码数据包

        Args:
            data: 原始数据字节

        Returns:
            Optional[Dict]: 解码后的数据，失败返回 None
            {
                'flag': R/W 标志,
                'address': 地址 (仅读请求),
                'data': 数据值
            }
        """
        if len(data) < ProtocolHandler.RESPONSE_FRAME_LEN:
            return None

        # 检查帧头和帧尾
        if data[0] != ProtocolHandler.FRAME_HEADER:
            return None
        if data[-1] != ProtocolHandler.FRAME_END:
            return None

        flag = data[1]

        # 根据标志解析不同格式
        if flag == ProtocolHandler.FLAG_WRITE:
            # 写响应: [5A] [01] [00] [00] [00] [00] [Checksum] [A5]
            payload = data[2:6]  # 4字节数据
            received_checksum = data[6]

            # 验证校验和
            calculated = ProtocolHandler._calculate_checksum(bytes([flag]) + payload)
            if received_checksum != calculated:
                return None

            data_value = (payload[0] << 24) | (payload[1] << 16) | (payload[2] << 8) | payload[3]

            return {
                'flag': flag,
                'data': data_value
            }

        elif flag == ProtocolHandler.FLAG_READ:
            # 读响应: [5A] [02] [Data] [Checksum] [A5]
            payload = data[2:6]  # 4字节数据
            received_checksum = data[6]

            # 验证校验和
            calculated = ProtocolHandler._calculate_checksum(bytes([flag]) + payload)
            if received_checksum != calculated:
                return None

            data_value = (payload[0] << 24) | (payload[1] << 16) | (payload[2] << 8) | payload[3]

            return {
                'flag': flag,
                'data': data_value
            }

        return None

    @staticmethod
    def decode_request(data: bytes) -> Optional[Dict]:
        """
        解码读请求包（用于验证接收到的请求是否正确）

        Args:
            data: 原始数据字节

        Returns:
            Optional[Dict]: 解码后的数据，失败返回 None
        """
        if len(data) < ProtocolHandler.READ_FRAME_LEN:
            return None

        # 检查帧头和帧尾
        if data[0] != ProtocolHandler.FRAME_HEADER:
            return None
        if data[-1] != ProtocolHandler.FRAME_END:
            return None

        flag = data[1]
        if flag not in (ProtocolHandler.FLAG_WRITE, ProtocolHandler.FLAG_READ):
            return None

        # 解析地址
        address = (data[2] << 8) | data[3]

        # 验证校验和
        received_checksum = data[4]
        calculated = ProtocolHandler._calculate_checksum(data[1:4])
        if received_checksum != calculated:
            return None

        return {
            'flag': flag,
            'address': address
        }

    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        """
        计算 XOR 校验和

        Args:
            data: 待校验的字节数据

        Returns:
            int: 校验和 (0x00 ~ 0xFF)
        """
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum & 0xFF

    @staticmethod
    def validate_frame(data: bytes) -> bool:
        """
        验证帧格式是否正确

        Args:
            data: 原始数据字节

        Returns:
            bool: 帧格式是否有效
        """
        if len(data) < ProtocolHandler.READ_FRAME_LEN:
            return False
        if data[0] != ProtocolHandler.FRAME_HEADER:
            return False
        if data[-1] != ProtocolHandler.FRAME_END:
            return False
        return True

    @staticmethod
    def find_frame_header(data: bytes) -> int:
        """
        在数据流中查找帧头位置

        Args:
            data: 原始数据字节

        Returns:
            int: 帧头位置索引，未找到返回 -1
        """
        try:
            return data.index(ProtocolHandler.FRAME_HEADER)
        except ValueError:
            return -1

    @staticmethod
    def extract_frame(data: bytes) -> Optional[bytes]:
        """
        从数据流中提取一个完整的帧

        Args:
            data: 原始数据字节

        Returns:
            Optional[bytes]: 完整的帧数据，未找到完整帧返回 None
        """
        header_idx = ProtocolHandler.find_frame_header(data)
        if header_idx == -1:
            return None

        # 从帧头开始查找帧尾
        for i in range(header_idx + 1, len(data)):
            if data[i] == ProtocolHandler.FRAME_END:
                return data[header_idx:i + 1]

        return None
