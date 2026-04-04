from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
import threading
from network import start_host, start_client
from handshake import perform_handshake
from state import state

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for client connection request
class ConnectRequest(BaseModel):
    ip: str

# ─── Endpoints ───────────────────────────────────────────

@app.get("/status")
def get_status():
    return {
        "connected": state.connected,
        "peer_ip": state.peer_ip,
        "mode": state.mode
    }


@app.post("/connect/host")
def connect_host():
    state.mode = "host"
    ip = socket.gethostbyname(socket.gethostname())
    state.peer_ip = ip
    
    def wait_for_connection():
        state.connection = start_host(state.DEFAULT_PORT)
        state.connected = True
    
    thread = threading.Thread(target=wait_for_connection, daemon=True)
    thread.start()
    
    # return immediately — React polls /status to know when connected
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

@app.post("/handshake")
def handshake():
    result = perform_handshake(state.connection, state.mode)
    state.aes_key = result["aes_key"]
    state.fingerprint = result["fingerprint"]
    return {"fingerprint": state.fingerprint}

@app.post("/verify")
def verify(confirmed: bool):
    if not confirmed:
        state.connection.close()
        return {"status": "rejected"}
    return {"status": "verified"}