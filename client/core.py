import asyncio
import ssl
from typing import Optional


class VPNClient:
    def __init__(self, server_host: str, server_port: int = 8443):
        self.server_host = server_host
        self.server_port = server_port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.ssl_context: Optional[ssl.SSLContext] = None
    
    async def connect(self):
        pass
    
    async def disconnect(self):
        pass
    
    async def send_data(self, data: bytes):
        pass
    
    async def receive_data(self) -> bytes:
        return b''