import socket
import ssl
import select
import struct
import threading
from typing import Dict, Set, Optional
from .vpn_encryption import create_ssl_context
from .vpn_tun import create_tun, read_packet, write_packet, close_tun
from .vpn_routing import enable_nat, disable_nat


class VPNServerCore:
    def __init__(self, host: str = '0.0.0.0', port: int = 8443, nat_interface: str = 'eth0'):
        self.host = host
        self.port = port
        self.nat_interface = nat_interface
        self.tun_fd = None
        self.tun_name = None
        self.server_socket = None
        self.ssl_context = None
        self.clients: Dict[socket.socket, str] = {}
        self.ip_to_socket: Dict[str, socket.socket] = {}
        self.ip_pool_start = 10
        self.ip_pool_current = self.ip_pool_start
        self.running = False
        self.lock = threading.Lock()
    
    def _allocate_ip(self) -> str:
        with self.lock:
            ip = f'10.0.0.{self.ip_pool_current}'
            self.ip_pool_current += 1
            return ip
    
    def _setup_tun(self):
        self.tun_fd, self.tun_name = create_tun('tun0')
        import subprocess
        subprocess.run(['ip', 'addr', 'add', '10.0.0.1/24', 'dev', self.tun_name], check=True)
        subprocess.run(['ip', 'link', 'set', 'dev', self.tun_name, 'up'], check=True)
    
    def _setup_server_socket(self):
        self.ssl_context = create_ssl_context()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)
    
    def _accept_client(self):
        try:
            client_socket, addr = self.server_socket.accept()
            ssl_socket = self.ssl_context.wrap_socket(client_socket, server_side=True)
            ssl_socket.setblocking(False)
            
            client_ip = self._allocate_ip()
            
            with self.lock:
                self.clients[ssl_socket] = client_ip
                self.ip_to_socket[client_ip] = ssl_socket
            
            ip_data = client_ip.encode('utf-8')
            header = struct.pack('!I', len(ip_data))
            ssl_socket.sendall(header + ip_data)
            
            print(f'Client connected from {addr}, assigned IP: {client_ip}')
        except ssl.SSLError:
            pass
        except Exception as e:
            print(f'Error accepting client: {e}')
    
    def _handle_client_data(self, client_socket):
        try:
            data = client_socket.recv(2048)
            if not data:
                self._remove_client(client_socket)
                return
            
            write_packet(self.tun_fd, data)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except Exception as e:
            print(f'Error handling client data: {e}')
            self._remove_client(client_socket)
    
    def _handle_tun_data(self):
        try:
            packet = read_packet(self.tun_fd)
            if len(packet) < 20:
                return
            
            dst_ip = '.'.join(map(str, packet[16:20]))
            
            with self.lock:
                client_socket = self.ip_to_socket.get(dst_ip)
            
            if client_socket:
                try:
                    client_socket.sendall(packet)
                except Exception as e:
                    print(f'Error sending to client {dst_ip}: {e}')
                    self._remove_client(client_socket)
        except Exception as e:
            print(f'Error handling tun data: {e}')
    
    def _remove_client(self, client_socket):
        with self.lock:
            if client_socket in self.clients:
                client_ip = self.clients[client_socket]
                del self.clients[client_socket]
                if client_ip in self.ip_to_socket:
                    del self.ip_to_socket[client_ip]
                print(f'Client {client_ip} disconnected')
        
        try:
            client_socket.close()
        except:
            pass
    
    def start(self):
        self._setup_tun()
        self._setup_server_socket()
        enable_nat(self.nat_interface)
        
        self.running = True
        print(f'VPN Server started on {self.host}:{self.port}')
        print(f'TUN interface: {self.tun_name}')
        
        try:
            while self.running:
                with self.lock:
                    client_sockets = list(self.clients.keys())
                
                read_list = [self.server_socket, self.tun_fd] + client_sockets
                
                try:
                    readable, _, exceptional = select.select(read_list, [], read_list, 1.0)
                except Exception as e:
                    continue
                
                for s in readable:
                    if s is self.server_socket:
                        self._accept_client()
                    elif s == self.tun_fd:
                        self._handle_tun_data()
                    else:
                        self._handle_client_data(s)
                
                for s in exceptional:
                    if s != self.server_socket and s != self.tun_fd:
                        self._remove_client(s)
        
        except KeyboardInterrupt:
            print('\nShutting down...')
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        
        with self.lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
            self.ip_to_socket.clear()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if self.tun_fd is not None:
            close_tun(self.tun_fd)
        
        disable_nat(self.nat_interface)
        print('VPN Server stopped')