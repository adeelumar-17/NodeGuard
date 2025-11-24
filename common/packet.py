import struct
from typing import Optional


class PacketHandler:
    @staticmethod
    def parse_ip_header(data: bytes) -> dict:
        if len(data) < 20:
            return {}
        version_ihl = data[0]
        version = version_ihl >> 4
        ihl = (version_ihl & 0xF) * 4
        ttl = data[8]
        protocol = data[9]
        src_addr = '.'.join(map(str, data[12:16]))
        dst_addr = '.'.join(map(str, data[16:20]))
        return {
            'version': version,
            'ihl': ihl,
            'ttl': ttl,
            'protocol': protocol,
            'src': src_addr,
            'dst': dst_addr
        }
    
    @staticmethod
    def validate_packet(data: bytes) -> bool:
        if len(data) < 20:
            return False
        header = PacketHandler.parse_ip_header(data)
        return header.get('version') == 4