from crypto import (
    generate_dh_keys,
    serialize_public_key,
    deserialize_public_key,
    serialize_parameters,
    deserialize_parameters,
    derive_session_key,
    derive_aes_key,
    fingerprint
)
from utils import send_msg, recv_msg

def perform_handshake(sock, mode):
    # sequence goes here (TODO)
    pass