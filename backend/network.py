import socket

def start_host(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", port))
    sock.listen()
    print(f"Your IP: {socket.gethostbyname(socket.gethostname())}")
    print(f"Waiting for connection on port {port}...")
    connection, address = sock.accept()
    print(f"Connected to {address[0]}!")
    return connection

def start_client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        print("You have connected!!!")
    except ConnectionRefusedError:
        print("Could not connect — is the host running?")
        sock.close()
        return None
    return sock

def close_connection(sock):
    sock.close()