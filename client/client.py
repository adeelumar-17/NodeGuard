#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from client.vpn_client_core import VPNClientCore
from common.config import Config


def main():
    config = Config('client/config.json')
    
    server_host = config.get('server_host')
    server_port = config.get('server_port', 8443)
    
    if not server_host:
        print('Error: server_host not configured in config.json')
        sys.exit(1)
    
    client = VPNClientCore(server_host=server_host, server_port=server_port)
    client.start()


if __name__ == '__main__':
    main()