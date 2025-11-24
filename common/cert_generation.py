from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime
import ipaddress
from pathlib import Path
from typing import Dict, Tuple


def generate_private_key(key_size: int = 4096) -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )


def generate_ca_certificate(
    private_key: rsa.RSAPrivateKey,
    common_name: str = "VPN CA",
    validity_days: int = 3650
) -> x509.Certificate:
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VPN Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    ).add_extension(
        x509.BasicConstraints(ca=True, path_length=0),
        critical=True,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
            key_encipherment=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    return cert


def generate_server_certificate(
    private_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    common_name: str = "VPN Server",
    dns_names: list = None,
    validity_days: int = 825
) -> x509.Certificate:
    if dns_names is None:
        dns_names = ["localhost", "127.0.0.1"]
    
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VPN Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    san_list = []
    for name in dns_names:
        try:
            parts = name.split('.')
            if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                san_list.append(x509.IPAddress(ipaddress.ip_address(name)))
            else:
                san_list.append(x509.DNSName(name))
        except:
            san_list.append(x509.DNSName(name))
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    ).add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=False,
    ).add_extension(
        x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
        critical=False,
    ).add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
        critical=False,
    ).sign(ca_key, hashes.SHA256(), default_backend())
    
    return cert


def generate_client_certificate(
    private_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    common_name: str = "VPN Client",
    validity_days: int = 825
) -> x509.Certificate:
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VPN Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
    ).add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
        ]),
        critical=False,
    ).add_extension(
        x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
        critical=False,
    ).add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
        critical=False,
    ).sign(ca_key, hashes.SHA256(), default_backend())
    
    return cert


def save_private_key(key: rsa.RSAPrivateKey, path: Path):
    with open(path, 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    path.chmod(0o600)


def save_certificate(cert: x509.Certificate, path: Path):
    with open(path, 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def generate_certificates(
    output_dir: str = None,
    ca_common_name: str = "VPN CA",
    server_common_name: str = "VPN Server",
    client_common_name: str = "VPN Client",
    server_dns_names: list = None
) -> Dict[str, str]:
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'certificates'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ca_key = generate_private_key()
    ca_cert = generate_ca_certificate(ca_key, ca_common_name)
    
    server_key = generate_private_key()
    server_cert = generate_server_certificate(
        server_key, ca_cert, ca_key, server_common_name, server_dns_names
    )
    
    client_key = generate_private_key()
    client_cert = generate_client_certificate(
        client_key, ca_cert, ca_key, client_common_name
    )
    
    paths = {
        'ca_cert': str(output_dir / 'ca.crt'),
        'ca_key': str(output_dir / 'ca.key'),
        'server_cert': str(output_dir / 'server.crt'),
        'server_key': str(output_dir / 'server.key'),
        'client_cert': str(output_dir / 'client.crt'),
        'client_key': str(output_dir / 'client.key'),
    }
    
    save_private_key(ca_key, Path(paths['ca_key']))
    save_certificate(ca_cert, Path(paths['ca_cert']))
    save_private_key(server_key, Path(paths['server_key']))
    save_certificate(server_cert, Path(paths['server_cert']))
    save_private_key(client_key, Path(paths['client_key']))
    save_certificate(client_cert, Path(paths['client_cert']))
    
    return paths