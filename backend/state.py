# state.py
DEFAULT_PORT = 5000

class AppState:
    def __init__(self):
        self.connection = None
        self.aes_key = None
        self.mode = None
        self.connected = False
        self.peer_ip = None
        self.fingerprint = None

state = AppState()