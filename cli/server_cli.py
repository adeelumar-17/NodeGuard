import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server import VPNServer


class ServerCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VPN Server')
        self.parser.add_argument('--host', default='0.0.0.0', help='Server host')
        self.parser.add_argument('--port', type=int, default=8443, help='Server port')
        self.parser.add_argument('--cert', help='SSL certificate path')
        self.parser.add_argument('--key', help='SSL key path')
    
    async def run(self, args):
        server = VPNServer(host=args.host, port=args.port)
        await server.start()
    
    def main(self):
        args = self.parser.parse_args()
        asyncio.run(self.run(args))


if __name__ == '__main__':
    cli = ServerCLI()
    cli.main()