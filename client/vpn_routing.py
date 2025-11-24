import subprocess


def add_route_default(tun_name: str = 'tun0'):
    subprocess.run([
        'ip', 'route', 'add', '0.0.0.0/0', 'dev', tun_name
    ], check=True)


def remove_route_default(tun_name: str = 'tun0'):
    subprocess.run([
        'ip', 'route', 'del', '0.0.0.0/0', 'dev', tun_name
    ], check=False)