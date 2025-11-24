import struct
from enum import IntEnum
from typing import Tuple


class MessageType(IntEnum):
    HANDSHAKE = 1
    AUTH = 2
    DATA = 3
    KEEPALIVE = 4
    DISCONNECT = 5


class Protocol:
    HEADER_SIZE = 8
    VERSION = 1
    
    @staticmethod
    def pack_message(msg_type: MessageType, data: bytes) -> bytes:
        header = struct.pack('!HHI', Protocol.VERSION, msg_type, len(data))
        return header + data
    
    @staticmethod
    def unpack_message(data: bytes) -> Tuple[int, MessageType, bytes]:
        if len(data) < Protocol.HEADER_SIZE:
            raise ValueError('Incomplete message')
        version, msg_type, length = struct.unpack('!HHI', data[:Protocol.HEADER_SIZE])
        payload = data[Protocol.HEADER_SIZE:Protocol.HEADER_SIZE + length]
        return version, MessageType(msg_type), payload