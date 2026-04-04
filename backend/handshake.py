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
    if mode == "host":
        # Step 1 - generate parameters and keys
        private_key, public_key = generate_dh_keys()
        parameters = public_key.parameters()

        # Step 2 - send parameters to client
        send_msg(sock, serialize_parameters(parameters))

        # Step 3 - send our public key
        send_msg(sock, serialize_public_key(public_key))

        # Step 4 + 5 - receive and deserialize client's public key
        peer_public_key_bytes = recv_msg(sock)
        peer_public_key = deserialize_public_key(peer_public_key_bytes)

        # for fingerprinting — both sides hash host's public key
        fp_key_bytes = serialize_public_key(public_key)

    elif mode == "client":
        # Step 1 + 2 - receive and deserialize parameters
        parameters_data = recv_msg(sock)
        parameters = deserialize_parameters(parameters_data)

        # Step 3 - generate our keys from host's parameters
        private_key = parameters.generate_private_key()
        public_key = private_key.public_key()

        # Step 4 + 5 - receive and deserialize host's public key
        peer_public_key_bytes = recv_msg(sock)
        peer_public_key = deserialize_public_key(peer_public_key_bytes)

        # Step 6 - send our public key
        send_msg(sock, serialize_public_key(public_key))

        # for fingerprinting — both sides hash host's public key
        fp_key_bytes = peer_public_key_bytes

    # Both sides do this identically from here
    # Step 7 - derive shared secret
    shared_secret = derive_session_key(private_key, peer_public_key)

    # Step 8 - derive AES key
    aes_key = derive_aes_key(shared_secret)

    # Step 9 - show fingerprint for verification
    fp = fingerprint(fp_key_bytes)
    print(f"\nPeer fingerprint: {fp}")
    print("Verify this matches your peer's fingerprint out of band.")

    # Step 10 - ask for confirmation
    confirm = input("Does the fingerprint match? (y/n): ")
    if confirm.lower() != "y":
        sock.close()
        raise Exception("Fingerprint mismatch - connection terminated")

    print("Handshake complete, session established!")
    return {"aes_key": aes_key, "fingerprint": fp}