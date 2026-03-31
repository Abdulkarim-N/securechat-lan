from cryptography.hazmat.primitives.asymmetric.dh import generate_parameters
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_der_public_key
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def generate_dh_keys():
    parameters = generate_parameters(generator=2, key_size=2048) #get the parameters to make the keys
    private_key = parameters.generate_private_key() #make the private key
    public_key = private_key.public_key()

    return private_key,public_key
    

def serialize_public_key(public_key):
    data = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    return data

def deserialize_public_key(data):
    public_key = load_der_public_key(data)
    return public_key

def derive_session_key(private_key, peer_public_key):
    shared_secret = private_key.exchange(peer_public_key)
    return shared_secret

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
    from cryptography.hazmat.primitives.asymmetric.dh import DHParameterNumbers
    from cryptography.hazmat.primitives.serialization import load_der_parameters
    return load_der_parameters(data)