# Secure VPN

A lightweight, secure VPN implementation in Python with TLS 1.3 encryption and TUN interface support.

## Overview

This VPN creates encrypted tunnels between clients and a central server, routing all client traffic through the server. The implementation uses:

- TLS 1.3 for transport encryption
- TUN virtual network interfaces for packet handling
- Certificate-based mutual authentication
- IP address assignment and NAT traversal

## Features

- **Secure**: TLS 1.3 with mutual certificate authentication
- **Lightweight**: Minimal dependencies, pure Python implementation
- **Flexible**: LAN and cloud deployment modes
- **CLI Tool**: Simple command-line interface for connection management
- **IPv4**: Full IPv4 packet routing with automatic NAT configuration

## Architecture

```
secure-vpn/
├── server/              # Server implementation
│   ├── vpn_server_core.py
│   ├── vpn_encryption.py
│   ├── vpn_tun.py
│   ├── vpn_routing.py
│   ├── server.py
│   └── config.json
├── client/              # Client implementation
│   ├── vpn_client_core.py
│   ├── vpn_encryption.py
│   ├── vpn_tun.py
│   ├── vpn_routing.py
│   ├── client.py
│   └── config.json
├── common/              # Shared components
│   ├── cert_generation.py
│   └── config.py
├── cli/                 # Command-line interface
│   └── vpn_cli.py
└── certificates/        # TLS certificates
```

## Requirements

**System Requirements:**
- Linux (TUN/TAP support required)
- Root/sudo access (for TUN interface and routing)
- Python 3.10+

**Python Dependencies:**
```bash
pip install -r requirements.txt
```

**System Packages:**
```bash
apt-get install iptables iproute2
```

## Certificate Generation

Generate certificates before first use:

```bash
python scripts/generate_certs.py
```

This creates:
- `certificates/ca.crt` - Certificate Authority
- `certificates/server.crt/key` - Server certificate
- `certificates/client.crt/key` - Client certificate

## Server Setup

### LAN Mode

**1. Create server configuration:**

Create `server/config.json`:
```json
{
  "server_host": "0.0.0.0",
  "server_port": 8443,
  "nat_interface": "eth0"
}
```

**2. Start server:**
```bash
sudo python server/server.py
```

Server listens on all interfaces. Clients connect using the server's LAN IP (e.g., 192.168.1.100).

### Cloud Mode

**1. Configure cloud server:**

Create `server/config.json`:
```json
{
  "server_host": "0.0.0.0",
  "server_port": 8443,
  "nat_interface": "eth0"
}
```

Replace `eth0` with your cloud provider's primary network interface.

**2. Configure firewall:**
```bash
ufw allow 8443/tcp
```

**3. Start server:**
```bash
sudo python server/server.py
```

**4. Enable IP forwarding (if not persistent):**
```bash
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p
```

## Client Setup

### Direct Connection

**1. Create client configuration:**

Create `client/config.json`:
```json
{
  "server_host": "SERVER_IP",
  "server_port": 8443
}
```

**2. Connect:**
```bash
sudo python client/client.py
```

### CLI Tool

**Connect:**
```bash
sudo python cli/vpn_cli.py connect --server SERVER_IP
```

**Check status:**
```bash
python cli/vpn_cli.py status
```

**Disconnect:**
```bash
sudo python cli/vpn_cli.py disconnect
```

## Network Configuration

### Server Network

- Server IP: `10.0.0.1/24`
- Client IP Pool: `10.0.0.10` - `10.0.0.254`
- TUN Interface: `tun0`

### NAT and Routing

The server automatically configures:
- IP forwarding
- iptables MASQUERADE for NAT
- Forwarding rules between TUN and external interface

### Client Routing

The client automatically:
- Creates TUN interface with assigned IP
- Adds route for VPN subnet (10.0.0.0/24)
- Does NOT route all traffic by default

To route all traffic through VPN:
```bash
ip route add default via 10.0.0.1 dev tun0 metric 100
```

## Troubleshooting

### Permission Denied

**Problem:** Cannot create TUN interface

**Solution:** Run with sudo/root privileges
```bash
sudo python server/server.py
sudo python client/client.py
```

### Certificate Errors

**Problem:** SSL handshake failures

**Solution:** Regenerate certificates and ensure all hosts use the same CA:
```bash
python scripts/generate_certs.py
```

Copy certificates to all machines maintaining directory structure.

### Connection Refused

**Problem:** Client cannot connect to server

**Solution:**
1. Verify server is running: `netstat -tlnp | grep 8443`
2. Check firewall: `sudo ufw status`
3. Test connectivity: `telnet SERVER_IP 8443`

### No Internet Access

**Problem:** Connected but no internet through VPN

**Solution:**
1. Verify server IP forwarding: `sysctl net.ipv4.ip_forward`
2. Check NAT rules: `iptables -t nat -L -n -v`
3. Verify `nat_interface` matches server's external interface
4. Ensure client routes traffic through VPN

### TUN Interface Not Created

**Problem:** `/dev/net/tun` not accessible

**Solution:**
```bash
modprobe tun
ls -la /dev/net/tun
```

### Process Already Running

**Problem:** CLI reports already connected but VPN not working

**Solution:**
```bash
python cli/vpn_cli.py disconnect
rm ~/.vpn_state.json
```

### MTU Issues

**Problem:** Some websites work, others timeout

**Solution:** Reduce MTU on TUN interface:
```bash
ip link set dev tun0 mtu 1400
```

## Performance Notes

- Expected throughput: 50-200 Mbps (depends on CPU)
- Latency overhead: 1-5ms
- CPU usage scales with traffic volume

## Security Considerations

- Certificates use 4096-bit RSA keys
- TLS 1.3 only, older versions disabled
- Mutual certificate authentication required
- No password-based authentication
- Private keys stored unencrypted (secure storage recommended)

## License

This project is provided as-is for educational and internal use.