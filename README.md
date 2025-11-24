# Secure VPN

A modular, secure VPN implementation in Python 3.10+.

## Project Structure

```
secure-vpn/
├── server/          # Server-side components
│   ├── core.py      # Main server logic
│   ├── auth.py      # Authentication manager
│   ├── tunnel.py    # Tunnel management
│   └── server.py    # Server entry point
├── client/          # Client-side components
│   ├── core.py      # Main client logic
│   ├── connection.py # Connection manager
│   ├── interface.py  # Network interface handling
│   └── client.py    # Client entry point
├── common/          # Shared components
│   ├── protocol.py  # Protocol definitions
│   ├── crypto.py    # Cryptographic operations
│   ├── packet.py    # Packet handling
│   └── config.py    # Configuration management
├── cli/             # Command-line interfaces
│   ├── server_cli.py
│   └── client_cli.py
├── certificates/    # SSL/TLS certificates
└── scripts/         # Utility scripts
    └── generate_certs.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Generate certificates:
```bash
python scripts/generate_certs.py
```

Start server:
```bash
python server/server.py --host 0.0.0.0 --port 8443
```

Connect client:
```bash
python client/client.py --host <server-ip> --port 8443
```