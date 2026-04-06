# SecureChat LAN

A serverless, peer-to-peer encrypted messaging application designed for local area networks. SecureChat LAN eliminates centralized infrastructure entirely — no servers, no message storage, no third parties. All communication happens directly between two peers with end-to-end encryption over raw TCP sockets, with a browser-based UI served by a local FastAPI backend.

Built as a final project for **SOFE4840U (Computer Security)** at Ontario Tech University.

---

## Why This Exists

Most messaging platforms route messages through centralized servers. Even with end-to-end encryption, metadata (who you talk to, when, and how often) still flows through corporate infrastructure. Those servers also represent a single point of failure — if compromised, all users are affected.

In local network environments (offices, labs, air-gapped systems), a lightweight secure communication tool that requires no internet and no external server simply doesn't exist in an accessible form. SecureChat LAN fills that gap.

---

## Architecture Overview

SecureChat LAN has two layers:

- **Cryptographic peer-to-peer layer** — two devices connected directly via raw TCP sockets, with all data encrypted before leaving the device
- **Local API layer** — a FastAPI server running on each device that bridges the browser frontend to the socket layer, exposing REST endpoints and a WebSocket channel

```
┌─────────────────────────────────────────────────────┐
│                     Device A                        │
│  ┌──────────────┐       ┌────────────────────────┐  │
│  │ React (5173) │ ◄───► │ FastAPI Backend (8000) │  │
│  └──────────────┘  WS + │ network / crypto /     │  │
│                   REST  │ handshake / messaging   │  │
│                         └──────────┬───────────────┘ │
│                                    │  TCP Socket      │
└────────────────────────────────────┼────────────────-┘
                                     │  AES-256-GCM
                                     │  Encrypted
─────────────────────────────────────┼────────────────
┌────────────────────────────────────┼────────────────┐
│                         Device B   │                 │
│                         └──────────┴───────────────┐ │
│  ┌──────────────┐       │ FastAPI Backend (8001) │  │
│  │ React (5174) │ ◄───► │ network / crypto /     │  │
│  └──────────────┘  WS + │ handshake / messaging   │  │
│                   REST  └────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Connection Establishment

One peer acts as the **host** (binds a TCP socket on port 5000, waits for incoming connections). The other is the **client** (connects to the host's local IP). This asymmetry only exists during setup — once established, communication is symmetric.

The host's IP is displayed in the UI. The user shares it with their peer out-of-band (verbally, via another channel, etc.).

### 2. Cryptographic Handshake

Before any messages are exchanged, both peers perform a Diffie-Hellman key exchange:

```
HOST                                              CLIENT
────                                              ──────
Generate DH parameters (2048-bit prime, generator)
Generate DH key pair (private + public)

Send DH parameters        ──────────────────►    Receive parameters
Send host public key (DER) ─────────────────►    Receive host public key
                                                  Generate DH key pair from parameters
Receive client public key  ◄──────────────────   Send client public key (DER)

Both independently compute:
  shared_secret = DH(my_private_key, peer_public_key)
  aes_key       = HKDF-SHA256(shared_secret) → 32 bytes

Both display: SHA-256 fingerprint of host's public key
User verifies fingerprints match out of band → no MITM
```

**The shared secret is never transmitted.** Each peer derives it independently using their own private key and the other's public key. The DH property guarantees both arrive at the same value.

The session AES key is derived from the shared secret via HKDF with SHA-256 — a standard key derivation function that stretches the DH output into a clean 256-bit symmetric key.

### 3. Fingerprint Verification

Both peers display the SHA-256 hash of the host's public key as a 64-character hex string. Users compare these values out-of-band (read them aloud, compare on screen). Identical fingerprints confirm no Man-in-the-Middle is intercepting the exchange.

### 4. Encrypted Messaging

Every message is encrypted with AES-256-GCM before leaving the device:

```
Plaintext message "Hello"
  └─► Format: b"M" + b"Hello"
  └─► Generate 16-byte random nonce
  └─► AES-256-GCM encrypt with session key
  └─► Output: [nonce (16B)] + [ciphertext] + [GCM auth tag (16B)]
  └─► Length-prefix framed → sent over TCP socket
```

- **AES-256**: 256-bit key, currently considered computationally infeasible to brute force
- **GCM mode**: Authenticated encryption — any tampering with ciphertext causes decryption to fail automatically, preventing forgery
- **Unique nonce per message**: Prevents nonce reuse attacks and ciphertext replay
- **No plaintext ever sent**: Even during the handshake, only public keys and DH parameters travel over the wire

### 5. Encrypted File Transfer

Files are broken into **4KB chunks**, each independently encrypted with AES-256-GCM:

```
[Encrypted Header]   → b"F" + "filename|chunk_count"
[Encrypted Chunk 0]  → b"C" + chunk_number (4B big-endian) + chunk_data
[Encrypted Chunk 1]  → ...
[Encrypted End]      → b"E" + filename
```

The receiver stores chunks in a dictionary keyed by chunk number and reassembles them in order after all arrive. Even the filename is encrypted — nothing about the transfer is visible in plaintext on the network.

### 6. Message Framing

TCP provides a raw byte stream with no concept of message boundaries. Every send/receive goes through a **length-prefixed framing** layer:

```
┌──────────────┬──────────────────────────┐
│ Length (4B)  │ Message (Length bytes)   │
│ big-endian   │ encrypted ciphertext     │
└──────────────┴──────────────────────────┘
```

This ensures messages are never split or merged, regardless of TCP segmentation.

---

## Security Properties

| Threat | Mitigation | Strength |
|---|---|---|
| Eavesdropping | AES-256-GCM encryption on all traffic | Strong |
| Man-in-the-Middle | SHA-256 fingerprint out-of-band verification | Strong (if verified) |
| Key Interception | DH exchange — shared secret never transmitted | Strong |
| Message Tampering | GCM authentication tag — fails on any modification | Strong |
| Replay Attacks | Unique random 16-byte nonce per message | Strong |
| Plaintext Leakage | No plaintext sent at any point post-connection | Strong |
| Single Point of Failure | No central server — direct peer-to-peer only | Strong |

### Known Limitations

- **No Perfect Forward Secrecy (PFS)**: A single session key is used for the entire session. If the key is later compromised, all past messages in that session are decryptable. Mitigation would require ephemeral key renegotiation.
- **Traffic analysis**: Packet timing and sizes are not obfuscated. An observer cannot read content, but can infer communication patterns.
- **MITM if fingerprint skipped**: If users do not verify fingerprints, a MITM attack is feasible during the handshake.
- **LAN-only**: No NAT traversal or internet routing. The application is scoped to devices on the same local network.
- **No group messaging**: One-to-one connections only.

---

## Tech Stack

| Layer | Technology | Details |
|---|---|---|
| Backend language | Python 3.12 | — |
| Web framework | FastAPI 0.135 | ASGI, REST + WebSocket |
| ASGI server | Uvicorn 0.43 | Development server |
| Networking | Python `socket` | Raw TCP, port 5000 |
| Cryptography library | `cryptography` 46.0 | Hazmat primitives |
| Key exchange | Diffie-Hellman | 2048-bit parameters |
| Key derivation | HKDF-SHA256 | 32-byte AES key output |
| Symmetric encryption | AES-256-GCM | Authenticated encryption |
| Fingerprinting | SHA-256 | 64-char hex digest |
| Concurrency | Python `threading` | Daemon threads per connection |
| Frontend framework | React 19 | — |
| Build tool | Vite 8 | — |
| HTTP client | Axios 1.14 | REST calls to FastAPI |
| API transport | REST + WebSocket | REST for setup, WS for chat |

---

## Project Structure

```
securechat-lan/
├── start_instance1.py          # Launches backend (port 8000) + frontend (port 5173)
├── start_instance2.py          # Launches backend (port 8001) + frontend (port 5174)
├── start_dev.bat               # Windows: launches all 4 processes
├── reset_test.bat              # Windows: resets both instances
│
├── backend/
│   ├── main.py                 # FastAPI server — REST endpoints + WebSocket
│   ├── state.py                # Global app state (socket, AES key, mode, flags)
│   ├── network.py              # TCP socket: start_host(), start_client()
│   ├── crypto.py               # All crypto: DH, AES-GCM, HKDF, SHA-256
│   ├── handshake.py            # Handshake protocol orchestration
│   ├── messaging.py            # Threaded send/receive chat loop (CLI mode)
│   ├── file_transfer.py        # Encrypted 4KB chunked file send/receive
│   ├── utils.py                # Length-prefixed message framing
│   ├── requirements.txt        # Python dependencies
│   └── received_files/         # Incoming files saved here
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── .env                    # Instance 1: API=8000, port=5173
    ├── .env.instance2          # Instance 2: API=8001, port=5174
    └── src/
        ├── App.jsx             # State machine — routes between 4 screens
        ├── config.js           # API_URL and WS_URL from env vars
        └── components/
            ├── ConnectionScreen.jsx    # Host/client role selection + IP entry
            ├── WaitingScreen.jsx       # Host waits; polls /status every 2s
            ├── FingerprintScreen.jsx   # Handshake + fingerprint display + confirm
            └── ChatScreen.jsx          # Chat UI, file upload, WebSocket connection
```

### Module Responsibilities

**`utils.py`** — Foundation for all network I/O. Implements length-prefixed framing so TCP's byte stream is split into discrete messages. Every send and receive in the project goes through `send_msg` / `recv_msg`.

**`network.py`** — Pure TCP connection layer. `start_host` binds and accepts. `start_client` connects. Returns a connected socket. No encryption awareness.

**`crypto.py`** — All cryptographic operations in isolation. DH key generation, serialization (DER), shared secret derivation, HKDF key derivation, AES-256-GCM encrypt/decrypt, SHA-256 fingerprinting. Nothing else in the project performs crypto.

**`handshake.py`** — Orchestrates the DH key exchange sequence (host or client path) using `crypto.py` and `utils.py` in the correct order to avoid deadlocks. Writes the derived AES key and fingerprint to global state on completion.

**`state.py`** — Single global `AppState` instance shared across all FastAPI endpoints and background threads. Holds the active socket, AES key, peer IP, connection flags, and handshake status.

**`main.py`** — FastAPI application. Exposes REST endpoints for connection setup, handshake management, and file transfer. Exposes a WebSocket endpoint `/ws/chat` for real-time bidirectional encrypted messaging. All heavy work is done in daemon threads to keep the event loop non-blocking.

**`file_transfer.py`** — Chunks files into 4KB blocks, prepends a chunk index, encrypts each block with the session AES key, and sends them. On receive, decrypts and buffers chunks by index, then reassembles in order.

**`messaging.py`** — Legacy CLI chat loop (two concurrent threads: send from stdin, receive from socket). Used for terminal-mode testing; not active in the frontend flow.

---

## UI Flow

The React frontend is a four-screen state machine:

```
ConnectionScreen
  │
  ├─ "Start Hosting"  ──► POST /connect/host ──► WaitingScreen
  │                                                     │
  │                                                     │ polls GET /status every 2s
  │                                                     │ until connected: true
  │                                                     ▼
  └─ "Connect to Peer" (enter IP) ──► POST /connect/client ──► FingerprintScreen
                                                               │
                                                               │ POST /handshake
                                                               │ polls GET /handshake/status every 2s
                                                               │ displays SHA-256 fingerprint
                                                               │ user confirms match
                                                               │ POST /verify
                                                               ▼
                                                           ChatScreen
                                                               │
                                                               │ WS /ws/chat
                                                               │ text messages + file upload
                                                               │ POST /send/file
                                                               │
                                                               └─ Disconnect ──► ConnectionScreen
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/connect/host` | Start listening for a peer connection. Returns local IP. |
| `POST` | `/connect/client` | Connect to peer at `{"ip": "..."}`. |
| `POST` | `/handshake` | Start the DH key exchange in a background thread. |
| `GET` | `/handshake/status` | Returns `{status, fingerprint}` — poll until `"complete"`. |
| `POST` | `/verify` | Confirm fingerprint match `{"confirmed": true/false}`. |
| `GET` | `/status` | Returns `{connected, peer_ip, mode}`. |
| `POST` | `/send/file` | Upload file (multipart). Backend chunks, encrypts, and sends. |
| `POST` | `/disconnect` | Clean disconnect — closes socket, resets state. |
| `POST` | `/reset` | Full state reset (testing). |
| `WS` | `/ws/chat` | Bidirectional encrypted chat stream. |

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip + npm

### Setup

```bash
git clone https://github.com/Abdulkarim-N/securechat-lan.git
cd securechat-lan

# Python environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

pip install -r backend/requirements.txt

# Node dependencies
cd frontend
npm install
cd ..
```

---

## Running

### On a Single Machine (Testing Both Instances)

```bash
# Terminal 1
python start_instance1.py
# Starts: Backend on port 8000, Frontend on port 5173

# Terminal 2
python start_instance2.py
# Starts: Backend on port 8001, Frontend on port 5174
```

Open **http://localhost:5173** and **http://localhost:5174** in two browser tabs.

### On Two Separate Machines (Real LAN Use)

On each machine, run only one instance:

```bash
# Machine A
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
cd frontend && npm run dev -- --host

# Machine B
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
cd frontend && npm run dev -- --host
```

### Windows

```bat
start_dev.bat        :: Launches all 4 processes (2 backends, 2 frontends)
reset_test.bat       :: Resets state on both instances
```

---

## Typical Session

1. Open **Instance 1** in browser → click **Start Hosting** → your IP is displayed
2. Open **Instance 2** in browser → enter Instance 1's IP → click **Connect to Peer**
3. Both browsers advance to the **Fingerprint Verification** screen
4. Both show a 64-character SHA-256 fingerprint — compare them (read aloud or side-by-side)
5. Both click **Confirm** — if either denies, the connection closes
6. **Chat begins** — type messages, or use the attachment button to send a file
7. Click **Disconnect** to end the session cleanly

---

## Acknowledgements

Built for SOFE4840U — Computer Security, Ontario Tech University.

Cryptographic primitives provided by the [Python `cryptography` library](https://cryptography.io/) (Hazmat layer). DH parameters follow RFC 3526 (2048-bit MODP group).
