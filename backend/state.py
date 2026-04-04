# state.py
class AppState:
    def __init__(self):
        self.connection = None
        self.aes_key = None
        self.mode = None
        self.connected = False
        self.peer_ip = None
        self.fingerprint = None
        self.DEFAULT_PORT = 5000

state = AppState()