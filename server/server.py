#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.vpn_server_core import VPNServerCore
from common.config import Config


def main():
    config = Config('server/config.json')
    
    host = config.get('server_host', '0.0.0.0')
    port = config.get('server_port', 8443)
    nat_interface = config.get('nat_interface', 'eth0')
    
    server = VPNServerCore(host=host, port=port, nat_interface=nat_interface)
    server.start()


if __name__ == '__main__':
    main()