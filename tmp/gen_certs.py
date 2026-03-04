from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os

# Generate key
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Generate cert
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Sentinel"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Intelligence"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Sentinel-OS"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName("localhost")]),
    critical=False,
).sign(key, hashes.SHA256())

# Ensure paths exist
backend_dir = r"d:\Projects\Sentinel\repo\Sentinel-POC\backend"
os.makedirs(backend_dir, exist_ok=True)

# Write files
with open(os.path.join(backend_dir, "key.pem"), "wb") as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))

with open(os.path.join(backend_dir, "cert.pem"), "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Certificates generated successfully.")
