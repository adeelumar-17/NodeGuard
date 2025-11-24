import asyncio
import ssl
from typing import Optional


class VPNServer:
    def __init__(self, host: str = '0.0.0.0', port: int = 8443):
        self.host = host
        self.port = port
        self.server: Optional[asyncio.Server] = None
        self.ssl_context: Optional[ssl.SSLContext] = None
    
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        pass