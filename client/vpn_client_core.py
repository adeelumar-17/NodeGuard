import socket
import ssl
import select
import struct
import subprocess
from typing import Optional
from .vpn_encryption import create_ssl_context
from .vpn_tun import create_tun, read_packet, write_packet, close_tun
from .vpn_routing import add_route_default, remove_route_default


class VPNClientCore:
    def __init__(self, server_host: str, server_port: int = 8443):
        self.server_host = server_host
        self.server_port = server_port
        self.tun_fd = None
        self.tun_name = None
        self.client_socket = None
        self.ssl_context = None
        self.assigned_ip = None
        self.running = False
    
    def _setup_tun(self):
        self.tun_fd, self.tun_name = create_tun('tun0')
    
    def _configure_tun_interface(self):
        import subprocess

        if not self.assigned_ip:
            raise RuntimeError('No IP assigned')

        # Add IP address
        try:
            subprocess.run(
                ['ip', 'addr', 'add', f'{self.assigned_ip}/24', 'dev', self.tun_name],
                check=True
            )
        except subprocess.CalledProcessError as e:
            if "File exists" in str(e):
                print(f"[Warning] IP {self.assigned_ip} already assigned to {self.tun_name}")
            else:
                print(f"[Error] Failed to assign IP: {e}")
                raise

        # Bring interface up
        try:
            subprocess.run(
                ['ip', 'link', 'set', 'dev', self.tun_name, 'up'],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[Error] Failed to bring interface up: {e}")
            raise

        # Add VPN route
        try:
            # Delete old route first (safe)
            subprocess.run(
                ['ip', 'route', 'del', '10.0.0.0/24', 'dev', self.tun_name],
                check=False
            )
            subprocess.run(
                ['ip', 'route', 'add', '10.0.0.0/24', 'dev', self.tun_name],
                check=True
            )
        except subprocess.CalledProcessError as e:
            if "File exists" in str(e):
                print(f"[Warning] Route 10.0.0.0/24 already exists")
            else:
                print(f"[Error] Failed to add VPN route: {e}")
                raise

    
    def _connect_to_server(self):
        self.ssl_context = create_ssl_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = self.ssl_context.wrap_socket(
            sock, 
            server_side=False,
            server_hostname=self.server_host
        )
        self.client_socket.connect((self.server_host, self.server_port))
        self.client_socket.setblocking(False)
    
    def _receive_ip_assignment(self):
        self.client_socket.setblocking(True)
        
        header = self.client_socket.recv(4)
        if len(header) != 4:
            raise RuntimeError('Failed to receive IP assignment header')
        
        ip_len = struct.unpack('!I', header)[0]
        ip_data = self.client_socket.recv(ip_len)
        if len(ip_data) != ip_len:
            raise RuntimeError('Failed to receive IP assignment data')
        
        self.assigned_ip = ip_data.decode('utf-8')
        self.client_socket.setblocking(False)
        
        print(f'Assigned IP: {self.assigned_ip}')
    
    def _handle_tun_data(self):
        try:
            packet = read_packet(self.tun_fd)
            if packet:
                self.client_socket.sendall(packet)
        except ssl.SSLWantWriteError:
            pass
        except Exception as e:
            print(f'Error handling tun data: {e}')
            raise
    
    def _handle_server_data(self):
        try:
            data = self.client_socket.recv(2048)
            if not data:
                print('Server closed connection')
                self.running = False
                return
            
            write_packet(self.tun_fd, data)
        except ssl.SSLWantReadError:
            pass
        except Exception as e:
            print(f'Error handling server data: {e}')
            raise
    
    def start(self):
        try:
            self._setup_tun()
            self._connect_to_server()
            self._receive_ip_assignment()
            self._configure_tun_interface()
            
            self.running = True
            print(f'Connected to VPN server at {self.server_host}:{self.server_port}')
            print(f'TUN interface: {self.tun_name}')
            
            while self.running:
                read_list = [self.tun_fd, self.client_socket]
                
                try:
                    readable, _, exceptional = select.select(read_list, [], read_list, 1.0)
                except Exception as e:
                    continue
                
                for s in readable:
                    if s == self.tun_fd:
                        self._handle_tun_data()
                    elif s == self.client_socket:
                        self._handle_server_data()
                
                if exceptional:
                    print('Socket error detected')
                    break
        
        except KeyboardInterrupt:
            print('\nDisconnecting...')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        if self.tun_fd is not None:
            try:
                subprocess.run(['ip', 'route', 'del', '10.0.0.0/24', 'dev', self.tun_name], check=False)
            except:
                pass
            close_tun(self.tun_fd)
        
        print('VPN Client stopped')
