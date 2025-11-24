import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server import VPNServerCore


class ServerCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VPN Server')
        self.parser.add_argument('--host', default='0.0.0.0', help='Server host')
        self.parser.add_argument('--port', type=int, default=8443, help='Server port')
        self.parser.add_argument('--nat-interface', default='eth0', help='NAT interface')
    
    def run(self, args):
        server = VPNServerCore(host=args.host, port=args.port, nat_interface=args.nat_interface)
        server.start()
    
    def main(self):
        args = self.parser.parse_args()
        self.run(args)


if __name__ == '__main__':
    cli = ServerCLI()
    cli.main()