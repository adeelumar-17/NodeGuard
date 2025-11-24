#!/usr/bin/env python3

import argparse
import subprocess
import sys
import signal
import os
import json
from pathlib import Path


class VPNState:
    STATE_FILE = Path.home() / '.vpn_state.json'
    
    @classmethod
    def save(cls, pid, server):
        cls.STATE_FILE.write_text(json.dumps({'pid': pid, 'server': server}))
    
    @classmethod
    def load(cls):
        if cls.STATE_FILE.exists():
            return json.loads(cls.STATE_FILE.read_text())
        return None
    
    @classmethod
    def clear(cls):
        if cls.STATE_FILE.exists():
            cls.STATE_FILE.unlink()
    
    @classmethod
    def is_process_running(cls, pid):
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


class VPNCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='VPN CLI Tool')
        self.subparsers = self.parser.add_subparsers(dest='command', required=True)
        
        connect_parser = self.subparsers.add_parser('connect', help='Connect to VPN server')
        connect_parser.add_argument('--server', required=True, help='Server IP address')
        connect_parser.add_argument('--port', type=int, default=8443, help='Server port')
        
        self.subparsers.add_parser('disconnect', help='Disconnect from VPN')
        self.subparsers.add_parser('status', help='Check VPN status')
    
    def connect(self, args):
        state = VPNState.load()
        if state and VPNState.is_process_running(state['pid']):
            print(f"Already connected to {state['server']}")
            return
        
        client_dir = Path(__file__).parent.parent / 'client'
        config_path = client_dir / 'config.json'
        
        config = {
            'server_host': args.server,
            'server_port': args.port
        }
        config_path.write_text(json.dumps(config, indent=2))
        
        client_script = client_dir / 'client.py'
        process = subprocess.Popen(
            [sys.executable, str(client_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        VPNState.save(process.pid, args.server)
        print(f"Connected to VPN server at {args.server}:{args.port}")
        print(f"Process ID: {process.pid}")
    
    def disconnect(self):
        state = VPNState.load()
        if not state:
            print("Not connected to any VPN")
            return
        
        if not VPNState.is_process_running(state['pid']):
            print("VPN process not running")
            VPNState.clear()
            return
        
        try:
            os.kill(state['pid'], signal.SIGTERM)
            print(f"Disconnected from {state['server']}")
            VPNState.clear()
        except ProcessLookupError:
            print("VPN process already terminated")
            VPNState.clear()
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
    def status(self):
        state = VPNState.load()
        if not state:
            print("Status: Disconnected")
            return
        
        if VPNState.is_process_running(state['pid']):
            print(f"Status: Connected")
            print(f"Server: {state['server']}")
            print(f"Process ID: {state['pid']}")
        else:
            print("Status: Disconnected (process terminated)")
            VPNState.clear()
    
    def run(self):
        args = self.parser.parse_args()
        
        if args.command == 'connect':
            self.connect(args)
        elif args.command == 'disconnect':
            self.disconnect()
        elif args.command == 'status':
            self.status()


def main():
    cli = VPNCLI()
    cli.run()


if __name__ == '__main__':
    main()