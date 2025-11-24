import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from client import VPNClientCore


class ClientCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VPN Client')
        self.parser.add_argument('--host', required=True, help='Server host')
        self.parser.add_argument('--port', type=int, default=8443, help='Server port')
    
    def run(self, args):
        client = VPNClientCore(server_host=args.host, server_port=args.port)
        client.start()
    
    def main(self):
        args = self.parser.parse_args()
        self.run(args)


if __name__ == '__main__':
    cli = ClientCLI()
    cli.main()