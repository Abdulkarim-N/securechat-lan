from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
import threading
import asyncio
import tempfile
import os
from pydantic import BaseModel
from network import start_host, start_client
from handshake import perform_handshake
from state import state

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectRequest(BaseModel):
    ip: str

# ─── Reset ────────────────────────────────────────────────

@app.post("/reset")
def reset():
    if state.connection:
        try:
            state.connection.close()
        except:
            pass
    state.connection = None
    state.aes_key = None
    state.mode = None
    state.connected = False
    state.peer_ip = None
    state.fingerprint = None
    state.handshake_complete = False
    state.handshake_error = None
    state.handshake_started = False
    return {"status": "reset"}

# ─── Status ───────────────────────────────────────────────

@app.get("/status")
def get_status():
    return {
        "connected": state.connected,
        "peer_ip": state.peer_ip,
        "mode": state.mode
    }

# ─── Connection ───────────────────────────────────────────

@app.post("/connect/host")
def connect_host():
    if state.connected or state.connection is not None:
        return {"status": "already_hosting", "ip": state.peer_ip}

    state.mode = "host"
    ip = socket.gethostbyname(socket.gethostname())
    state.peer_ip = ip

    def wait_for_connection():
        state.connection = start_host(state.DEFAULT_PORT)
        state.connected = True

    thread = threading.Thread(target=wait_for_connection, daemon=True)
    thread.start()
    return {"status": "waiting", "ip": ip}

@app.post("/connect/client")
def connect_client(request: ConnectRequest):
    if not request.ip or request.ip.strip() == "":
        return {"status": "failed", "reason": "No IP provided"}

    state.mode = "client"
    state.connection = start_client(request.ip, state.DEFAULT_PORT)
    if state.connection is None:
        return {"status": "failed", "reason": "Could not connect"}

    state.connected = True
    state.peer_ip = request.ip
    return {"status": "connected"}

# ─── Handshake ────────────────────────────────────────────

@app.post("/handshake")
def handshake():
    if not state.connection:
        return {"error": "not connected"}
    if state.handshake_complete:
        return {"fingerprint": state.fingerprint}
    if state.handshake_started:
        return {"status": "already_started"}

    state.handshake_started = True

    def do_handshake():
        try:
            import time
            time.sleep(1)
            r = perform_handshake(state.connection, state.mode)
            state.aes_key = r["aes_key"]
            state.fingerprint = r["fingerprint"]
            state.handshake_complete = True
            state.handshake_error = None
        except Exception as e:
            state.handshake_error = str(e)
            state.handshake_started = False

    thread = threading.Thread(target=do_handshake, daemon=True)
    thread.start()
    return {"status": "handshake_started"}

@app.get("/handshake/status")
def handshake_status():
    if state.handshake_error:
        return {"status": "error", "error": state.handshake_error}
    if state.handshake_complete:
        return {"status": "complete", "fingerprint": state.fingerprint}
    return {"status": "pending"}

class VerifyRequest(BaseModel):
    confirmed: bool

@app.post("/verify")
def verify(request: VerifyRequest):
    if not request.confirmed:
        if state.connection:
            state.connection.close()
        return {"status": "rejected"}
    return {"status": "verified"}

# ─── WebSocket Chat ───────────────────────────────────────
@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()

    # wait for aes_key to be available
    if not state.aes_key:
        await websocket.close()
        return

    loop = asyncio.get_event_loop()

    def receive_thread():
        while True:
            try:
                from utils import recv_msg
                from crypto import decrypt
                if not state.connection or not state.aes_key:
                    print("Receive thread: no connection or key")
                    break
                data = recv_msg(state.connection)
                message = decrypt(state.aes_key, data)
                msg_type = message[:1]
                content = message[1:]
                if msg_type == b"M":
                    asyncio.run_coroutine_threadsafe(
                        websocket.send_text(content.decode()),
                        loop
                    )
            except Exception as e:
                print(f"Receive thread error: {type(e).__name__}: {e}")
                break

    thread = threading.Thread(target=receive_thread, daemon=True)
    thread.start()

    try:
        while True:
            text = await websocket.receive_text()
            from crypto import encrypt
            from utils import send_msg
            if not state.aes_key or not state.connection:
                break
            encrypted = encrypt(state.aes_key, b"M" + text.encode())
            send_msg(state.connection, encrypted)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket send error: {type(e).__name__}: {e}")
# ─── File Transfer ────────────────────────────────────────

@app.post("/send/file")
async def send_file_endpoint(file: UploadFile = File(...)):
    from file_transfer import send_file
    import os
    import tempfile

    # get file extension properly
    _, ext = os.path.splitext(file.filename)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        send_file(state.connection, state.aes_key, tmp_path)
        return {"status": "sent", "filename": file.filename}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
    finally:
        os.unlink(tmp_path)

# ─── Disconnect ───────────────────────────────────────────

@app.post("/disconnect")
def disconnect():
    if state.connection:
        try:
            state.connection.close()
        except:
            pass
    state.connection = None
    state.aes_key = None
    state.mode = None
    state.connected = False
    state.peer_ip = None
    state.fingerprint = None
    state.handshake_complete = False
    state.handshake_error = None
    state.handshake_started = False
    return {"status": "disconnected"}