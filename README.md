# SecureChat LAN

A serverless peer-to-peer encrypted messaging system that operates exclusively
over a local area network (LAN). SecureChat LAN eliminates centralized 
infrastructure entirely — no servers, no message storage, no third parties. 
All communication happens directly between two peers with end-to-end encryption.

Built as a final project for SOFE4840U (Computer Security) at Ontario Tech University.

---

## Why This Exists

Most messaging platforms rely on centralized servers to route and sometimes 
store messages. Even with end-to-end encryption, metadata still flows through 
corporate infrastructure — who you talk to, when, and how often is visible to 
the platform. These servers also represent a single point of failure: if 
compromised, every user is affected.

In local network environments (offices, labs, air-gapped systems), a 
lightweight secure communication tool that requires no internet and no server 
simply doesn't exist in an accessible form. SecureChat LAN fills that gap.

---

## How It Works

### Connection
One peer acts as the host (listens for incoming connections) and the other 
connects to them using their local IP address. This asymmetry only exists at 
connection time — once established, both peers are equal. All communication 
is direct, peer-to-peer.

### Handshake
Before any messages are exchanged, both peers perform a cryptographic 
handshake:

1. The host generates Diffie-Hellman (DH) parameters and sends them to the client
2. Both peers independently generate their own DH key pairs
3. They exchange only their public keys — private keys never leave the device
4. Each peer combines their private key with the other's public key to compute 
   an identical shared secret — without ever transmitting it
5. The shared secret is passed through HKDF (Hash-based Key Derivation Function)
   to produce a clean 256-bit AES session key
6. Both peers display a SHA-256 fingerprint of the host's public key for 
   out-of-band verification — if the fingerprints match, no Man-in-the-Middle 
   attack is occurring

### Encrypted Messaging
All messages are encrypted using AES-256-GCM before leaving the device:
- AES-256 provides confidentiality — messages are unreadable without the key
- GCM mode provides integrity — any tampering with the ciphertext causes 
  decryption to fail automatically
- A unique random nonce is generated for every single message, preventing 
  nonce reuse attacks
- Messages travel as ciphertext only — no plaintext ever hits the network

### File Transfer
Files are broken into 4KB chunks, each chunk individually encrypted with 
AES-256-GCM and sent with a chunk number for ordered reassembly. The receiver 
decrypts and reassembles in the correct order and writes the file to disk.
The file header (filename and chunk count) is also encrypted — nothing 
about the transfer is visible in plaintext.

### Session Teardown
Either peer can type `/quit` to end the session. A quit signal is sent to the 
peer, both sides stop their send/receive threads, the session key is discarded, 
and the socket is closed cleanly.

---

## Security Properties

| Threat | Mitigation |
|---|---|
| Eavesdropping | All traffic encrypted with AES-256-GCM after handshake |
| Man-in-the-Middle | SHA-256 public key fingerprint for out-of-band verification |
| Replay Attacks | Unique random nonce per message prevents replay |
| Key Interception | DH key exchange — shared secret never transmitted |
| Plaintext Leakage | No plaintext sent at any point after connection |
| Single Point of Failure | No central server — direct peer-to-peer only |

### Known Limitations
- Does not implement Perfect Forward Secrecy (PFS)
- Provides limited protection against traffic analysis (timing, packet size)
- Vulnerable to MITM if fingerprint verification is skipped
- Does not support NAT traversal or internet routing
- No group messaging support

---

## Project Structure
```
securechat-lan/
├── main.py           # Entry point — establishes connection and starts chat
├── network.py        # TCP socket setup, host/client connection handling
├── crypto.py         # All cryptography: DH, AES-GCM, HKDF, SHA-256
├── handshake.py      # Handshake protocol orchestration
├── messaging.py      # Threaded send/receive chat loop
├── file_transfer.py  # Encrypted chunked file send/receive
└── utils.py          # Message framing (length-prefixed send/recv)
```

### Module Responsibilities

**`utils.py`** — The foundation everything else builds on. Implements 
length-prefixed message framing so TCP's raw byte stream is broken into 
discrete messages correctly. Every send and receive in the project goes 
through `send_msg` and `recv_msg`.

**`network.py`** — Handles only the raw TCP connection. `start_host` binds 
to a port and waits. `start_client` connects to an IP. Returns a connected 
socket. Knows nothing about encryption.

**`crypto.py`** — Contains every cryptographic operation in isolation. DH 
key generation, serialization, session key derivation via HKDF, AES-256-GCM 
encrypt/decrypt, and SHA-256 fingerprinting. Nothing else in the project 
performs crypto operations.

**`handshake.py`** — Orchestrates the handshake sequence, calling `crypto.py` 
and `utils.py` in the correct order to prevent deadlocks. Returns a derived 
AES session key on success, terminates the connection on fingerprint mismatch.

**`messaging.py`** — Runs two concurrent threads: a send loop reading user 
input and a receive loop listening for incoming data. A shared `stop_event` 
flag coordinates clean shutdown between threads when either side quits or 
the connection drops.

**`file_transfer.py`** — Sends files as encrypted 4KB chunks with ordered 
chunk numbers. Receiver stores chunks in a dictionary keyed by chunk number 
and reassembles in order after all chunks arrive.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Networking | Python `socket` module (TCP) |
| Cryptography | `cryptography` library (Hazmat primitives) |
| Key Exchange | Diffie-Hellman (2048-bit) |
| Key Derivation | HKDF with SHA-256 |
| Symmetric Encryption | AES-256-GCM |
| Fingerprinting | SHA-256 |
| Concurrency | Python `threading` |
| Backend API | FastAPI |
| Frontend | React.js |
| API Transport | REST + WebSocket |

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)

### Backend Setup
```bash
git clone https://github.com/Abdulkarim-N/securechat-lan.git
cd securechat-lan
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### Running (Terminal Mode)
Open two terminals, both with the venv activated.

**Terminal 1 (Host):**
```bash
python main.py
# Input: 1
# Your IP will be displayed — share it with the peer
```

**Terminal 2 (Client):**
```bash
python main.py
# Input: 2
# Enter the host's IP address
```

Both peers complete fingerprint verification, then chat begins.

### Commands
```
/sendfile <path>    Send an encrypted file to your peer
/quit               End the session securely
```

---

## Cryptographic Flow Diagram
```
HOST                                          CLIENT
────                                          ──────
Generate DH parameters + key pair
Send parameters ─────────────────────────►  Receive parameters
Send public key  ─────────────────────────►  Receive host public key
                                             Generate key pair from parameters
Receive client public key  ◄─────────────── Send public key

Both independently compute:
shared_secret = DH(my_private, peer_public)
aes_key = HKDF(shared_secret, SHA-256, 32 bytes)

Display SHA-256 fingerprint of host public key
User verifies fingerprint matches out of band
                    ◄── Encrypted chat begins ──►
```

---

## Acknowledgements
Built for SOFE4840U Computer Security — Ontario Tech University, Winter 2026.