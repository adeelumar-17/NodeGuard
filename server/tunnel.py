import asyncio
from typing import Dict


class TunnelManager:
    def __init__(self):
        self.tunnels: Dict[str, asyncio.Task] = {}
    
    async def create_tunnel(self, client_id: str, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        pass
    
    async def destroy_tunnel(self, client_id: str):
        pass
    
    async def forward_packet(self, client_id: str, data: bytes):
        pass