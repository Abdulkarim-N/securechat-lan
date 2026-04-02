import struct

def send_msg(sock, data):
    length = len(data)
    header = struct.pack(">I", length)
    sock.sendall(header)
    sock.sendall(data)

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if chunk == b"":
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data

def recv_msg(sock):
    header = recv_exact(sock, 4)
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)