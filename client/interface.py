import asyncio
from typing import Optional


class NetworkInterface:
    def __init__(self, interface_name: str = 'tun0'):
        self.interface_name = interface_name
        self.fd: Optional[int] = None
    
    async def create_interface(self):
        pass
    
    async def destroy_interface(self):
        pass
    
    async def read_packet(self) -> bytes:
        return b''
    
    async def write_packet(self, data: bytes):
        pass