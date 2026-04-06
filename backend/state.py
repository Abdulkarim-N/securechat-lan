class AppState:
    def __init__(self):
        self.connection = None
        self.aes_key = None
        self.mode = None
        self.connected = False
        self.peer_ip = None
        self.fingerprint = None
        self.handshake_complete = False
        self.handshake_error = None
        self.handshake_started = False
        self.DEFAULT_PORT = 5000

state = AppState()