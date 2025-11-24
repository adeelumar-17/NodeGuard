import subprocess


def enable_nat(interface: str = 'eth0'):
    subprocess.run([
        'iptables', '-t', 'nat', '-A', 'POSTROUTING', 
        '-o', interface, '-j', 'MASQUERADE'
    ], check=True)
    
    subprocess.run([
        'iptables', '-A', 'FORWARD', '-i', 'tun0', 
        '-o', interface, '-j', 'ACCEPT'
    ], check=True)
    
    subprocess.run([
        'iptables', '-A', 'FORWARD', '-i', interface, 
        '-o', 'tun0', '-m', 'state', '--state', 'RELATED,ESTABLISHED', 
        '-j', 'ACCEPT'
    ], check=True)
    
    subprocess.run([
        'sysctl', '-w', 'net.ipv4.ip_forward=1'
    ], check=True, stdout=subprocess.DEVNULL)


def disable_nat(interface: str = 'eth0'):
    subprocess.run([
        'iptables', '-t', 'nat', '-D', 'POSTROUTING', 
        '-o', interface, '-j', 'MASQUERADE'
    ], check=False)
    
    subprocess.run([
        'iptables', '-D', 'FORWARD', '-i', 'tun0', 
        '-o', interface, '-j', 'ACCEPT'
    ], check=False)
    
    subprocess.run([
        'iptables', '-D', 'FORWARD', '-i', interface, 
        '-o', 'tun0', '-m', 'state', '--state', 'RELATED,ESTABLISHED', 
        '-j', 'ACCEPT'
    ], check=False)
    
    subprocess.run([
        'sysctl', '-w', 'net.ipv4.ip_forward=0'
    ], check=False, stdout=subprocess.DEVNULL)