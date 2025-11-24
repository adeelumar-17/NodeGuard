import ssl
from pathlib import Path
from typing import Optional


def get_certificates_dir() -> Path:
    return Path(__file__).parent.parent / 'certificates'


def create_ssl_context(
    cert_file: Optional[str] = None,
    key_file: Optional[str] = None,
    ca_file: Optional[str] = None
) -> ssl.SSLContext:
    certs_dir = get_certificates_dir()
    
    if cert_file is None:
        cert_file = str(certs_dir / 'server.crt')
    if key_file is None:
        key_file = str(certs_dir / 'server.key')
    if ca_file is None:
        ca_file = str(certs_dir / 'ca.crt')
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    context.load_verify_locations(cafile=ca_file)
    
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False
    
    return context


def wrap_socket(
    sock,
    context: Optional[ssl.SSLContext] = None,
    server_side: bool = True
) -> ssl.SSLSocket:
    if context is None:
        context = create_ssl_context()
    
    return context.wrap_socket(sock, server_side=server_side)