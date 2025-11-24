import os
import fcntl
import struct
from typing import Tuple


TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


def create_tun(name: str = 'tun0') -> Tuple[int, str]:
    tun_fd = os.open('/dev/net/tun', os.O_RDWR)
    
    ifr = struct.pack('16sH', name.encode('utf-8'), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun_fd, TUNSETIFF, ifr)
    
    return tun_fd, name


def read_packet(tun_fd: int, buffer_size: int = 2048) -> bytes:
    return os.read(tun_fd, buffer_size)


def write_packet(tun_fd: int, packet: bytes) -> int:
    return os.write(tun_fd, packet)


def close_tun(tun_fd: int):
    os.close(tun_fd)