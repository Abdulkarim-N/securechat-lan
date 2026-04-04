from cryptography.hazmat.primitives.asymmetric.dh import generate_parameters
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    ParameterFormat,
    load_der_public_key,
    load_der_parameters
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def generate_dh_keys(): #generates the keys
    parameters = generate_parameters(generator=2, key_size=2048)
    private_key = parameters.generate_private_key()
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_public_key(public_key):
    return public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

def deserialize_public_key(data):
    return load_der_public_key(data)

def derive_session_key(private_key, peer_public_key):
    return private_key.exchange(peer_public_key)

def derive_aes_key(shared_secret):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b""
    )
    return hkdf.derive(shared_secret)

def fingerprint(public_key_bytes):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(public_key_bytes)
    return digest.finalize().hex()

def serialize_parameters(parameters):
    return parameters.parameter_bytes(Encoding.DER, ParameterFormat.PKCS3)

def deserialize_parameters(data):
    return load_der_parameters(data)

def encrypt(aes_key, plaintext):
    nonce = os.urandom(16)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext

def decrypt(aes_key, data):
    nonce = data[:16]
    ciphertext = data[16:]
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ciphertext, None)